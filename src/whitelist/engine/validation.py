def validate_daily_bar(high: float, low: float, close: float, instrument_type: str) -> bool:
    """
    Validates daily bars before appending to history.
    Returns True if valid, False if malformed.
    """
    if instrument_type != "EQUITY" and close == 0.0 and high == 0.0 and low == 0.0:
        # Gracefully accept zero-price for non-equity instruments
        return True
        
    if not (high >= low >= 0):
        return False
    if not (low <= close <= high):
        return False
        
    return True
