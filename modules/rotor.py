"""
HAMIOS — rotorbesturing: antenne naar een azimut draaien.

  gs232    Yaesu GS-232A/B (serieel; ook veel compatibele interfaces):  M090<CR>
  rotctld  Hamlib rotctld (netwerk, standaard 127.0.0.1:4533):          P 90.0 0

Elke opdracht loopt in een eigen korte verbinding op de achtergrond, zodat de
interface nooit blokkeert; het resultaat komt terug via een callback.
"""

from __future__ import annotations

import socket
import threading

from .i18n import tr

TIMEOUT_S = 3.0


def gs232_command(az: float) -> bytes:
    return f"M{int(round(az)) % 360:03d}\r".encode("ascii")


def rotctld_command(az: float) -> bytes:
    return f"P {az % 360:.1f} 0\n".encode("ascii")


def _parse_host(addr: str) -> tuple[str, int]:
    from .rig_net import parse_address
    return parse_address(addr, "rotctld")      # standaard 127.0.0.1:4533


def turn(cfg, az: float, done=None) -> bool:
    """Draai de rotor naar az (°). False als er geen rotor is ingesteld.
    done(ok: bool, bericht: str) wordt aangeroepen vanuit een achtergrondthread."""
    kind = getattr(cfg, "rotor_type", "") or ""
    addr = getattr(cfg, "rotor_addr", "") or ""
    if kind not in ("gs232", "rotctld"):
        return False

    def run():
        try:
            if kind == "rotctld":
                host, port = _parse_host(addr)
                with socket.create_connection((host, port), timeout=TIMEOUT_S) as s:
                    s.settimeout(TIMEOUT_S)
                    s.sendall(rotctld_command(az))
                    reply = s.recv(64).decode("ascii", errors="replace").strip()
                ok = (not reply) or reply.startswith("RPRT 0")
                msg = "" if ok else reply
            else:
                import serial
                if not addr:
                    raise OSError(tr("cat.err.no_port"))
                with serial.Serial(addr, int(getattr(cfg, "rotor_baud", 9600)),
                                   timeout=TIMEOUT_S) as ser:
                    ser.write(gs232_command(az))
                    ser.flush()
                ok, msg = True, ""
        except Exception as e:
            ok, msg = False, str(e)
        if done:
            try:
                done(ok, msg)
            except Exception:
                pass

    threading.Thread(target=run, daemon=True, name="rotor").start()
    return True
