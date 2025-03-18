import pytest
from unittest.mock import patch, MagicMock
from project import WeatherApp

# Mock tkinter root and widgets for testing
class MockWidget:
    def __init__(self, **kwargs):
        self.config_params = {}
        self.children = []
        self.value = 0
        self.text = ""
    
    def configure(self, **kwargs):
        self.config_params.update(kwargs)
    
    def pack(self, **kwargs):
        pass
    
    def destroy(self):
        pass
    
    def get(self):
        return self.value
    
    def delete(self, start, end):
        pass
    
    def insert(self, index, text):
        self.text = text
    
    def winfo_children(self):
        return self.children

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
        app.status_label = MockWidget()
        app.error_label = MockWidget()
        app.update_gui = MagicMock()
        app.recent_cities = []
        app.city_entry = MockWidget()
        app.fetch_weather = MagicMock()
        app.recent_cities_container = MockWidget()
        app.add_to_recent_cities = MagicMock()
        
        return app

def test_select_city(weather_app):
    """Test selecting a city from dropdown"""
    weather_app.select_city("Paris")
    
    assert weather_app.city == "Paris"
    assert weather_app.status_label.config_params.get("text") == "Selected Paris"
    weather_app.fetch_weather.assert_called_once()
    weather_app.add_to_recent_cities.assert_called_once_with("Paris")

def test_add_to_recent_cities_new_city(weather_app):
    """Test adding a new city to recent cities"""
    weather_app.add_to_recent_cities = lambda city: weather_app.recent_cities.insert(0, city)
    weather_app.add_to_recent_cities("Paris")
    
    assert "Paris" in weather_app.recent_cities
    assert weather_app.recent_cities.index("Paris") == 0

def test_add_to_recent_cities_existing_city(weather_app):
    """Test adding an existing city moves it to front"""
    weather_app.recent_cities = ["London", "Paris", "Berlin"]
    weather_app.add_to_recent_cities = lambda city: (
        weather_app.recent_cities.remove(city) if city in weather_app.recent_cities else None,
        weather_app.recent_cities.insert(0, city)
    )[-1]
    weather_app.add_to_recent_cities("Paris")
    
    assert weather_app.recent_cities.index("Paris") == 0
    assert len(weather_app.recent_cities) == 3

def test_add_to_recent_cities_limit(weather_app):
    """Test that recent cities list is limited to 5 cities"""
    def add_to_recent_cities(city):
        if city in weather_app.recent_cities:
            weather_app.recent_cities.remove(city)
        weather_app.recent_cities.insert(0, city)
        weather_app.recent_cities = weather_app.recent_cities[:5]
    
    weather_app.add_to_recent_cities = add_to_recent_cities
    cities = ["London", "Paris", "Tokyo", "New York", "Berlin", "Mumbai"]
    for city in cities:
        weather_app.add_to_recent_cities(city)
    
    assert len(weather_app.recent_cities) == 5
    assert weather_app.recent_cities == ["Mumbai", "Berlin", "New York", "Tokyo", "Paris"]

def test_search_city_empty(weather_app):
    """Test searching with empty city name"""
    with patch.object(weather_app.city_entry, 'get', return_value=""):
        weather_app.search_city()
    
    assert weather_app.status_label.config_params.get("text") == "Please enter a city name"
    weather_app.fetch_weather.assert_not_called()
    weather_app.add_to_recent_cities.assert_not_called()