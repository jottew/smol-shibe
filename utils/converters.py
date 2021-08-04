import re

MENTION_REGEX = re.compile(r"<@(!?)([0-9]*)>")

def format_list(items: list, seperator: str = "or", brackets: str = ""):
    if len(items) < 2:
        return f"{brackets}{items[0]}{brackets}"

    new_items = []
    for i in items:
        if not re.match(MENTION_REGEX, i):
            new_items.append(f"{brackets}{i}{brackets}")
        else:
            new_items.append(i)

    msg = ", ".join(list(new_items)[:-1]) + f" {seperator} " + list(new_items)[-1]
    return msg

def time(miliseconds: int, seconds: bool = False):
    if seconds:
        miliseconds = miliseconds*1000

    if not isinstance(miliseconds, int):
        raise TypeError(f"argument \"seconds\" requires int, not {miliseconds.__class__.__name__}")

    seconds = int(miliseconds / 1000)
    minutes = int(seconds / 60)
    hours = int(minutes / 60)
    days = int(hours / 24)

    for _ in range(seconds):
        miliseconds -= 1000

    for _ in range(minutes):
        seconds -= 60
    
    for _ in range(hours):
        minutes -= 60
    
    for _ in range(days):
        hours -= 24
    
    if days > 0:
        time = [f"{days}d", f"{hours}h", f"{minutes}m", f"{seconds}s", f"{miliseconds}ms"]
    elif hours > 0:
        time = [f"{hours}h", f"{minutes}m", f"{seconds}s", f"{miliseconds}ms"]
    elif minutes > 0:
        time = [f"{minutes}m", f"{seconds}s", f"{miliseconds}ms"]
    elif seconds > 0:
        time = [f"{seconds}s", f"{miliseconds}ms"]
    else:
        time = [f"{miliseconds}ms"]

    result = []
    for v in time:
        if not str(v).startswith("0"):
            result.append(v)

    return format_list(result, seperator="and", brackets="`")
