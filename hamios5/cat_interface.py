"""
HAMIOS v5 — CAT radio-interface (conform FT-950 CAT Operation Reference Book)

Frequentie-digit-aantallen per radiotype:
  • Yaesu FT-950/2000/DX series → FA<8 cijfers>;   bijv. FA14250000;  (= 14.250 MHz)
      Paginanummer 2 handleiding: "FA14250000;" (Set command voorbeeld)
      Parameter P1 bereik: 0030000 – 56000000 (Hz), 8 cijfers
  • Kenwood / Elecraft (TS-590 e.d.) → FA<11 cijfers>;
  • Icom CI-V → binary BCD frame

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
        "Yaesu (FT-817/857/897)",
        "Kenwood / Elecraft",
        "Icom CI-V",
    ]

    _POLL_INTERVAL = 2.0   # seconden tussen frequentie-peilingen

    def __init__(self, cfg=None):
        self._cfg          = cfg
        self._serial       = None
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
        if not _serial_available:
            return False, "pyserial niet geïnstalleerd (pip install pyserial)"

        cfg = self._cfg
        if cfg is None:
            return False, "Geen configuratie beschikbaar"
        port = getattr(cfg, "cat_port", "").strip()
        if not port:
            return False, "Geen seriële poort ingesteld"

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

            self._log("INFO", f"Verbonden op {port}  "
                              f"{getattr(cfg, 'cat_baud', 9600)} baud  "
                              f"{getattr(cfg, 'cat_radio_type', '?')}")
            self._start_polling()
            return True, ""
        except PermissionError:
            self._serial = None
            msg = "PermissionError — poort al in gebruik door ander programma"
            self._log("ERR", msg)
            return False, msg
        except Exception as e:
            self._serial = None
            self._log("ERR", str(e))
            return False, str(e)

    def disconnect(self):
        self._stop_polling()
        with self._lock:
            if self._serial:
                try:
                    self._serial.close()
                except Exception:
                    pass
                self._serial = None
        self._log("INFO", "Verbinding verbroken")
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

    def _poll_loop(self):
        """
        Retourwaarden van _read_freq_hz_raw:
          int > 0  → geldige frequentie
          0        → verbonden maar geen geldige respons (?; of leeg)
          None     → verbindingsfout (exception / poort dicht)
        """
        import time
        while self._polling and self.connected:
            freq = self._read_freq_hz_raw()
            cb = self._freq_callback
            if freq is None:
                # Echte disconnect
                if cb:
                    try: cb(None)
                    except Exception: pass
                break
            else:
                # freq >= 0 : doorsturen (0 = verbonden maar freq onbekend)
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
        rtype = getattr(self._cfg, "cat_radio_type", "")
        try:
            if "Icom" in rtype:
                result = self._icom_read_freq()
            elif "Kenwood" in rtype or "Elecraft" in rtype:
                result = self._fa_read_freq(digits=11)
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
            while time.monotonic() < deadline:
                if self._serial.in_waiting:
                    buf += self._serial.read(self._serial.in_waiting)
                    if 0xFD in buf:
                        break
                time.sleep(0.02)
        # Zoek response frame: FE FE E0 addr 03 <5 bytes> FD
        i = 0
        while i < len(buf) - 10:
            if buf[i] == 0xFE and buf[i+1] == 0xFE and buf[i+4] == 0x03:
                bcd = buf[i+5:i+10]
                if len(bcd) == 5:
                    freq = 0
                    mul  = 1
                    for byte in bcd:
                        freq += (byte & 0x0F) * mul;      mul *= 10
                        freq += ((byte >> 4) & 0x0F) * mul; mul *= 10
                    return freq
            i += 1
        return None

    @property
    def connected(self) -> bool:
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
            return False, f"Onverwacht antwoord: {txt!r}"
        except Exception as e:
            return False, str(e)

    # ── Frequentie instellen ──────────────────────────────────────────────────

    def set_freq_hz(self, freq_hz: int) -> tuple[bool, str]:
        if not self.connected:
            ok, err = self.connect()
            if not ok:
                return False, err

        rtype = getattr(self._cfg, "cat_radio_type", "")
        try:
            if "Icom" in rtype:
                data = self._icom_cmd(freq_hz)
            elif "Kenwood" in rtype or "Elecraft" in rtype:
                data = self._fa_cmd_11(freq_hz)
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
                    self._log("ERR",
                        f"Radio weigert frequentie {mhz:.3f} MHz — "
                        "buiten bereik of radio niet in CAT-modus")
                    return False, f"Radio antwoordt ?; — frequentie geweigerd ({mhz:.3f} MHz)"
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

        code = self._MODE_CODES.get(mode.upper())
        if not code:
            return False, f"Onbekende modus: {mode!r}"

        rtype = getattr(self._cfg, "cat_radio_type", "")
        if "Icom" in rtype:
            return False, "Modus instellen via CI-V nog niet ondersteund"

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
                    return False, f"Radio weigert modus {mode}"
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
