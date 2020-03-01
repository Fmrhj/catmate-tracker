from datetime import datetime
from datetime import timedelta
import numpy as np
import pandas as pd

standard_date_format = "%Y-%m-%d %H:%M:%S"


def perdelta(start, end, delta):
    # generates a range of dates separated with start and end dates and a delta
    curr = start
    while curr < end:
        yield curr
        curr += delta


def nearest(items, pivot):
    # calculates the nearest item in a list from a pivot item
    return min(items, key=lambda x: abs(x - pivot))


def generate_next_meals_table():
    """ Function to fill a table with future meal time stamps
     Args:

     Returns:
         tmp_frame (DataFrame): pandas DataFrame with future meals
     """
    time_stamp_var = datetime.now()
    tmp = {'time_stamp': time_stamp_var.strftime(standard_date_format),
           'next_meals': generate_next_meals(time_stamp_var),
           'remaining_meals': np.linspace(start=4, stop=1, num=4)}
    tmp_frame = pd.DataFrame(tmp)

    return tmp_frame


def generate_next_meals(time_stamp_now=datetime.now()):
    """ Function to fill a table with future meal time stamps
    Args:
        time_stamp_now (datetime)

    Returns:
        list: with date for next meals
    """
    today_evening = datetime.strptime(time_stamp_now.strftime("%Y-%m-%d") + " 19:00:00", standard_date_format)
    today_morning = datetime.strptime(time_stamp_now.strftime("%Y-%m-%d") + " 07:00:00", standard_date_format)

    # Assign next meal to next following date today
    next_meal = max(today_evening, today_morning)

    # If the next meal is already in the past, take the next meal in the morning
    if next_meal < time_stamp_now:
        tomorrow_morning = datetime.strptime(time_stamp_now.strftime("%Y-%m-%d") + " 07:00:00",
                                             standard_date_format) + timedelta(days=1)
        next_meal = tomorrow_morning

    # Generate following meals for the next days.
    # Our catmate is programmed to rotate every 12 hours with 4 slots = 2 days
    date_list = []
    for date_item in perdelta(next_meal, next_meal + timedelta(days=2), timedelta(days=0.5)):
        date_list.append(date_item)

    return date_list


def calculate_remaining_meals(meals_table):
    """ Function to retrieve how many meals are left
    Args:
        meals_table (DataFrame): pandas DataFrame

    Returns:
        remaining_meals (int): number of remaining meals
    """
    b = meals_table[meals_table.next_meals == nearest(meals_table['next_meals'], datetime.now())][['remaining_meals']]
    return b.remaining_meals
