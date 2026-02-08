from time import monotonic

_t0 = monotonic()


def now() -> float:
    """Get elapsed time in seconds since initialisation."""
    return monotonic() - _t0


def reset() -> None:
    """Reset the clock time to 0."""
    global _t0
    _t0 = monotonic()
