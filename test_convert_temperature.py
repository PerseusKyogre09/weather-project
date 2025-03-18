import pytest
from project import WeatherApp

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
    WeatherApp.__init__ = lambda self, root: setattr(self, 'root', root) or setattr(self, 'temp_unit', 'celsius')
    app = WeatherApp(root)
    return app

def test_convert_temperature_to_fahrenheit(weather_app):
    """Test temperature conversion from Celsius to Fahrenheit"""
    assert weather_app.convert_temperature(0, "fahrenheit") == 32.0
    assert weather_app.convert_temperature(100, "fahrenheit") == 212.0
    assert weather_app.convert_temperature(-40, "fahrenheit") == -40.0
    assert weather_app.convert_temperature(25, "fahrenheit") == 77.0
    assert round(weather_app.convert_temperature(37.5, "fahrenheit"), 1) == 99.5

def test_convert_temperature_to_celsius(weather_app):
    """Test temperature conversion from Fahrenheit to Celsius (identity function)"""
    assert weather_app.convert_temperature(15, "celsius") == 15
    assert weather_app.convert_temperature(0, "celsius") == 0
    assert weather_app.convert_temperature(-10, "celsius") == -10