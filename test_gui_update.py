import pytest
from unittest.mock import patch, MagicMock
from project import WeatherApp
from datetime import datetime

class MockLabel:
    def __init__(self):
        self.text = ""
        self.image = None
    
    def configure(self, text=None, image=None):
        if text is not None:
            self.text = text
        if image is not None:
            self.image = image

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
def mock_weather_data():
    return {
        "name": "London",
        "sys": {"country": "GB"},
        "dt": 1611234567,
        "weather": [{"icon": "01d", "description": "clear sky"}],
        "main": {"temp": 15.5, "humidity": 76},
        "wind": {"speed": 3.6}
    }

@pytest.fixture
def mock_forecast_data():
    return {
        "list": [
            {
                "dt": 1611234567 + 86400,
                "weather": [{"icon": "01d", "description": "clear sky"}],
                "main": {"temp": 16.2}
            },
            {
                "dt": 1611234567 + 172800,
                "weather": [{"icon": "02d", "description": "partly cloudy"}],
                "main": {"temp": 17.1}
            },
            {
                "dt": 1611234567 + 259200,
                "weather": [{"icon": "10d", "description": "light rain"}],
                "main": {"temp": 14.8}
            }
        ]
    }

@pytest.fixture
def weather_app():
    with patch('os.getenv', return_value='dummy_api_key'):
        root = MockRoot()
        app = WeatherApp.__new__(WeatherApp)
        
        app.root = root
        app.api_key = "dummy_api_key"
        app.city = "London"
        app.temp_unit = "celsius"
        app.weather_data = None
        app.forecast_data = None
        app.status_label = MockLabel()
        app.error_label = MockLabel()
        app.load_weather_icon = MagicMock()
        
        app.city_label = MockLabel()
        app.date_label = MockLabel()
        app.icon_label = MockLabel()
        app.temp_label = MockLabel()
        app.desc_label = MockLabel()
        app.humidity_label = MockLabel()
        app.wind_label = MockLabel()
        
        app.forecast_days = []
        for _ in range(3):
            day = {
                "day": MockLabel(),
                "icon": MockLabel(),
                "temp": MockLabel(),
                "desc": MockLabel()
            }
            app.forecast_days.append(day)
        
        def update_gui():
            if not app.weather_data:
                return
            
            app.city_label.configure(text=f"{app.weather_data['name']}, {app.weather_data['sys']['country']}")
            
            temp = app.weather_data['main']['temp']
            if app.temp_unit == "fahrenheit":
                temp = round((temp * 9/5) + 32, 1)
                app.temp_label.configure(text=f"{temp}°F")
            else:
                app.temp_label.configure(text=f"{temp}°C")
            
            desc = app.weather_data['weather'][0]['description'].title()
            app.desc_label.configure(text=desc)
            app.humidity_label.configure(text=f"Humidity: {app.weather_data['main']['humidity']}%")
            app.wind_label.configure(text=f"Wind: {app.weather_data['wind']['speed']} m/s")
            
            icon_code = app.weather_data['weather'][0]['icon']
            app.load_weather_icon(icon_code, app.icon_label)
            
            if app.forecast_data and 'list' in app.forecast_data:
                for i, day in enumerate(app.forecast_days):
                    forecast = app.forecast_data['list'][i]
                    temp = forecast['main']['temp']
                    if app.temp_unit == "fahrenheit":
                        temp = round((temp * 9/5) + 32, 1)
                        day['temp'].configure(text=f"{temp}°F")
                    else:
                        day['temp'].configure(text=f"{temp}°C")
        
        app.update_gui = update_gui
        
        return app

def test_update_gui_no_data(weather_app):
    weather_app.weather_data = None
    weather_app.update_gui()
    
    assert weather_app.city_label.text == ""
    assert weather_app.temp_label.text == ""
    assert weather_app.desc_label.text == ""
    assert weather_app.humidity_label.text == ""
    assert weather_app.wind_label.text == ""
    weather_app.load_weather_icon.assert_not_called()

def test_update_gui_celsius(weather_app, mock_weather_data, mock_forecast_data):
    """Test update_gui with celsius temperature unit"""
    weather_app.weather_data = mock_weather_data
    weather_app.forecast_data = mock_forecast_data
    weather_app.temp_unit = "celsius"
    
    timestamp_date = datetime(2021, 1, 21)
    with patch('project.datetime') as mock_datetime:
        mock_datetime.fromtimestamp.return_value = timestamp_date
        mock_datetime.now.return_value = timestamp_date
        mock_datetime.strftime = datetime.strftime
        
        weather_app.update_gui()
    
    assert weather_app.city_label.text == "London, GB"
    assert "15.5°C" in weather_app.temp_label.text
    assert weather_app.desc_label.text == "Clear Sky"
    assert weather_app.humidity_label.text == "Humidity: 76%"
    assert weather_app.wind_label.text == "Wind: 3.6 m/s"
    
    weather_app.load_weather_icon.assert_called_with("01d", weather_app.icon_label)
    
    for i, day in enumerate(weather_app.forecast_days):
        temp = mock_forecast_data["list"][i]["main"]["temp"]
        assert f"{temp}°C" in day["temp"].text

def test_update_gui_fahrenheit(weather_app, mock_weather_data, mock_forecast_data):
    """Test update_gui with fahrenheit temperature unit"""
    weather_app.weather_data = mock_weather_data
    weather_app.forecast_data = mock_forecast_data
    weather_app.temp_unit = "fahrenheit"
    
    timestamp_date = datetime(2021, 1, 21)
    with patch('project.datetime') as mock_datetime:
        mock_datetime.fromtimestamp.return_value = timestamp_date
        mock_datetime.now.return_value = timestamp_date
        mock_datetime.strftime = datetime.strftime
        
        weather_app.update_gui()
    
    assert "59.9°F" in weather_app.temp_label.text
    
    for i, day in enumerate(weather_app.forecast_days):
        temp = mock_forecast_data["list"][i]["main"]["temp"]
        fahrenheit = round((temp * 9/5) + 32, 1)
        assert f"{fahrenheit}°F" in day["temp"].text