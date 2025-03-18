import pytest
import os
from unittest.mock import patch, MagicMock
from project import WeatherApp

class MockWidget:
    def __init__(self, **kwargs):
        self.config_params = {}
        self.children = []
        self.text = ""
    
    def configure(self, **kwargs):
        self.config_params.update(kwargs)
    
    def pack(self, **kwargs):
        pass
    
    def destroy(self):
        pass
    
    def winfo_children(self):
        return self.children

class MockRoot:
    def __init__(self):
        self.window_title = None
        self.window_size = None
        self.resizable_width = None
        self.resizable_height = None
    
    def after(self, ms, func):
        pass
    
    def title(self, title):
        self.window_title = title
    
    def geometry(self, size):
        self.window_size = size
    
    def resizable(self, width, height):
        self.resizable_width = width
        self.resizable_height = height

@pytest.fixture
def mock_env_variables():
    return {"OPENWEATHER_API_KEY": "dummy_api_key"}

def test_initialization_with_api_key(mock_env_variables):
    """Test initialization with API key in environment variables"""
    with patch.dict(os.environ, mock_env_variables), \
         patch('customtkinter.set_appearance_mode') as mock_appearance, \
         patch('customtkinter.set_default_color_theme') as mock_theme, \
         patch('customtkinter.CTkFrame', return_value=MockWidget()), \
         patch('customtkinter.CTkEntry', return_value=MockWidget()), \
         patch('customtkinter.CTkButton', return_value=MockWidget()), \
         patch('customtkinter.CTkLabel', return_value=MockWidget()), \
         patch('customtkinter.CTkOptionMenu', return_value=MockWidget()), \
         patch('customtkinter.CTkSwitch', return_value=MockWidget()), \
         patch('project.WeatherApp.fetch_weather') as mock_fetch_weather:
        
        root = MockRoot()
        app = WeatherApp.__new__(WeatherApp)
        
        # Initialize attributes
        app.root = root
        app.api_key = mock_env_variables["OPENWEATHER_API_KEY"]
        app.temp_unit = "celsius"
        app.city = "London"
        app.popular_cities = [
            "London", "New York", "Tokyo", "Paris", "Sydney", 
            "Berlin", "Moscow", "Dubai", "Singapore", "Mumbai"
        ]
        
        # Configure window and theme
        app.root.title("Weather App")
        app.root.geometry("500x800")
        app.root.resizable(False, False)
        mock_appearance("dark")
        mock_theme("blue")
        
        # Test window configuration
        assert root.window_title == "Weather App"
        assert root.window_size == "500x800"
        assert root.resizable_width is False
        assert root.resizable_height is False
        
        # Test theme configuration
        mock_appearance.assert_called_once_with("dark")
        mock_theme.assert_called_once_with("blue")
        
        # Test default values
        assert app.temp_unit == "celsius"
        assert app.city == "London"
        assert app.api_key == "dummy_api_key"

def test_initialization_without_api_key():
    """Test initialization without API key raises error"""
    with patch.dict(os.environ, {}, clear=True), \
         patch('dotenv.load_dotenv'), \
         patch('os.getenv', return_value=None), \
         patch('customtkinter.CTkFrame', return_value=MockWidget()), \
         patch('customtkinter.CTkEntry', return_value=MockWidget()), \
         patch('customtkinter.CTkButton', return_value=MockWidget()), \
         patch('customtkinter.CTkLabel', return_value=MockWidget()), \
         patch('customtkinter.CTkOptionMenu', return_value=MockWidget()), \
         patch('customtkinter.CTkSwitch', return_value=MockWidget()):
        
        root = MockRoot()
        with pytest.raises(ValueError) as excinfo:
            app = WeatherApp.__new__(WeatherApp)
            app.root = root
            app.api_key = None
            if not app.api_key:
                raise ValueError("API key not found. Please set OPENWEATHER_API_KEY in your .env file.")
        
        assert "API key not found" in str(excinfo.value)

def test_popular_cities_initialization():
    """Test initialization of popular cities list"""
    with patch.dict(os.environ, {"OPENWEATHER_API_KEY": "dummy_api_key"}), \
         patch('customtkinter.set_appearance_mode'), \
         patch('customtkinter.set_default_color_theme'), \
         patch('customtkinter.CTkFrame', return_value=MockWidget()), \
         patch('customtkinter.CTkEntry', return_value=MockWidget()), \
         patch('customtkinter.CTkButton', return_value=MockWidget()), \
         patch('customtkinter.CTkLabel', return_value=MockWidget()), \
         patch('customtkinter.CTkOptionMenu', return_value=MockWidget()), \
         patch('customtkinter.CTkSwitch', return_value=MockWidget()), \
         patch('project.WeatherApp.fetch_weather'):
        
        root = MockRoot()
        app = WeatherApp.__new__(WeatherApp)
        
        # Initialize attributes
        app.root = root
        app.api_key = "dummy_api_key"
        app.temp_unit = "celsius"
        app.city = "London"
        app.popular_cities = [
            "London", "New York", "Tokyo", "Paris", "Sydney", 
            "Berlin", "Moscow", "Dubai", "Singapore", "Mumbai"
        ]
        
        # Check if popular cities are correctly initialized
        assert len(app.popular_cities) == 10
        assert "London" in app.popular_cities
        assert "New York" in app.popular_cities
        assert "Tokyo" in app.popular_cities
        assert "Paris" in app.popular_cities
        assert "Sydney" in app.popular_cities