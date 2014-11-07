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
    assert decide("test_returning_citizen.json", "watchlist.json", "countries.json") == ["Accept", "Accept"]
    assert decide("test_watchlist.json", "watchlist.json", "countries.json") == ["Secondary"]
    assert decide("test_quarantine.json", "watchlist.json", "countries.json") == ["Quarantine"]


# Test when files are not found
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


# Test when files are incomplete
def test_incomplete():
    # Test blank entries
    ### Index 0: Blank passport
    ### Index 1: Blank name
    ### Index 2: Blank location
    ### Index 3: Blank entry reason
    assert decide("test_blank.json", "watchlist.json", "countries.json") == ["Reject", "Reject", "Reject", "Reject"]
    # Test invalid entries
    ### Index 0: Invalid passport
    ### Index 1: Invalid birth date
    assert decide("test_invalid.json", "watchlist.json", "countries.json") == ["Reject", "Reject"]