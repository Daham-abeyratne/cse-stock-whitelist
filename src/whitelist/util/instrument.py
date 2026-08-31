def get_instrument_type(symbol: str) -> str:
    """Derive instrument type from symbol suffix."""
    sym = symbol.upper()
    if ".N" in sym or ".X" in sym:
        return "EQUITY"
    elif ".R" in sym:
        return "RIGHTS"
    elif ".W" in sym:
        return "WARRANT"
    elif ".B" in sym or ".D" in sym:
        return "DEBT"
    return "EQUITY"
