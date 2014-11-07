#!/usr/bin/env python3

""" Computer-based immigration office for Kanadia """

__author__ = 'Joanna Kolbe, Olena Kit'
__email__ = "joannakolbe@gmail.com, olena.kit@mail.utoronto.ca"
__copyright__ = "2014 Joanna Kolbe, Olena Kit"
__status__ = "Prototype"

# imports one per line
import re
import datetime
import json


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
    decisions = []

    # entries is a list
    for entry in entries:
        # As Quarantine has the highest priority, we check this case first
        if requires_quarantine(entry, countries):
            decisions.append('Quarantine')
        else:
            # if entry is not complete, reject the traveller
            if not complete_record(entry):
                decisions.append('Reject')
            # travellers with complete entry, continue to check for other cases
            else:
                if requires_visa(entry, countries) and not is_valid_visa(entry):
                    decisions.append('Reject')
                elif is_on_watchilst(entry, watchlist):
                    decisions.append('Secondary')
                else:
                    decisions.append('Accept')
    return decisions


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
    Checks if a traveler must be sent to quarantine, that is if
    he or she is coming from or via a country that has
    a medical advisory
    :param  entry: object to be checked
    :param  countries: object containing country details
    :return: Boolean True if entries requires quarantine
    """

    return_value = False

    # some entries might not contain "via" info so check only for the ones that do
    # also check if country is set and holds a value
    if 'via' in entry.keys() and 'country' in entry['via'].keys() and entry['via']['country'] != '':
        country_name = entry['via']['country'].upper()
        # check if country name exists in countries file
        if country_name in countries.keys():
            # return value will be set to true if requires quarantine
            return_value = countries[country_name]["medical_advisory"] != ''

    # if passed through checking 'via', also check 'from' country
    if not return_value:
        if 'from' in entry.keys() and 'country' in entry['from'].keys() and entry['from']['country'] != '':
            country_name = entry['from']['country'].upper()
            if country_name in countries.keys():
                return_value = countries[country_name]["medical_advisory"] != ''

    return return_value


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

    if not valid_passport_format(entry['passport']):
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
        if (entry['first_name'].upper() == person['first_name'].upper() and
                entry['last_name'].upper() == person['last_name'].upper()) or \
                entry['passport'].upper() == person['passport'].upper():
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
    if entry["entry_reason"].lower() == "transit" and \
            countries[entry['home']['country']]['transit_visa_required'] == '1':
        return True
    elif entry['entry_reason'].lower() == 'visit' and \
            countries[entry['home']['country']]['visitor_visa_required'] == '1':
        return True
    else:
        return False


def is_valid_visa(entry):
    """
    Check if traveller has a valid visa - one that is less than two years old.

    :param entry: object to be checked
    :return: Boolean True if traveller's visa is valid
    """

    # check if entry has a visa and if visa object is correctly formatted
    if 'visa' in entry.keys() and 'date' in entry['visa'].keys() and 'code' in entry['visa'].keys() \
            and entry['visa']['code'] != '' and valid_date_format(entry['visa']['date']):

        # get today's date - return in YYYY-MM-DD format (exactly what we want)
        today = datetime.date.today()

        # visa date is a string value, must convert to date object
        visa_date = (entry['visa']['date']).split('-')
        visa_date = datetime.date(int(visa_date[0]), month=int(visa_date[1]), day=int(visa_date[2]))

        # calculate day difference between today and visa's date
        delta_t = today - visa_date

        # get date of 2 years back
        two_years_ago = datetime.date(today.year - 2, month=today.month, day=today.day)
        # calculate day difference between today and 2 years ago
        two_years = today - two_years_ago

        if delta_t.days < two_years.days:
            return True

    return False