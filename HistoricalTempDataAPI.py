"""This module demonstrates unpacking JSON strings and the zip function.

This module builds on Assignment Ten, and completes the quarter-long
project. Made modifications to the HistoricalTemps class. Created a
static method that converts a JSON string to a list and extracts
historical dates and their corresponding temperatures. Modified the
load_temps method that uses data from open-meteo. Updated the start and
end setters. Lastly, this module contains a new module level function
that allows the user to change start and end dates.
"""
from datetime import datetime

import pgeocode as pgeo
import math
import requests
import json


request_url = "https://archive-api.open-meteo.com/v1/archive"


def main():
    """Ask the user their name and respond. Then, call menu function."""
    user_name = input("Please enter your name: ")
    print(f"Hi {user_name}, let's explore some historical temperatures.")
    print()
    menu()


def print_menu(dataset_one, dataset_two):
    """Print 'Main Menu' and all user menu options."""
    print("Main Menu")
    if dataset_one is not None:
        print("1 - Replace " + dataset_one.loc_name)
    else:
        print("1 - Load dataset one")
    if dataset_two is not None:
        print("2 - Replace " + dataset_two.loc_name)
    else:
        print("2 - Load dataset two")
    print("3 - Compare average temperatures")
    print("4 - Dates above threshold temperature")
    print("5 - Highest historical dates")
    print("6 - Change start and end dates for dataset one")
    print("7 - Change start and end dates for dataset two")
    print("9 - Quit")


def menu():
    """Call the print_menu function and ask user to choose from options.

    Create two names called dataset_one and dataset_two. Attempt to
    convert the user input to an integer. If the user input is something
    that cannot be converted, catch the error and tell the user to enter
    a number the next time. If the entry was not a valid selection, tell
    the user they must choose an integer from the menu. If the user
    input is valid, print out a unique statement for each choice. Keep
    asking user to input a valid number until the user decides to exit
    the program. Upon exit, thank the user for using the database.
    If the user enters 1 or 2, call the create_dataset function and
    return dataset_one or dataset_two, respectively.
    """
    dataset_one = None
    dataset_two = None
    print_menu(dataset_one, dataset_two)
    user_input = input("What is your choice? ")
    while user_input != "9":
        try:
            int_user_input = int(user_input)
        except ValueError:
            print("Please enter a number only")
            print_menu(dataset_one, dataset_two)
            user_input = input("What is your choice? ")
            continue
        match int_user_input:
            case 1:
                dataset_one = create_dataset()
            case 2:
                dataset_two = create_dataset()
            case 3:
                compare_average_temps(dataset_one, dataset_two)
            case 4:
                print_extreme_days(dataset_one)
            case 5:
                print_top_five_days(dataset_one)
            case 6:
                change_dates(dataset_one)
                # print("selection six is almost functional")
            case 7:
                change_dates(dataset_one)
                # print("almost finished working on selection 7")
            case 9:
                break
            case _:
                print("That wasn't a valid selection")
        print_menu(dataset_one, dataset_two)
        user_input = input("What is your choice? ")
    print("Goodbye!  Thank you for using the database")


def compare_average_temps(dataset_one, dataset_two):
    """Print the name and average temps of each place.

    Take in two parameters, dataset_one and dataset_two, and ensure they
    are not none. If either is none, tell user to load two datasets
    first. If both are not none, print out the location and its
    average temperature.

    @param dataset_one: HistoricalTemps object
    @type: HistoricalTemps
    @param dataset_two: HistoricalTemps object
    @type: HistoricalTemps
    """
    if dataset_one is not None and dataset_two is not None:
        print(f"The average maximum temperature for {dataset_one.loc_name} was"
              f" {HistoricalTemps.average_temp(dataset_one):.2f}"
              f" degrees Celsius")
        print(f"The average maximum temperature for {dataset_two.loc_name} was"
              f" {HistoricalTemps.average_temp(dataset_two):.2f}"
              f" degrees Celsius")
    else:
        print("Please load two datasets first")


class HistoricalTemps:
    """An object that stores daily temperatures for a given zip code."""

    def __init__(self, zip_code: str, start="1950-08-13", end="2023-08-25"):
        """Create a HistoricalTemps object.

        @param zip_code: stored historical temps of the area
        @type zip_code: str
        @param start: Lower bound for the range of dates.
        @type start: str
        @param end: Upper bound for the range of dates.
        @type end: str
        @return: None
        @rtype: NoneType
        """
        self._zip_code = zip_code
        self._start = start
        self._end = end
        lat, lon, loc_name = HistoricalTemps.zip_to_loc_info(self, zip_code)
        if math.isnan(lat):
            raise LookupError
        self._lat = lat
        self._lon = lon
        self._loc_name = loc_name
        self._temp_list = None
        self._load_temp()

    @property
    def zip_code(self):
        """Return zip_code."""
        return self._zip_code

    @property
    def start(self):
        """Return start date."""
        return self._start

    @property
    def loc_name(self):
        """Return loc_name."""
        return self._loc_name

    @start.setter
    def start(self, start: str):
        """Set start date."""
        original_start_date = self._start
        try:
            self._start = start
            self._load_temp()
        except LookupError:
            # self._start = original_start_date
            # self._start = original_start_date
            # have to revert date back to old date, then raise again error again
            # have to save the old date
            print("Start date could not be changed.")

    @property
    def end(self):
        """Return end date."""
        return self._end

    @end.setter
    def end(self, end: str):
        """Set end date."""
        original_end_date = self._end
        try:
            self._end = end
            self._load_temp()
        except LookupError:
            print("End date could not be changed. Please check that the end "
                  "date is in the correct format and is before the current "
                  f"end date of {self._end}.")

    @staticmethod
    def zip_to_loc_info(self, zip: str):
        """Use zip code to get latitude, longitude, and location name.

        Create a pgeo object and use the object to create a dictionary
        containing info about the zip code. Store the zip code's
        latitude, longitude, and location name. Return latitude,
        longitude, and location name.

        @param zip: zip code of historical temperature area
        @type zip: str
        @param self: HistoricalTemp object
        @type: HistoricalTemp
        @return: lat, lon, loc_name
        @rtype: str
        """
        geocoder = pgeo.Nominatim('us')
        result = geocoder.query_postal_code(zip)
        lat = result['latitude']
        lon = result['longitude']
        loc_name = result['place_name']
        return lat, lon, loc_name

    def _load_temp(self):
        """Assign self._temp_list with historical temperature data.

        Call the requests function request data from open-meteo. Print
        results.
        """
        parameters = {"latitude": self._lat, "longitude": self._lon,
                      "start_date": self._start, "end_date": self._end,
                      "daily": "temperature_2m_max",
                      "timezone": "America/Los_Angeles"}
        json_string = requests.get(request_url, params=parameters)
        self._temp_list = self._convert_json_to_list(json_string)
        return self._temp_list

    def average_temp(self):
        """Calculate and return an area's average temperature.

        @return: average temperature
        @rtype: float
        """
        sum_of_temperatures = 0.0
        for temperature in self._temp_list:
            sum_of_temperatures += temperature[1]
        average_temperature = sum_of_temperatures / len(self._temp_list)
        return average_temperature

    def extreme_days(self, threshold: float):
        """Determine and return temps that exceed threshold, with dates.

        @param threshold: user inputted temperature threshold
        @return: list of dates with corresponding temps that exceed
                 temperature threshold
        @rtype: list of tuples
        """
        return [(date, temp) for date, temp in self._temp_list
                if temp > threshold]

    def top_x_days(self, num_days=10):
        """Determine the hottest temperatures and corresponding dates.

        Take in the parameter num_days and use it to determine the
        hottest days in the temperature list. The default value is 10.

        :param num_days: int
        :return: list
        """
        top_temps = sorted(self._temp_list, key=lambda x: x[1], reverse=True)
        return top_temps[0:num_days]

    @staticmethod
    def _convert_json_to_list(data):
        json_data = json.loads(data.text)
        dates_and_temps = json_data["daily"]
        dates = dates_and_temps["time"]
        temps = dates_and_temps["temperature_2m_max"]
        # print(dates)
        dates_and_temps_list = list(zip(dates, temps))
        return dates_and_temps_list


def create_dataset():
    """Create and return a historical temp object.

    @return: historical_temps object
    @rtype: historical_temps
    """
    user_zip_code = input("Please enter a zip code: ")
    try:
        historical_temps = HistoricalTemps(zip_code=user_zip_code)
        return historical_temps
    except LookupError:
        print("Data could not be loaded. Please check that the zip code is "
              "correct and that you have a working internet connection.")
        return None


def print_extreme_days(dataset: HistoricalTemps):
    """Print the temps, with dates, that exceed threshold temperature.

    Take in a HistoricalTemps object and make sure it is not none. If it
    is, let the user know to load a dataset first. If the dataset is not
    none, ask the user to input a threshold temperature. If the entry is
    invalid, tell the user to enter a valid temperature. If the
    temperature is valid, invoke extreme_days onto the dataset using the
    threshold temperature as the parameter. Then print out the number of
    days that exceed the threshold temperature, the threshold
    temperature, the dataset location, and the temperatures, with dates,
    that exceed the temperature threshold.

    @param dataset: HistoricalTemps object
    """
    if dataset is None:
        print("Please load this dataset first")
    else:
        threshold_temperature = input("List days above what temperature? ")
        float_threshold_temperature = None
        extreme_temp_days = None
        try:
            float_threshold_temperature = float(threshold_temperature)
            extreme_temp_days = (dataset.extreme_days
                                 (float_threshold_temperature))
        except ValueError:
            print("Please enter a valid temperature")

        if (float_threshold_temperature is not None
                and extreme_temp_days is not None):
            print(f"There are {len(extreme_temp_days)} days above "
                  f"{float_threshold_temperature} degrees in "
                  f"{dataset.loc_name}")
            for date, temp in extreme_temp_days:
                print(f"{date}: {temp}")


def print_top_five_days(dataset: HistoricalTemps):
    """Print the hottest five days and corresponding temperatures.

    Take in a HistoricalTemps object and make sure it is not none. If it
    is, let the user know to load a dataset first. If the dataset is not
    none, determine the hottest five days and their corresponding
    temperatures. Print out the dataset's location and its hottest five
    days with their temperatures.

    :param dataset: HistoricalTemps
    :return: str
    """
    if dataset is None:
        print("Please load this dataset first")
    else:
        top_five_days = dataset.top_x_days(5)
        print(f"Following are the hottest five days in {dataset.loc_name} on "
              "record from" f"\n{dataset.start} to {dataset.end}")
        for date, temp in top_five_days:
            print(f"Date {date}: {temp}")


def change_dates(dataset: HistoricalTemps):
    """Change start and end dates.

    Take in a HistoricalTemps object and change the start and end dates of the
    dataset. If either change is unsuccessful, the dates will not change and
    will refer to the original dates.

    :param dataset: HistoricalTemps
    :return:none
    """
    if dataset is None:
        print("Please load this dataset first")
    else:
        try:
            new_start_date = input("Please enter a new start date (YYYY-MM-DD): ")
            dataset.start = new_start_date
        except ValueError:
            print("inside change start date except block")

        # original_start_date = dataset.start
        # try:
        #     print(original_start_date)
        #     new_start_date = input("Please enter a new start date "
        #                            "(YYYY-MM-DD): ")
        #     dataset.start = new_start_date
        #     # print(dataset.start)
        # except ValueError:
        #     print("Change me")
        #     # dataset.start = original_start_date
        # if dataset.start is not original_start_date:
        #     try:
        #         new_end_date = input("Please enter a new end date (YY-MM-DD): ")
        #         dataset.end = new_end_date
        #     except ValueError:
        #         print("end date message")


if __name__ == "__main__":
    main()
