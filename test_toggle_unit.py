import pytest
from unittest.mock import patch, MagicMock
from project import WeatherApp

class MockSwitch:
    def __init__(self):
        self._value = 0
    
    def get(self):
        return self._value
    
    def set(self, value):
        self._value = value

class MockRoot:
    def after(self, ms, func):
        if callable(func):
            func()
    
    def title(self, title):
        pass
    
    def geometry(self, size):
        pass
    
    def resizable(self, width, height):
        pass

@pytest.fixture
def weather_app():
    root = MockRoot()
    
    # Minimal initialization for testing toggle_unit
    app = WeatherApp.__new__(WeatherApp)
    app.root = root
    app.temp_unit = "celsius"
    app.unit_switch = MockSwitch()
    app.update_gui = MagicMock()
    
    return app

def test_toggle_unit_to_fahrenheit(weather_app):
    """Test toggling temperature unit to fahrenheit"""
    weather_app.temp_unit = "celsius"
    weather_app.unit_switch.set(1)  # ON position
    
    weather_app.toggle_unit()
    
    assert weather_app.temp_unit == "fahrenheit"
    weather_app.update_gui.assert_called_once()

def test_toggle_unit_to_celsius(weather_app):
    """Test toggling temperature unit to celsius"""
    weather_app.temp_unit = "fahrenheit"
    weather_app.unit_switch.set(0)  # OFF position
    
    weather_app.toggle_unit()
    
    assert weather_app.temp_unit == "celsius"
    weather_app.update_gui.assert_called_once()

def test_toggle_unit_no_change_celsius(weather_app):
    """Test toggle doesn't change when already in celsius and switch is off"""
    weather_app.temp_unit = "celsius"
    weather_app.unit_switch.set(0)  # OFF position
    
    weather_app.toggle_unit()
    
    assert weather_app.temp_unit == "celsius"
    weather_app.update_gui.assert_called_once()

def test_toggle_unit_no_change_fahrenheit(weather_app):
    """Test toggle doesn't change when already in fahrenheit and switch is on"""
    weather_app.temp_unit = "fahrenheit"
    weather_app.unit_switch.set(1)  # ON position
    
    weather_app.toggle_unit()
    
    assert weather_app.temp_unit == "fahrenheit"
    weather_app.update_gui.assert_called_once()