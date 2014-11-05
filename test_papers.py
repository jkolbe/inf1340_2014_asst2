#!/usr/bin/env python3

""" Module to test papers.py  """

__author__ = 'Joanna Kolbe, Olena Kit'
__email__ = "joannakolbe@gmail.com, olena.kit@mail.utoronto.ca"
__copyright__ = "2014 Joanna Kolbe, Olena Kit"
__status__ = "Prototype"

# imports one per line
import pytest
from papers import decide

def test_basic():
    assert decide("test_returning_citizen.json", "watchlist.json", "countries.json") == ["Accept", "Accept"]
    assert decide("test_watchlist.json", "watchlist.json", "countries.json") == ["Secondary"]
    assert decide("test_quarantine.json", "watchlist.json", "countries.json") == ["Quarantine"]

def test_files():
    with pytest.raises(FileNotFoundError):
        decide("test_returning_citizen.json","","")
    with pytest.raises(FileNotFoundError):
        decide("test_returning_citizen.json", "", "countries.json")
    with pytest.raises(FileNotFoundError):
        decide("test_returning_citizen.json", "watchlist.json", "")

    with pytest.raises(FileNotFoundError):
        decide("test_watchlist.json","","")
    with pytest.raises(FileNotFoundError):
        decide("test_watchlist.json", "", "countries.json")
    with pytest.raises(FileNotFoundError):
        decide("test_watchlist.json", "watchlist.json", "")

    with pytest.raises(FileNotFoundError):
        decide("test_quarantine.json","","")
    with pytest.raises(FileNotFoundError):
        decide("test_quarantine.json", "", "countries.json")
    with pytest.raises(FileNotFoundError):
        decide("test_quarantine.json", "watchlist.json", "")


# add functions for other tests
# Add tests to check for incomplete entries
# ex. missing passport, name being blank, missing region in location entry