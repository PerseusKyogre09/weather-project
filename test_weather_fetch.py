import pytest
from unittest.mock import patch, MagicMock
from project import WeatherApp
import requests

class MockResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
        self.content = b""
    
    def json(self):
        return self.json_data
    
    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.exceptions.HTTPError(f"HTTP Error: {self.status_code}")

class MockRoot:
    def __init__(self):
        self.functions = []
    
    def after(self, ms, func):
        self.functions.append(func)
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
    with patch('os.getenv', return_value='dummy_api_key'):
        root = MockRoot()
        app = WeatherApp.__new__(WeatherApp)
        
        # Set minimum attributes needed for testing
        app.root = root
        app.api_key = "dummy_api_key"
        app.city = "London"
        app.temp_unit = "celsius"
        app.weather_data = None
        app.forecast_data = None
        app.status_label = MagicMock()
        app.error_label = MagicMock()
        app.update_gui = MagicMock()
        app.recent_cities = []
        app.add_to_recent_cities = MagicMock()
        
        return app

@pytest.mark.parametrize("exception,expected_message", [
    (requests.exceptions.ConnectionError("No connection"), "Error: No connection"),
    (requests.exceptions.Timeout("Request timed out"), "Error: Request timed out"),
    (requests.exceptions.HTTPError("404 Client Error"), "Error: 404 Client Error"),
])
def test_fetch_weather_error_handling(weather_app, exception, expected_message):
    """Test error handling in fetch weather"""
    with patch('requests.get', side_effect=exception):
        weather_app._fetch_weather_thread()
        
        weather_app.status_label.configure.assert_called_with(text="Failed to fetch weather data")
        weather_app.error_label.configure.assert_called_with(text=expected_message)
        assert weather_app.update_gui.call_count == 0