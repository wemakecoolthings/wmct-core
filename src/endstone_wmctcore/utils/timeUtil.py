from datetime import datetime, timedelta
import time


class TimezoneUtils:
    TIMEZONE_OFFSETS = {
        "EST": -5,  # Standard time offset (EST)
    }

    # Automatically calculates if DST is active based on timestamp
    @staticmethod
    def is_dst(timestamp):
        # America/New_York DST: Starts second Sunday in March, Ends first Sunday in November
        dt = datetime.fromtimestamp(timestamp)
        year = dt.year

        # Second Sunday of March
        dst_start = datetime(year, 3, 8)
        while dst_start.weekday() != 6:  # Find the first Sunday
            dst_start += timedelta(days=1)

        # First Sunday of November
        dst_end = datetime(year, 11, 1)
        while dst_end.weekday() != 6:
            dst_end += timedelta(days=1)

        # Determine if we're in DST
        return dst_start <= dt < dst_end

    # Converts a UTC timestamp to any timezone without imports
    @staticmethod
    def convert_to_timezone(timestamp, timezone_name):
        offset = TimezoneUtils.TIMEZONE_OFFSETS.get(timezone_name, 0)
        if TimezoneUtils.is_dst(timestamp):
            offset += 1  # Adjust for DST

        utc_time = datetime.fromtimestamp(timestamp)
        local_time = utc_time + timedelta(hours=offset)
        return local_time.strftime('%Y-%m-%d %I:%M:%S %p') + f" {timezone_name}"
