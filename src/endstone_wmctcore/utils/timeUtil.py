from datetime import datetime, timedelta

class TimezoneUtils:
    TIMEZONE_OFFSETS = {
        "EST": -5,  # Standard time offset (EST)
    }

    @staticmethod
    def is_dst(timestamp):
        """Determines if a given timestamp falls within Daylight Saving Time (DST) for Eastern Time."""
        try:
            dt = datetime.utcfromtimestamp(timestamp)  # Use UTC time
        except (OSError, ValueError):
            return False  # If timestamp is invalid, return False

        year = dt.year

        # Second Sunday of March at 2 AM (DST Start)
        dst_start = datetime(year, 3, 8, 2)  # Start searching from March 8th at 2 AM
        while dst_start.weekday() != 6:  # Find the first Sunday
            dst_start += timedelta(days=1)

        # First Sunday of November at 2 AM (DST End)
        dst_end = datetime(year, 11, 1, 2)  # Start searching from November 1st at 2 AM
        while dst_end.weekday() != 6:
            dst_end += timedelta(days=1)

        # Eastern Daylight Time (EDT) applies between these dates
        return dst_start <= dt < dst_end

    @staticmethod
    def convert_to_timezone(timestamp, timezone_name):
        """Converts a UTC timestamp to EST/EDT time with proper DST handling."""
        try:
            if timezone_name not in TimezoneUtils.TIMEZONE_OFFSETS:
                return "CORRUPTED (CRASH) - Est. Duration"

            standard_offset = TimezoneUtils.TIMEZONE_OFFSETS[timezone_name]
            dst_offset = 1 if TimezoneUtils.is_dst(timestamp) else 0

            # Convert UTC time to local time
            utc_time = datetime.utcfromtimestamp(timestamp)
            local_time = utc_time + timedelta(hours=standard_offset + dst_offset)

            # Determine the correct timezone label (EST or EDT)
            timezone_label = "EDT" if dst_offset else "EST"

            return local_time.strftime('%Y-%m-%d %I:%M:%S %p') + f" {timezone_label}"

        except (OSError, ValueError, TypeError):
            # If there are invalid inputs or timestamp errors, return "CORRUPTED"
            return "CORRUPTED (CRASH) - Est. Duration"
