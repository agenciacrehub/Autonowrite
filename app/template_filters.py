from datetime import datetime

def timesince(dt, default="just now"):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    """
    if dt is None:
        return ""
        
    now = datetime.utcnow()
    diff = now - dt
    
    periods = [
        ('year', 'years', 60*60*24*365),
        ('month', 'months', 60*60*24*30),
        ('day', 'days', 60*60*24),
        ('hour', 'hours', 60*60),
        ('minute', 'minutes', 60),
        ('second', 'seconds', 1)
    ]
    
    for period, plural_period, seconds in periods:
        value = diff.total_seconds() / seconds
        if value >= 1:
            value = int(round(value))
            if value == 1:
                return f"{value} {period} ago"
            else:
                return f"{value} {plural_period} ago"
    return default
