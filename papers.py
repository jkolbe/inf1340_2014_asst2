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
from calendar import isleap



def decide(input_file, watchlist_file, countries_file):
    """
    Decides whether a traveller's entry into Kanadia should be accepted
    The order of priority for the immigration decisions: quarantine, reject, secondary, and accept.

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
    watchlist = data[1]
    countries = data[2]

    # will hold a list of return string values
    return_vals = []



    # entries is a list
    for entry in entries:

        if requires_quarantine(entry, countries):
            return_vals.append('Quarantine')
        else:
            if complete_record(entry):
                print('complete!')
                if requires_visa(entry, countries) and not is_valid_visa(entry):
                    return_vals.append({entry['first_name']: 'Reject'})
            else:
                return_vals.append('Reject')

        """

        print(entry['first_name'])
        print('requires quarantine? ', requires_quarantine(entry, countries))
        print('is on watchlist? ', is_on_watchilst(entry, watchlist))
        print('is complete? ', complete_record(entry))
        print('requires visa?', requires_visa(entry, countries))
        """

    return return_vals


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


def requires_quarantine(entry, countries):
    """
    Case:   If the traveler is coming from or via a country that has
            a medical advisory, he or she must be send to quarantine.
    :param  entry: object to be checked
    :param  countries: object containing country details
    :return: Boolean True if entries requires quarantine
    """

    # some entries might not contain "via" info so check only for the ones that do
    # also check if country is set and holds a value
    if 'via' in entry.keys() and 'country' in entry['via'].keys() and entry['via']['country'] != '':
        country_name = entry['via']['country']
        # check if country name exists in countries file
        if country_name in countries.keys():
            # print(countries[country_name]["medical_advisory"])
            return countries[country_name]["medical_advisory"] != ''


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
                if lrqr not in entry[location].keys() or entry[location][lrqr] == '':
                    rtr_value = False

    return rtr_value


def is_on_watchilst(entry, watchlist):
    """
    Case: If the traveller has a name or passport on the watch list, she or he must be sent to secondary processing.
    :param entry: object to be checked
    :param watchlist: list of objects containing watchlist entries
    :return: Boolean True if entry is on the watchlist
    """
    for person in watchlist:
        if (entry['first_name'] == person['first_name'] and entry['last_name'] == person['last_name']) \
                or entry['passport'] == person['passport']:
            return True


def requires_visa(entry, countries):
    """
    Case A: If the reason for entry is to visit and the visitor has a passport from a country from which
            a visitor visa is required, the traveller must have a valid visa.
    Case B: If the reason for entry is transit and the visitor has a passport from a country from which
            a transit visa is required, the traveller must have a valid visa.
    :param entry: object to be checked
    :param countries: object containing country details
    :return: Boolean True, if entry requires a visa to enter the country
    """
    if entry["entry_reason"] == "visit" and countries[entry['home']['country']]['transit_visa_required'] == '1':
        return True
    elif entry['entry_reason'] == 'transit' and countries[entry['home']['country']]['visitor_visa_required'] == '1':
        return True
    else:
        return False


def is_valid_visa(entry):
    """
    Check if traveller has a valid visa - one that is less than two years old.

    :param entry: object to be checked
    :return: Boolean True if traveller's visa is valid
    """

    #check if entry has a visa and if visa object is correctly formatted
    if 'visa' in entry.keys() and 'date' in entry['visa'].keys() and 'code' in entry['visa'].keys() \
            and entry['visa']['code'] != '' and valid_date_format(entry['visa']['date']):

        # get today's date - return in YYYY-MM-DD format (exactly what we want)
        today = datetime.date.today()

        # visa date is a string value, must convert to date object
        visa_date = (entry['visa']['date']).split('-')
        visa_date = datetime.date(int(visa_date[0]), month=int(visa_date[1]), day=int(visa_date[2]))

        # calculate day difference between today and visa's date
        delta_t = today - visa_date

        # check is less than 2 years = 730 or 731 if leap
        two_years = 730
        if isleap(today.year) or isleap(today.year - 1):
            two_years += 1

        if int(delta_t.days) < two_years:
            return True

    return False