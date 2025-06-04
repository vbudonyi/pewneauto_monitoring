import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pytest
from app import clean_data
from config import URL


def test_nbsp_replacement_and_whitespace_trimming():
    data = {
        'name': ' Test\xa0Car ',
        'link': 'http://example.com '
    }
    cleaned = clean_data(data)
    assert cleaned['name'] == 'Test Car'
    assert cleaned['link'] == 'http://example.com'


def test_relative_link_prefixed_with_url():
    data = {
        'name': 'Car',
        'link': '/cars/1 '
    }
    cleaned = clean_data(data)
    assert cleaned['link'] == URL + '/cars/1'

