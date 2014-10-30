#!/usr/bin/env python3

""" Computer-based immigration office for Kanadia """

__author__ = 'Joanna Kolbe, Olena Kit'
__email__ = "joannakolbe@gmail.com"
__copyright__ = "2014 Joanna Kolbe, Olena Kit"
__status__ = "Prototype"

# imports one per line
import re
import datetime
import json
import inspect


def decide(input_file, watchlist_file, countries_file):
    """
    Decides whether a traveller's entry into Kanadia should be accepted

    :param input_file: The name of a JSON formatted file that contains cases to decide
    :param watchlist_file: The name of a JSON formatted file that contains names and passport numbers on a watchlist
    :param countries_file: The name of a JSON formatted file that contains country data, such as whether
        an entry or transit visa is required, and whether there is currently a medical advisory
    :return: List of strings. Possible values of strings are: "Accept", "Reject", "Secondary", and "Quarantine"
    """

    # iterate through files, read and store json value for each in data list
    # data[0] will contain the entries, data[1] the watchlist and data[2] the countries
    data = []
    files = [input_file, watchlist_file, countries_file]
    for file in files:
        with open(file, "r") as file_reader:
            temp = file_reader.read()
        temp = json.loads(temp)
        data.append(temp)

    entries = data[0]
    # print(entries)



    # Case 1 : If the required information for an entry record is incomplete, the traveler must be rejected.


    # entries is a list
    for entry in entries:
        # each entry is a dictionary

        # check if record is complete
        if complete_record(entry):
            print('continue')
            # DO FURTHER CHECKING
        else:
            raise ValueError


def valid_passport_format(passport_number):
    """
    Checks whether a pasport number is five sets of five alpha-number characters separated by dashes
    :param passport_number: alpha-numeric string
    :return: Boolean; True if the format is valid, False otherwise
    """
    passport_format = re.compile('.{5}-.{5}-.{5}-.{5}-.{5}')

    if passport_format.match(passport_number):
        return True
    else:
        return False


def valid_date_format(date_string):
    """
    Checks whether a date has the format YYYY-mm-dd in numbers
    :param date_string: date to be checked
    :return: Boolean True if the format is valid, False otherwise
    """
    try:
        datetime.datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def complete_record(entry):
    """
    Checks whether an entry consists of all required information
    :param entry: object to be checked
    :return: Boolean True if complete information
    """
    rtr_value = True
    required = ['first_name', 'last_name', 'birth_date', 'passport', 'home', 'from', 'entry_reason']
    locations = ['home', 'from', 'via']
    location_required = ['city', 'region', 'country']

    # check if empty object has all required keys and non empty values
    for rqr in required:
        if rqr not in entry.keys() or entry[rqr] == '':
            rtr_value = False

    # check each location object in entry (Home, From, Via)  for existence of city, region and country
    for location in locations:
        # check only is location type set in the entry
        if location in entry.keys():
            for lrqr in location_required:
                if lrqr not in entry[location].keys():
                    rtr_value = False

    return rtr_value
