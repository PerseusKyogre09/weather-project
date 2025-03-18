import customtkinter as ctk
import requests
import json
from datetime import datetime
import time
from PIL import Image, ImageTk
import io
import os
from threading import Thread
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather App")
        self.root.geometry("500x800")
        self.root.resizable(False, False)
        
        # Appearance and color
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # API validation
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Please set OPENWEATHER_API_KEY in your .env file.")
        
        # Default (if API incorrect)
        self.temp_unit = "celsius"
        self.city = "London"
        self.weather_data = None
        self.forecast_data = None
        
        # Popular cities list
        self.popular_cities = [
            "London", "New York", "Tokyo", "Paris", "Sydney", 
            "Berlin", "Moscow", "Dubai", "Singapore", "Mumbai"
        ]
        
        self.create_widgets()
        self.fetch_weather()
        
    def create_widgets(self):
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.search_frame = ctk.CTkFrame(self.main_frame)
        self.search_frame.pack(fill="x", padx=10, pady=10)
        
        # City input
        self.city_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Enter city name...")
        self.city_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.city_entry.insert(0, self.city)
        
        # Search button
        self.search_button = ctk.CTkButton(self.search_frame, text="Search", command=self.search_city)
        self.search_button.pack(side="right")
        
        # Popular cities section
        self.popular_cities_frame = ctk.CTkFrame(self.main_frame)
        self.popular_cities_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.popular_label = ctk.CTkLabel(self.popular_cities_frame, text="Popular Cities:")
        self.popular_label.pack(side="left", padx=(10, 0))
        
        # Dropdown (popular cities)
        self.city_dropdown = ctk.CTkOptionMenu(
            self.popular_cities_frame, 
            values=self.popular_cities,
            command=self.select_city
        )
        self.city_dropdown.pack(side="right", padx=(0, 10))
        
        self.weather_frame = ctk.CTkFrame(self.main_frame)
        self.weather_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Error message display
        self.error_label = ctk.CTkLabel(
            self.weather_frame, 
            text="", 
            font=("Arial", 16, "bold"),
            text_color="red"
        )
        self.error_label.pack(pady=(10, 0))

        self.city_label = ctk.CTkLabel(self.weather_frame, text="", font=("Arial", 24, "bold"))
        self.city_label.pack(pady=(20, 0))
        
        # Date
        self.date_label = ctk.CTkLabel(self.weather_frame, text="")
        self.date_label.pack(pady=(5, 10))
        
        # Weather icon
        self.icon_label = ctk.CTkLabel(self.weather_frame, text="")
        self.icon_label.pack(pady=(5, 5))
        
        # Temperature
        self.temp_label = ctk.CTkLabel(self.weather_frame, text="", font=("Arial", 36))
        self.temp_label.pack(pady=(5, 5))
        
        # Weather description
        self.desc_label = ctk.CTkLabel(self.weather_frame, text="")
        self.desc_label.pack(pady=(5, 10))
        
        # Weather details
        self.details_frame = ctk.CTkFrame(self.weather_frame)
        self.details_frame.pack(fill="x", padx=20, pady=10)
        
        # Humidity
        self.humidity_label = ctk.CTkLabel(self.details_frame, text="Humidity: --")
        self.humidity_label.pack(side="left", expand=True)
        
        # Wind speed
        self.wind_label = ctk.CTkLabel(self.details_frame, text="Wind: --")
        self.wind_label.pack(side="right", expand=True)
        
        # Temperature toggle
        self.toggle_frame = ctk.CTkFrame(self.main_frame)
        self.toggle_frame.pack(fill="x", padx=10, pady=10)
        
        self.unit_label = ctk.CTkLabel(self.toggle_frame, text="Temperature Unit:")
        self.unit_label.pack(side="left", padx=(10, 0))
        
        self.unit_switch = ctk.CTkSwitch(self.toggle_frame, text="°F", command=self.toggle_unit)
        self.unit_switch.pack(side="right", padx=(0, 10))
        
        # Forecast section
        self.forecast_label = ctk.CTkLabel(self.main_frame, text="3-Day Forecast", font=("Arial", 18, "bold"))
        self.forecast_label.pack(pady=(10, 0))
        
        self.forecast_frame = ctk.CTkFrame(self.main_frame)
        self.forecast_frame.pack(fill="x", padx=10, pady=10)
        
        self.forecast_days = []
        for i in range(3):
            day_frame = ctk.CTkFrame(self.forecast_frame)
            day_frame.pack(side="left", fill="both", expand=True, padx=5)
            
            day_label = ctk.CTkLabel(day_frame, text="")
            day_label.pack(pady=(5, 0))
            
            icon_label = ctk.CTkLabel(day_frame, text="")
            icon_label.pack(pady=(5, 0))
            
            temp_label = ctk.CTkLabel(day_frame, text="")
            temp_label.pack(pady=(5, 0))
            
            desc_label = ctk.CTkLabel(day_frame, text="")
            desc_label.pack(pady=(5, 5))
            
            self.forecast_days.append({
                "frame": day_frame,
                "day": day_label,
                "icon": icon_label,
                "temp": temp_label,
                "desc": desc_label
            })
        
        # Recent cities
        self.recents_frame = ctk.CTkFrame(self.main_frame)
        self.recents_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        self.recents_label = ctk.CTkLabel(self.recents_frame, text="Recently Viewed:", font=("Arial", 12))
        self.recents_label.pack(side="left", padx=(10, 0))
        
        self.recent_cities_container = ctk.CTkFrame(self.recents_frame, fg_color="transparent")
        self.recent_cities_container.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        # Store recent cities (max 5)
        self.recent_cities = []
        
        # Status
        self.status_frame = ctk.CTkFrame(self.root)
        self.status_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="Ready")
        self.status_label.pack(pady=5)
        
    def search_city(self):
        self.city = self.city_entry.get().strip()
        if self.city:
            self.status_label.configure(text=f"Searching for {self.city}...")
            self.error_label.configure(text="")
            self.fetch_weather()
            self.add_to_recent_cities(self.city)
        else:
            self.status_label.configure(text="Please enter a city name")
    
    def select_city(self, city):
        self.city = city
        self.city_entry.delete(0, "end")
        self.city_entry.insert(0, city)
        self.status_label.configure(text=f"Selected {city}")
        self.error_label.configure(text="")
        self.fetch_weather()
        self.add_to_recent_cities(city)
    
    def add_to_recent_cities(self, city):
        # Duplication avoiding ninja technique brrr
        if city in self.recent_cities:
            self.recent_cities.remove(city)
        self.recent_cities.insert(0, city)
        
        # Last 5 city searched
        self.recent_cities = self.recent_cities[:5]
        self.update_recent_cities_display()
    
    def update_recent_cities_display(self):
        for widget in self.recent_cities_container.winfo_children():
            widget.destroy()
        
        for city in self.recent_cities:
            city_btn = ctk.CTkButton(
                self.recent_cities_container,
                text=city,
                width=70,
                height=25,
                font=("Arial", 10),
                command=lambda c=city: self.select_city(c)
            )
            city_btn.pack(side="left", padx=2)
    
    def fetch_weather(self):
        Thread(target=self._fetch_weather_thread).start()
    
    def _fetch_weather_thread(self):
        try:
            # Get current weather
            weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={self.api_key}&units=metric"
            weather_response = requests.get(weather_url)
            
            # Check if city not found
            if weather_response.status_code == 404:
                self.root.after(0, lambda: self.status_label.configure(text="Failed to fetch weather data"))
                self.root.after(0, lambda: self.error_label.configure(text=f"Error: City '{self.city}' not found"))
                return
            
            weather_response.raise_for_status()
            self.weather_data = weather_response.json()
            
            # Get forecast
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={self.city}&appid={self.api_key}&units=metric"
            forecast_response = requests.get(forecast_url)
            forecast_response.raise_for_status()
            self.forecast_data = forecast_response.json()
            
            # Add to recent cities only if successful
            self.root.after(0, lambda: self.add_to_recent_cities(self.city))
            self.root.after(0, self.update_gui)
            self.root.after(0, lambda: self.status_label.configure(text="Data fetched successfully"))
        except requests.exceptions.HTTPError as e:
            self.root.after(0, lambda: self.status_label.configure(text="Failed to fetch weather data"))
            self.root.after(0, lambda: self.error_label.configure(text=f"Error: {str(e)}"))
        except requests.exceptions.RequestException as e:
            self.root.after(0, lambda: self.status_label.configure(text="Failed to fetch weather data"))
            self.root.after(0, lambda: self.error_label.configure(text=f"Error: {str(e)}"))
    
    def update_gui(self):
        if not self.weather_data:
            return
        
        # Clear any previous error messages
        self.error_label.configure(text="")
        
        # Update weather
        city_name = self.weather_data.get("name", "")
        country = self.weather_data.get("sys", {}).get("country", "")
        self.city_label.configure(text=f"{city_name}, {country}")
        
        # Update date
        timestamp = self.weather_data.get("dt", 0)
        date_str = datetime.fromtimestamp(timestamp).strftime("%A, %d %B %Y")
        self.date_label.configure(text=date_str)
        
        # Update weather icon
        icon_code = self.weather_data.get("weather", [{}])[0].get("icon", "")
        self.load_weather_icon(icon_code, self.icon_label)
        
        # Update temperature
        temp_c = self.weather_data.get("main", {}).get("temp", 0)
        temp_f = self.convert_temperature(temp_c, "fahrenheit")
        
        if self.temp_unit == "celsius":
            self.temp_label.configure(text=f"{temp_c:.1f}°C")
        else:
            self.temp_label.configure(text=f"{temp_f:.1f}°F")
        
        # Update description
        description = self.weather_data.get("weather", [{}])[0].get("description", "").capitalize()
        self.desc_label.configure(text=description)
        
        # Update details
        humidity = self.weather_data.get("main", {}).get("humidity", 0)
        self.humidity_label.configure(text=f"Humidity: {humidity}%")
        
        wind_speed = self.weather_data.get("wind", {}).get("speed", 0)
        self.wind_label.configure(text=f"Wind: {wind_speed} m/s")
        
        # Update forecast
        if self.forecast_data and "list" in self.forecast_data:
            # Get unique dates for forecast
            forecast_dates = set()
            forecasts = []
            
            for forecast in self.forecast_data["list"]:
                date = datetime.fromtimestamp(forecast.get("dt", 0)).strftime("%Y-%m-%d")
                if date not in forecast_dates and date != datetime.now().strftime("%Y-%m-%d"):
                    forecast_dates.add(date)
                    forecasts.append(forecast)
                    if len(forecasts) >= 3:
                        break
            
            # Update forecast days
            for i, forecast in enumerate(forecasts[:3]):
                if i < len(self.forecast_days):
                    day_frame = self.forecast_days[i]
                    
                    # Day of week
                    day_timestamp = forecast.get("dt", 0)
                    day_name = datetime.fromtimestamp(day_timestamp).strftime("%A")
                    day_frame["day"].configure(text=day_name)
                    
                    # Icon
                    icon_code = forecast.get("weather", [{}])[0].get("icon", "")
                    self.load_weather_icon(icon_code, day_frame["icon"])
                    
                    # Temperature
                    temp_c = forecast.get("main", {}).get("temp", 0)
                    temp_f = self.convert_temperature(temp_c, "fahrenheit")
                    
                    if self.temp_unit == "celsius":
                        day_frame["temp"].configure(text=f"{temp_c:.1f}°C")
                    else:
                        day_frame["temp"].configure(text=f"{temp_f:.1f}°F")
                    
                    # Description
                    description = forecast.get("weather", [{}])[0].get("description", "").capitalize()
                    day_frame["desc"].configure(text=description)
    
    def load_weather_icon(self, icon_code, label):
        try:
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
            icon_response = requests.get(icon_url)
            icon_response.raise_for_status()
            
            icon_image = Image.open(io.BytesIO(icon_response.content))
            icon_photo = ImageTk.PhotoImage(icon_image)
            label.image = icon_photo
            label.configure(image=icon_photo, text="")
        except Exception as e:
            label.configure(text=f"Icon\nError", image="")
    
    def toggle_unit(self):
        if self.unit_switch.get() == 1:
            self.temp_unit = "fahrenheit"
        else:
            self.temp_unit = "celsius"
        
        self.update_gui()
    
    def convert_temperature(self, temp, unit):
        if unit == "fahrenheit":
            return (temp * 9/5) + 32
        else:
            return temp

if __name__ == "__main__":
    root = ctk.CTk()
    app = WeatherApp(root)
    root.mainloop()