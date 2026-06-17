"""HAMIOS sound utilities - consolidated beep/alert functions."""


def play_beep(frequency: int, duration: int) -> None:
    """Play a system beep at given frequency and duration.

    Args:
        frequency: Frequency in Hz (e.g., 600, 1400, 2800)
        duration: Duration in milliseconds (e.g., 5, 180)
    """
    try:
        import winsound
        winsound.Beep(frequency, duration)
    except Exception:
        pass


def play_tick() -> None:
    """Geigerteller-tick: één korte puls."""
    play_beep(2800, 5)


def play_sat_enter() -> None:
    """Satelliet komt QTH-zone binnen: één hoge ping."""
    play_beep(1400, 180)


def play_sat_exit() -> None:
    """Satelliet verlaat QTH-zone: één lage ping."""
    play_beep(600, 180)


def play_sat_ping() -> None:
    """Stijgende "ding" ping for satellite detection."""
    try:
        import winsound
        winsound.Beep(880, 80)      # Low tone
        winsound.Beep(1320, 120)    # High tone - rising
    except Exception:
        pass
