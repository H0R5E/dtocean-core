
import datetime

import pytest

from dtocean_core.core import Core
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import DateTimeData


def test_DateTimeData_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "DateTimeData" in all_objs.keys()


def test_DateTimeData():

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    
    test = DateTimeData()
    
    raw = datetime.datetime.now()
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert isinstance(b, datetime.datetime)
    

def test_DateTimeData_invalid():

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    
    test = DateTimeData()
    
    raw = 1.
    
    with pytest.raises(TypeError):
        test.get_data(raw, meta)
        

def test_get_None():
    
    test = DateTimeData()
    result = test.get_value(None)
    
    assert result is None
