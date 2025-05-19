from datetime import datetime

def format_date(date_str):
    """
        Transform an incomplète date in format YYYY-MM-DD
    """
    if not date_str or date_str.lower() == "none":
        return None
    
    parts = date_str.split("-")

    while len(parts) < 3:
        parts.append("01")

    try:
        return datetime.strptime("-".join(parts), "%Y-%m-%d")
    except ValueError:
        return None