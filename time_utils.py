import time

# Configuration for timezone and daylight saving
TIMEZONE_OFFSET = 1  # Offset in hours from UTC (standard time)
DAYLIGHT_SAVING_OFFSET = 1  # Additional offset during daylight saving time

def get_timestamp_from_datestring(date_string):
    """
    Converts a date string in the format 'YYYY-MM-DD HH:MM' to a Unix timestamp.

    Args:
        date_string (str): The date string to convert.

    Returns:
        int: The Unix timestamp corresponding to the given date string.
    """
    # Split the date and time parts
    date_part, time_part = date_string.split(' ')
    year, month, day = map(int, date_part.split('-'))
    hour, minute = map(int, time_part.split(':'))

    # Create a tuple representing the date and time
    time_tuple = (year, month, day, hour, minute, 0, 0, 0, 0)

    # Use time.mktime to convert the tuple to a Unix timestamp
    unix_timestamp = int(time.mktime(time_tuple))
    return unix_timestamp

def is_daylight_saving(current_date):
    # Implement a method to determine if daylight saving time is in effect
    # For simplicity, assume daylight saving time is in effect from the last Sunday in March to the last Sunday in October
    year = current_date[0]
    month = current_date[1]
    day = current_date[2]

    if month < 3 or month > 10:
        return False
    if month > 3 and month < 10:
        return True
    
    # Calculate last Sunday of March
    last_sunday_march = 31 - (time.mktime((year, 3, 31, 0, 0, 0, 0, 0)) // 86400 + 3) % 7
    # Calculate last Sunday of October
    last_sunday_october = 31 - (time.mktime((year, 10, 31, 0, 0, 0, 0, 0)) // 86400 + 3) % 7

    if month == 3 and day > last_sunday_march:
        return True
    if month == 10 and day <= last_sunday_october:
        return False
    if month == 3 and day <= last_sunday_march:
        return False
    if month == 10 and day > last_sunday_october:
        return True

    return False

def get_current_time():
    current_time = time.localtime()
    local_timestamp = time.mktime(current_time) + TIMEZONE_OFFSET * 3600
    if is_daylight_saving(current_time):
        local_timestamp += DAYLIGHT_SAVING_OFFSET * 3600
    return int(local_timestamp)

def get_api_date():
    current_time = time.localtime(get_current_time())
    print("API time:", current_time)

    year = current_time[0]
    month = current_time[1]
    day = current_time[2]

    formatted_date = "{}-{:02d}-{:02d}".format(year, month, day)

    return formatted_date