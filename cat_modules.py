from datetime import datetime
import numpy as np

# Global variable
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


""" Function to fill a table with future meal time stamps
Args: 
    time_stamp_now (datetime)

Returns:
    list: with date for next meals
"""
def generateNextMeals(time_stamp_now=datetime.now()):
    today_evening = datetime.strptime(time_stamp_now.strftime("%Y-%m-%d") + " 19:00:00", standard_date_format)
    today_morning = datetime.strptime(time_stamp_now.strftime("%Y-%m-%d") + " 07:00:00", standard_date_format)

    # Assign next meal to next following date
    if (today_evening > time_stamp_now):
        next_meal = today_evening
    else:
        next_meal = today_morning

    # Generate following meals for the next days.
    # Our catmate is programmed to rotate every 12 hours with 4 slots = 2 days
    date_list = []
    for date_item in perdelta(next_meal, next_meal + timedelta(days=2), timedelta(days=0.5)):
        date_list.append(date_item)

    return (date_list)


""" Function to retrieve how many meals are left
Args:
    meals_table (DataFrame) pandas DataFrame

Returns:
    remaining_meals (int) 
"""
def calculateRemainingMeals(meals_table):
    b = a[a.next_meals == nearest(a['next_meals'], datetime.now())][['remaining_meals']]
    return (b.remaining_meals)