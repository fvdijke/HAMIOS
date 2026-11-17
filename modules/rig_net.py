"""
HAMIOS — radiobesturing via het netwerk: Hamlib rigctld en flrig.

Daarmee werkt CAT met vrijwel elke radio (Hamlib kent ruim 200 modellen),
zonder dat HAMIOS zelf het protocol van de radio hoeft te spreken.

  rigctld  TCP, tekstprotocol:  f → '14074000'   F 14074000 → 'RPRT 0'
                                M USB 0 → 'RPRT 0'
  flrig    XML-RPC (HTTP):      rig.get_vfo, rig.set_frequency, rig.set_mode
"""

from __future__ import annotations

import socket
import xmlrpc.client

DEFAULT_PORT = {"rigctld": 4532, "flrig": 12345, "rotctld": 4533}
TIMEOUT_S = 2.0

# HAMIOS-radiomodus (zie CatInterface._MODE_CODES) → Hamlib-modus
_HAMLIB_MODES = {"LSB": "LSB", "USB": "USB", "CW": "CW", "CW-R": "CWR", "AM": "AM",
                 "AM-N": "AM", "FM": "FM", "FM-N": "FM", "RTTY": "RTTY", "FSK-R": "RTTYR",
                 "PKT-U": "PKTUSB", "PKT-L": "PKTLSB", "PKT-FM": "PKTFM"}
# flrig: modusnamen verschillen per radio; de gangbare basisnamen
_FLRIG_MODES = {"LSB": "LSB", "USB": "USB", "CW": "CW", "CW-R": "CW-R", "AM": "AM",
                "AM-N": "AM", "FM": "FM", "FM-N": "FM", "RTTY": "RTTY", "FSK-R": "RTTY-R",
                "PKT-U": "USB", "PKT-L": "LSB", "PKT-FM": "FM"}


def parse_address(text: str, kind: str) -> tuple[str, int]:
    """'host:poort', 'host' of '' → (host, poort); standaard 127.0.0.1."""
    text = (text or "").strip()
    host, port = "127.0.0.1", DEFAULT_PORT.get(kind, 4532)
    if not text or text.upper().startswith("COM"):
        return host, port
    if ":" in text:
        h, _, p = text.rpartition(":")
        host = h.strip("[] ") or host
        try:
            port = int(p)
        except ValueError:
            pass
    else:
        host = text
    return host, port


class _TimeoutTransport(xmlrpc.client.Transport):
    def make_connection(self, host):
        conn = super().make_connection(host)
        conn.timeout = TIMEOUT_S
        return conn


class NetRig:
    """Gemeenschappelijke interface voor rigctld en flrig."""

    def __init__(self, kind: str, address: str):
        self.kind = kind
        self.host, self.port = parse_address(address, kind)
        self._sock: socket.socket | None = None
        self._rpc = None
        self.is_open = False

    # ── verbinding ──────────────────────────────────────────────────────────
    def open(self):
        if self.kind == "rigctld":
            self._sock = socket.create_connection((self.host, self.port), timeout=TIMEOUT_S)
            self._sock.settimeout(TIMEOUT_S)
        else:
            self._rpc = xmlrpc.client.ServerProxy(f"http://{self.host}:{self.port}/RPC2",
                                                  transport=_TimeoutTransport())
            self._rpc.rig.get_vfo()          # verbindingstest
        self.is_open = True

    def close(self):
        self.is_open = False
        if self._sock is not None:
            try:
                self._sock.sendall(b"q\n")
            except OSError:
                pass
            try:
                self._sock.close()
            except OSError:
                pass
        self._sock = None
        self._rpc = None

    # ── rigctld ─────────────────────────────────────────────────────────────
    def _cmd(self, line: str) -> str:
        """Eén rigctld-opdracht; geeft de eerste antwoordregel terug."""
        if self._sock is None:
            raise OSError("not connected")
        self._sock.sendall(line.encode("ascii") + b"\n")
        buf = b""
        while not buf.endswith(b"\n"):
            chunk = self._sock.recv(256)
            if not chunk:
                self.is_open = False
                raise OSError("connection closed")
            buf += chunk
        return buf.decode("ascii", errors="replace").splitlines()[0].strip()

    @staticmethod
    def _rprt_ok(reply: str) -> bool:
        return not reply.startswith("RPRT") or reply == "RPRT 0"

    # ── publieke bediening ──────────────────────────────────────────────────
    def read_freq(self) -> int:
        if self.kind == "rigctld":
            reply = self._cmd("f")
            return int(float(reply)) if reply and reply[0].isdigit() else 0
        return int(float(self._rpc.rig.get_vfo()))

    def set_freq(self, hz: int) -> bool:
        if self.kind == "rigctld":
            return self._rprt_ok(self._cmd(f"F {int(hz)}"))
        self._rpc.rig.set_frequency(float(hz))
        return True

    def set_mode(self, mode: str) -> bool:
        m = mode.upper()
        if self.kind == "rigctld":
            return self._rprt_ok(self._cmd(f"M {_HAMLIB_MODES.get(m, 'USB')} 0"))
        self._rpc.rig.set_mode(_FLRIG_MODES.get(m, "USB"))
        return True
