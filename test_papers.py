#!/usr/bin/env python3

""" Module to test papers.py  """

__author__ = 'Joanna Kolbe, Olena Kit'
__email__ = "joannakolbe@gmail.com, olena.kit@mail.utoronto.ca"
__copyright__ = "2014 Joanna Kolbe, Olena Kit"
__status__ = "Prototype"

# imports one per line
import pytest
from papers import decide


# Basic tests
def test_basic():
    assert decide("test_returning_citizen.json", "watchlist.json",
                  "countries.json") == ["Accept", "Accept"]
    assert decide("test_watchlist.json", "watchlist.json",
                  "countries.json") == ["Secondary"]
    assert decide("test_quarantine.json", "watchlist.json",
                  "countries.json") == ["Quarantine"]


# File not found tests
def test_files():
    with pytest.raises(FileNotFoundError):
        decide("", "", "")
        decide("", "watchlist.json", "")
        decide("", "", "countries.json")
        decide("", "watchlist.json", "countries.json")
        decide("test_returning_citizen.json", "", "")
        decide("test_returning_citizen.json", "", "countries.json")
        decide("test_returning_citizen.json", "watchlist.json", "")
        decide("test_watchlist.json", "", "")
        decide("test_watchlist.json", "", "countries.json")
        decide("test_watchlist.json", "watchlist.json", "")
        decide("test_quarantine.json", "", "")
        decide("test_quarantine.json", "", "countries.json")
        decide("test_quarantine.json", "watchlist.json", "")


# Incomplete file tests
def test_incomplete():
    """
    Test blank entries
    Index 0: Blank passport
    Index 1: Blank first name
    Index 2: Blank last name
    Index 3: Blank birth date
    Index 4: Blank home country
    Index 5: Blank from country
    Index 6: Blank entry reason
    """
    assert decide("test_blank.json", "watchlist.json", "countries.json")\
        == ["Reject", "Reject", "Reject", "Reject",
            "Reject", "Reject", "Reject"]

    '''
    Test invalid entries
    Index 0: Invalid passport
    Index 1: Invalid birth date
    Index 2: Invalid visa date
    Index 3: Invalid visa code
    '''
    assert decide("test_invalid.json", "watchlist.json", "countries.json") == \
        ["Reject", "Reject", "Reject", "Reject"]


def test_visa():
    """
    Visa tests
    Index 0: Valid visa and entry is to visit
    Index 1: Expired visa and entry is to visit
    Index 2: Valid visa and entry is transit
    Index 3: Expired visa and entry is transit
    Index 4: Valid visa and entry is visit -
                from and via country both require visa
    Index 5: Valid visa and entry is visit - from country
                requires visa and via country does not
    Index 6: Valid visa and entry is visit - via country
                requires visa and from country does not
    """
    assert decide("test_visa.json", "watchlist.json", "countries.json") ==\
        ["Accept", "Reject", "Accept", "Reject", "Accept", "Accept", "Accept"]


def test_case():
    """
    Case mismatch tests
    Index 0: Passport, first name, last name, and country codes in uppercase
    Index 1: Passport in lowercase
    Index 2: First name and last name in lowercase
    Index 3: Country codes in lowercase
    """
    assert decide("test_case.json", "watchlist.json", "countries.json") ==\
        ["Secondary", "Secondary", "Secondary", "Secondary"]


def test_precedence():
    """
    Precedence tests
    Index 0: Quarantine over Reject - reject due to expired passport,
                but quarantine due to medical advisory
    Index 1: Quarantine over Secondary -secondary due to passport on watchlist,
                but quarantine due to medical advisory
    Index 2: Quarantine over Accept - accept due to returning to KAN,
                but quarantine due to medical advisory
    Index 3: Reject over Secondary - secondary due to passport on watchlist,
                but reject due to blank name
    Index 4: Reject over Accept - accept due to returning to KAN, but reject
                due to invalid passport
    Index 5: Secondary over Accept - accept due to returning to KAN,
                but secondary due to passport on watchlist
    """
    assert decide("test_precedence.json", "watchlist.json", "countries.json")\
        == ["Quarantine", "Quarantine", "Quarantine", "Reject",
            "Reject", "Secondary"]


def test_input_file():
    """
    test for proper input type format
    """
    with pytest.raises(TypeError):
        # file does not contain a list of entries
        decide("test_input_file.json", "watchlist.json", "countries.json")
    with pytest.raises(TypeError):
        # entries in a list are not objects
        decide("test_input_file_2.json", "watchlist.json", "countries.json")
