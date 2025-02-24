from datetime import datetime

def ban_message(server, expiration, reason) -> str:
    return f"""
§cYou were banned from §6{server}
§cPunishment Expires: §6{expiration}
§cPunishment Reason: §6{reason}
""".strip()

def format_time_remaining(expiration) -> str:
    # Convert expiration timestamp to datetime object
    expiration_datetime = datetime.fromtimestamp(expiration)
    now = datetime.now()
    remaining = expiration_datetime - now

    if remaining.total_seconds() <= 0:
        return "Expired"

    # Check if expiration is more than 100 years
    if remaining.total_seconds() > 100 * 31536000:  # 100 years in seconds
        return "Never - Permanent Ban"

    total_seconds = int(remaining.total_seconds())

    years, rem = divmod(total_seconds, 31536000)  # 365 days
    months, rem = divmod(rem, 2592000)  # 30 days
    weeks, rem = divmod(rem, 604800)  # 7 days
    days, rem = divmod(rem, 86400)  # 1 day
    hours, rem = divmod(rem, 3600)  # 1 hour
    minutes, seconds = divmod(rem, 60)  # 1 minute

    time_parts = []
    if years: time_parts.append(f"{years} year{'s' if years > 1 else ''}")
    if months: time_parts.append(f"{months} month{'s' if months > 1 else ''}")
    if weeks: time_parts.append(f"{weeks} week{'s' if weeks > 1 else ''}")
    if days: time_parts.append(f"{days} day{'s' if days > 1 else ''}")
    if hours: time_parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes: time_parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
    if seconds: time_parts.append(f"{seconds} second{'s' if seconds > 1 else ''}")

    return ", ".join(time_parts)