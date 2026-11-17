"""
HAMIOS v5 — CAT radio-interface (conform FT-950 CAT Operation Reference Book)

Frequentie-digit-aantallen per radiotype:
  • Yaesu FT-950/2000/DX series → FA<8 cijfers>;   bijv. FA14250000;  (= 14.250 MHz)
      Paginanummer 2 handleiding: "FA14250000;" (Set command voorbeeld)
      Parameter P1 bereik: 0030000 – 56000000 (Hz), 8 cijfers
  • Yaesu FT-991/710/DX10/DX101 → FA<9 cijfers>;  bijv. FA014250000;
  • Yaesu FT-817/857/897 → binair 5-byte-commando (4 BCD-bytes + opcode), 10 Hz-eenheid
  • Kenwood / Elecraft (TS-590 e.d.) → FA<11 cijfers>;  modus: MD<n>;
  • Icom CI-V → binary BCD frame (frequentie 05/03, modus 06)

VS-commando (FT-950 p.17):
  VS0; = selecteer VFO-A (sturen vóór FA voor zekerheid)
  VS1; = selecteer VFO-B

ID-commando (FT-950 p.9):
  ID; → antwoord ID0310; (vaste waarde, bruikbaar voor verbindingstest)

IF-commando (FT-950 p.10):
  IF; → alles-in-één status: IF[3-mem][8-freq][+/-][4-clar][rx-clar][tx-clar][mode]...;
  Frequentie staat op positie 3-10 (0-indexed: bytes 2..9) = 8 ASCII-digits.
"""

import threading

from .i18n import tr

_serial_available = False
try:
    import serial
    _serial_available = True
except ImportError:
    pass


class CatInterface:
    """Enkelvoudige CAT-verbinding met een radio."""

    RADIO_TYPES = [
        "Yaesu (FT-950/2000/DX/3000/5000)",
        "Yaesu (FT-991/710/DX10/DX101)",
        "Yaesu (FT-817/857/897)",
        "Kenwood / Elecraft",
        "Icom CI-V",
        "Hamlib rigctld (TCP)",
        "flrig (XML-RPC)",
    ]

    _POLL_INTERVAL = 2.0   # seconden tussen frequentie-peilingen

    def _kind(self) -> str:
        """Protocolfamilie van het ingestelde radiotype."""
        rtype = getattr(self._cfg, "cat_radio_type", "") or ""
        if "rigctld" in rtype:
            return "rigctld"
        if "flrig" in rtype:
            return "flrig"
        if "Icom" in rtype:
            return "icom"
        if "Kenwood" in rtype or "Elecraft" in rtype:
            return "kenwood"
        if "817" in rtype or "857" in rtype or "897" in rtype:
            return "ft817"
        if "991" in rtype or "710" in rtype or "DX10" in rtype:
            return "yaesu9"
        return "yaesu8"

    def __init__(self, cfg=None):
        self._cfg          = cfg
        self._serial       = None
        self._net          = None    # rig_net.NetRig bij rigctld / flrig
        self._lock         = threading.Lock()
        self._log_callback  = None   # callable(direction, data)
        self._freq_callback = None   # callable(freq_hz: int | None)
        self._polling       = False
        self._poll_thread   = None

    # ── Interne logging ───────────────────────────────────────────────────────

    def _log(self, direction: str, data):
        cb = self._log_callback
        if cb:
            try:
                cb(direction, data)
            except Exception:
                pass

    # ── Verbinding ────────────────────────────────────────────────────────────

    def connect(self) -> tuple[bool, str]:
        if self._kind() in ("rigctld", "flrig"):
            return self._connect_net()
        if not _serial_available:
            return False, tr("cat.err.no_pyserial")

        cfg = self._cfg
        if cfg is None:
            return False, tr("cat.err.no_cfg")
        port = getattr(cfg, "cat_port", "").strip()
        if not port:
            return False, tr("cat.err.no_port")

        try:
            with self._lock:
                if self._serial:
                    try:
                        self._serial.close()
                    except Exception:
                        pass
                    self._serial = None

                parity_map = {
                    "Geen": serial.PARITY_NONE,
                    "Even": serial.PARITY_EVEN,
                    "Odd":  serial.PARITY_ODD,
                }
                stop_map = {"1": serial.STOPBITS_ONE, "2": serial.STOPBITS_TWO}

                parity   = parity_map.get(getattr(cfg, "cat_parity",   "Geen"),
                                          serial.PARITY_NONE)
                stopbits = stop_map.get(str(getattr(cfg, "cat_stopbits", "1")),
                                        serial.STOPBITS_ONE)
                databits = int(getattr(cfg, "cat_databits", 8))

                self._serial = serial.Serial(
                    port     = port,
                    baudrate = int(getattr(cfg, "cat_baud", 9600)),
                    bytesize = databits,
                    parity   = parity,
                    stopbits = stopbits,
                    timeout  = 0.5,
                    rtscts   = bool(getattr(cfg, "cat_rtscts", False)),
                    dsrdtr   = bool(getattr(cfg, "cat_dsrdtr", False)),
                )
                self._serial.dtr = bool(getattr(cfg, "cat_dtr", False))
                self._serial.rts = bool(getattr(cfg, "cat_rts", False))

            self._log("INFO", tr("cat.log.connected", port=port,
                                 baud=getattr(cfg, 'cat_baud', 9600),
                                 radio=getattr(cfg, 'cat_radio_type', '?')))
            self._start_polling()
            return True, ""
        except PermissionError:
            self._serial = None
            msg = tr("cat.err.port_busy")
            self._log("ERR", msg)
            return False, msg
        except Exception as e:
            self._serial = None
            self._log("ERR", str(e))
            return False, str(e)

    def _connect_net(self) -> tuple[bool, str]:
        """Hamlib rigctld / flrig: adres uit het poortveld (host:poort)."""
        from .rig_net import NetRig
        cfg = self._cfg
        if cfg is None:
            return False, tr("cat.err.no_cfg")
        kind = self._kind()
        try:
            with self._lock:
                if self._net is not None:
                    self._net.close()
                if self._serial is not None:
                    try:
                        self._serial.close()
                    except Exception:
                        pass
                    self._serial = None
                net = NetRig(kind, getattr(cfg, "cat_port", ""))
                net.open()
                self._net = net
            self._log("INFO", tr("cat.log.connected", port=f"{net.host}:{net.port}",
                                 baud="TCP", radio=getattr(cfg, "cat_radio_type", "?")))
            self._start_polling()
            return True, ""
        except Exception as e:
            self._net = None
            msg = tr("cat.err.net", kind=kind, err=str(e))
            self._log("ERR", msg)
            return False, msg

    def disconnect(self):
        self._stop_polling()
        with self._lock:
            if self._net is not None:
                self._net.close()
                self._net = None
            if self._serial:
                try:
                    self._serial.close()
                except Exception:
                    pass
                self._serial = None
        self._log("INFO", tr("cat.log.disconnected"))
        cb = self._freq_callback
        if cb:
            try:
                cb(None)
            except Exception:
                pass

    # ── Frequentie pollen ─────────────────────────────────────────────────────

    def _start_polling(self):
        self._polling = True
        t = threading.Thread(target=self._poll_loop, daemon=True,
                              name="cat-poll")
        self._poll_thread = t
        t.start()

    def _stop_polling(self):
        self._polling = False

    # Na dit aantal achtereenvolgende lege responsen → radio offline melden
    _OFFLINE_THRESHOLD = 3

    def _poll_loop(self):
        """
        Retourwaarden van _read_freq_hz_raw:
          int > 0  → geldige frequentie van radio
          0        → verbonden maar geen geldige respons (?; of leeg)
          None     → verbindingsfout (exception / poort dicht)

        Als _OFFLINE_THRESHOLD opeenvolgende lege responsen binnenkomen, wordt
        de freq_callback aangeroepen met -1 ('Radio offline') in plaats van 0.
        """
        import time
        no_response_count = 0
        while self._polling and self.connected:
            freq = self._read_freq_hz_raw()
            cb = self._freq_callback
            if freq is None:
                # Poort dicht / exception → echte disconnect
                if cb:
                    try: cb(None)
                    except Exception: pass
                break
            elif freq == 0:
                # Geen bruikbare respons van radio
                no_response_count += 1
                if no_response_count >= self._OFFLINE_THRESHOLD:
                    # Radio reageert niet → meld als offline (-1)
                    if cb:
                        try: cb(-1)
                        except Exception: pass
                else:
                    if cb:
                        try: cb(0)
                        except Exception: pass
            else:
                # Geldige frequentie ontvangen → reset teller
                no_response_count = 0
                if cb:
                    try: cb(freq)
                    except Exception: pass
            time.sleep(self._POLL_INTERVAL)

    def _read_freq_hz_raw(self):
        """
        Geeft:  int > 0  → frequentie in Hz
                0        → verbonden, geen bruikbare FA-respons (probeer IF; als Yaesu)
                None     → verbindingsfout (exception / poort dicht)
        """
        if not self.connected:
            return None
        kind = self._kind()
        try:
            if kind in ("rigctld", "flrig"):
                with self._lock:
                    return self._net.read_freq() if self._net else None
            if kind == "icom":
                result = self._icom_read_freq()
            elif kind == "ft817":
                result = self._ft817_read_freq()
            elif kind == "kenwood":
                result = self._fa_read_freq(digits=11)
            elif kind == "yaesu9":
                result = self._fa_read_freq(digits=9)
            else:
                # Yaesu: probeer eerst FA; (8 cijfers), dan IF; als fallback
                result = self._fa_read_freq(digits=8)
                if result == 0:
                    result = self._if_read_freq()
            return result if result is not None else 0
        except Exception:
            return None

    def _fa_read_freq(self, digits: int = 8):
        """
        Stuur FA; en parseer FA<N digits>;
        Geeft int Hz of 0 terug (nooit None).
        digits=8  → Yaesu FT-950 (conform handleiding p.9)
        digits=11 → Kenwood / Elecraft
        """
        import time
        with self._lock:
            self._serial.reset_input_buffer()
            self._serial.write(b"FA;")
            self._serial.flush()
            time.sleep(0.08)
            buf = b""
            deadline = time.monotonic() + 0.5
            while time.monotonic() < deadline:
                if self._serial.in_waiting:
                    buf += self._serial.read(self._serial.in_waiting)
                    if b";" in buf:
                        break
                time.sleep(0.02)

        if b"?" in buf:
            return 0
        idx = buf.find(b"FA")
        if idx < 0:
            return 0
        chunk = buf[idx:]
        end   = chunk.find(b";")
        if end < 3:
            return 0
        d = chunk[2:end]
        # Accepteer het verwachte aantal cijfers OF elke geldig getal (7-11)
        if d.isdigit() and (len(d) == digits or 7 <= len(d) <= 11):
            return int(d)
        return 0

    def _if_read_freq(self):
        """
        Stuur IF; en parseer de frequentie uit het antwoord.
        FT-950 IF-antwoord: IF[3-mem][8-freq][...]; (conform handleiding p.10)
        Frequentie staat op positie 2..9 (0-indexed) in de payload na 'IF'.
        """
        import time
        with self._lock:
            self._serial.reset_input_buffer()
            self._serial.write(b"IF;")
            self._serial.flush()
            time.sleep(0.10)
            buf = b""
            deadline = time.monotonic() + 0.6
            while time.monotonic() < deadline:
                if self._serial.in_waiting:
                    buf += self._serial.read(self._serial.in_waiting)
                    if b";" in buf:
                        break
                time.sleep(0.02)

        idx = buf.find(b"IF")
        if idx < 0:
            return 0
        payload = buf[idx+2:]          # alles na 'IF'
        end = payload.find(b";")
        if end < 11:
            return 0
        # Sla de 3 geheugenkanaal-bytes over, lees daarna 8 frequentiecijfers
        freq_bytes = payload[3:11]
        if freq_bytes.isdigit():
            return int(freq_bytes)
        return 0

    def _icom_read_freq(self) -> int | None:
        """Icom CI-V: stuur commando 03 (read operating freq) en parseer BCD."""
        import time
        addr = int(getattr(self._cfg, "cat_civ_addr", 0x58))
        cmd  = bytes([0xFE, 0xFE, addr, 0xE0, 0x03, 0xFD])
        with self._lock:
            self._serial.reset_input_buffer()
            self._serial.write(cmd)
            self._serial.flush()
            time.sleep(0.12)
            buf = b""
            deadline = time.monotonic() + 0.5
            freq = None
            # Veel CI-V-interfaces echoën het commando: wacht op het échte
            # antwoord (aan E0) in plaats van te stoppen bij de eerste FD
            while time.monotonic() < deadline:
                if self._serial.in_waiting:
                    buf += self._serial.read(self._serial.in_waiting)
                    freq = self._icom_parse_freq(buf)
                    if freq is not None:
                        break
                time.sleep(0.02)
        return freq

    @staticmethod
    def _icom_parse_freq(buf: bytes) -> int | None:
        """Zoek een antwoordframe FE FE E0 <radio> 03 <5 BCD-bytes> FD (de echo
        van ons eigen commando, FE FE <radio> E0 03 FD, wordt overgeslagen)."""
        for i in range(len(buf) - 10):
            if (buf[i] == 0xFE and buf[i + 1] == 0xFE and buf[i + 2] == 0xE0
                    and buf[i + 4] == 0x03 and buf[i + 10] == 0xFD):
                freq, mul = 0, 1
                for byte in buf[i + 5:i + 10]:
                    lo, hi = byte & 0x0F, (byte >> 4) & 0x0F
                    if lo > 9 or hi > 9:
                        break                    # geen geldige BCD
                    freq += lo * mul
                    mul *= 10
                    freq += hi * mul
                    mul *= 10
                else:
                    return freq
        return None

    # ── Yaesu FT-817/857/897: binair 5-byte-protocol ─────────────────────────
    @staticmethod
    def _bcd_10hz(freq_hz: int) -> list:
        """Frequentie → 4 BCD-bytes in eenheden van 10 Hz (FT-817: 01 42 50 00 = 14,250 MHz)."""
        digits = f"{max(0, int(freq_hz)) // 10:08d}"[-8:]
        return [(int(digits[k]) << 4) | int(digits[k + 1]) for k in range(0, 8, 2)]

    @staticmethod
    def _ft817_parse_freq(buf: bytes) -> int:
        """4 BCD-bytes (10 Hz-eenheden) → Hz, of 0 bij ongeldige data."""
        if len(buf) < 4:
            return 0
        val = 0
        for byte in buf[:4]:
            hi, lo = (byte >> 4) & 0x0F, byte & 0x0F
            if hi > 9 or lo > 9:
                return 0
            val = val * 100 + hi * 10 + lo
        return val * 10

    def _ft817_read_freq(self) -> int:
        """Opcode 03: antwoord = 4 BCD-bytes (10 Hz) + modusbyte."""
        import time
        with self._lock:
            self._serial.reset_input_buffer()
            self._serial.write(bytes([0, 0, 0, 0, 0x03]))
            self._serial.flush()
            buf = b""
            deadline = time.monotonic() + 0.5
            while time.monotonic() < deadline and len(buf) < 5:
                if self._serial.in_waiting:
                    buf += self._serial.read(self._serial.in_waiting)
                time.sleep(0.02)
        return self._ft817_parse_freq(buf) if len(buf) >= 5 else 0

    @property
    def connected(self) -> bool:
        if self._net is not None:
            return self._net.is_open
        return self._serial is not None and self._serial.is_open

    # ── Verbindingstest / identificatie ──────────────────────────────────────

    def identify(self) -> tuple[bool, str]:
        """
        Stuur ID; en lees het antwoord (FT-950 antwoordt ID0310;).
        Geeft (True, "ID0310") of (False, foutmelding) terug.
        """
        if not self.connected:
            ok, err = self.connect()
            if not ok:
                return False, err
        import time
        if self._kind() in ("rigctld", "flrig"):
            try:
                with self._lock:
                    f = self._net.read_freq() if self._net else 0
            except Exception as e:
                return False, str(e)
            return (True, f"{self._kind()} · {f / 1e6:.6f} MHz") if f else \
                (False, tr("cat.err.unexpected", txt="—"))
        if self._kind() in ("icom", "ft817"):
            # Geen ID-commando: test met het uitlezen van de frequentie
            try:
                f = self._icom_read_freq() if self._kind() == "icom" else self._ft817_read_freq()
            except Exception as e:
                return False, str(e)
            if f:
                return True, f"{f / 1e6:.6f} MHz"
            return False, tr("cat.err.unexpected", txt="—")
        try:
            with self._lock:
                self._serial.reset_input_buffer()
                self._serial.write(b"ID;")
                self._serial.flush()
                time.sleep(0.15)
                buf = b""
                deadline = time.monotonic() + 0.5
                while time.monotonic() < deadline:
                    if self._serial.in_waiting:
                        buf += self._serial.read(self._serial.in_waiting)
                        if b";" in buf:
                            break
                    time.sleep(0.02)
            self._log("TX", b"ID;")
            if buf:
                self._log("RX", buf)
            txt = buf.decode("ascii", errors="replace").strip()
            if txt.startswith("ID") and txt.endswith(";"):
                return True, txt[:-1]   # bijv. "ID0310"
            return False, tr("cat.err.unexpected", txt=repr(txt))
        except Exception as e:
            return False, str(e)

    # ── Frequentie instellen ──────────────────────────────────────────────────

    def set_freq_hz(self, freq_hz: int) -> tuple[bool, str]:
        if not self.connected:
            ok, err = self.connect()
            if not ok:
                return False, err

        kind = self._kind()
        if kind in ("rigctld", "flrig"):
            try:
                with self._lock:
                    ok = self._net.set_freq(freq_hz)
                self._log("TX", f"F {freq_hz}".encode())
                if not ok:
                    return False, tr("cat.err.refused", mhz=f"{freq_hz / 1e6:.3f}")
                return True, ""
            except Exception as e:
                self._log("ERR", str(e))
                return False, str(e)
        try:
            if kind == "icom":
                data = self._icom_cmd(freq_hz)
            elif kind == "ft817":
                data = bytes(self._bcd_10hz(freq_hz) + [0x01])
            elif kind == "kenwood":
                data = self._fa_cmd_11(freq_hz)
            elif kind == "yaesu9":
                data = f"FA{freq_hz:09d};".encode("ascii")
            else:
                # Yaesu FT-950/2000/DX/3000/5000 — 8 cijfers (conform handleiding p.2,9)
                data = self._fa_cmd_8(freq_hz)

            with self._lock:
                self._serial.write(data)
                self._serial.flush()
                import time; time.sleep(0.10)
                rx = b""
                while self._serial.in_waiting:
                    rx += self._serial.read(self._serial.in_waiting)
                    time.sleep(0.02)

            self._log("TX", data)
            if rx:
                self._log("RX", rx)
                if b"?" in rx:
                    mhz = freq_hz / 1_000_000
                    self._log("ERR", tr("cat.log.refused", mhz=f"{mhz:.3f}"))
                    # "?;" blijft in de melding: EIBI/FT8 herkennen een weigering daaraan
                    return False, tr("cat.err.refused", mhz=f"{mhz:.3f}")
            return True, ""
        except Exception as e:
            self._log("ERR", str(e))
            return False, str(e)

    # ── Modus instellen ───────────────────────────────────────────────────────

    # MD-commando modi (conform FT-950 CAT ref. p.11)
    _MODE_CODES = {
        "LSB":   "1", "USB":   "2", "CW":    "3",
        "FM":    "4", "AM":    "5", "RTTY":  "6",
        "CW-R":  "7", "PKT-L": "8", "FSK-R": "9",
        "PKT-FM":"A", "FM-N":  "B", "PKT-U": "C",
        "AM-N":  "D",
    }
    # Kenwood/Elecraft MD-codes (geen aparte datamodus: PKT → SSB)
    _KENWOOD_MODES = {"LSB": "1", "USB": "2", "CW": "3", "FM": "4", "AM": "5",
                      "RTTY": "6", "CW-R": "7", "FSK-R": "9",
                      "PKT-L": "1", "PKT-U": "2", "PKT-FM": "4", "FM-N": "4", "AM-N": "5"}
    # Icom CI-V commando 06
    _ICOM_MODES = {"LSB": 0x00, "USB": 0x01, "AM": 0x02, "CW": 0x03, "RTTY": 0x04,
                   "FM": 0x05, "CW-R": 0x07, "FSK-R": 0x08,
                   "PKT-L": 0x00, "PKT-U": 0x01, "PKT-FM": 0x05, "FM-N": 0x05, "AM-N": 0x02}
    # Yaesu FT-817/857/897 opcode 07 (DIG voor data/RTTY, PKT voor FM-packet)
    _FT817_MODES = {"LSB": 0x00, "USB": 0x01, "CW": 0x02, "CW-R": 0x03, "AM": 0x04,
                    "AM-N": 0x04, "FM": 0x08, "FM-N": 0x88, "RTTY": 0x0A, "FSK-R": 0x0A,
                    "PKT-L": 0x0A, "PKT-U": 0x0A, "PKT-FM": 0x0C}

    def set_mode(self, mode: str) -> tuple[bool, str]:
        """
        Stel de operatiemodus in via het MD-commando (conform CAT ref. p.11).
        mode: "USB", "LSB", "CW", "FM", "AM", "RTTY", enz.
        Geeft (True, "") of (False, foutmelding) terug.
        """
        if not self.connected:
            ok, err = self.connect()
            if not ok:
                return False, err

        m = mode.upper()
        code = self._MODE_CODES.get(m)
        if not code:
            return False, tr("cat.err.unknown_mode", mode=mode)

        kind = self._kind()
        if kind in ("rigctld", "flrig"):
            try:
                with self._lock:
                    ok = self._net.set_mode(m)
                self._log("TX", f"M {m}".encode())
                return (True, "") if ok else (False, tr("cat.err.mode_refused", mode=mode))
            except Exception as e:
                self._log("ERR", str(e))
                return False, str(e)
        if kind == "icom":
            addr = int(getattr(self._cfg, "cat_civ_addr", 0x58))
            data = bytes([0xFE, 0xFE, addr, 0xE0, 0x06,
                          self._ICOM_MODES.get(m, 0x01), 0xFD])
        elif kind == "ft817":
            data = bytes([self._FT817_MODES.get(m, 0x01), 0, 0, 0, 0x07])
        elif kind == "kenwood":
            # Kenwood/Elecraft: MD<n>; (zonder de '0' van Yaesu); datamodi → SSB
            data = f"MD{self._KENWOOD_MODES.get(m, '2')};".encode("ascii")
        else:
            data = f"MD0{code};".encode("ascii")
        try:
            with self._lock:
                self._serial.write(data)
                self._serial.flush()
                import time; time.sleep(0.05)
                rx = b""
                while self._serial.in_waiting:
                    rx += self._serial.read(self._serial.in_waiting)
                    time.sleep(0.02)
            self._log("TX", data)
            if rx:
                self._log("RX", rx)
                if b"?" in rx:
                    return False, tr("cat.err.mode_refused", mode=mode)
            return True, ""
        except Exception as e:
            self._log("ERR", str(e))
            return False, str(e)

    # ── Protocol encoders ─────────────────────────────────────────────────────

    @staticmethod
    def _fa_cmd_8(freq_hz: int) -> bytes:
        """Yaesu FT-950/2000/DX: FA + 8 cijfers + ;  (conform CAT ref. p.2,9)
        Bereik: 0030000 – 56000000 Hz → FA00030000; … FA56000000;"""
        return f"FA{freq_hz:08d};".encode("ascii")

    @staticmethod
    def _fa_cmd_11(freq_hz: int) -> bytes:
        """Kenwood / Elecraft: FA + 11 cijfers + ;
        Bereik: 00000000000 – 99999999999 Hz"""
        return f"FA{freq_hz:011d};".encode("ascii")

    def _icom_cmd(self, freq_hz: int) -> bytes:
        """Icom CI-V: binary BCD freq-set commando."""
        addr = int(getattr(self._cfg, "cat_civ_addr", 0x58))
        bcd  = []
        for _ in range(5):
            lo = freq_hz % 10;  freq_hz //= 10
            hi = freq_hz % 10;  freq_hz //= 10
            bcd.append((hi << 4) | lo)
        return bytes([0xFE, 0xFE, addr, 0xE0, 0x05] + bcd + [0xFD])


# ── Module-niveau singleton ───────────────────────────────────────────────────
_instance: CatInterface | None = None


def get_instance() -> CatInterface | None:
    return _instance


def set_instance(cat: CatInterface):
    global _instance
    _instance = cat


def serial_available() -> bool:
    return _serial_available
