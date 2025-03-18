# Weather Application
#### Video Demo:  <URL HERE>
#### Description:

This is my final project for CS50P (Programming with Python), where I created a weather application that demonstrates my understanding of Python programming concepts, GUI development, API integration, and software testing.

I developed this weather application as a way to combine my interest in Custom Tkinter (as it's quite new and similar to Tkinter). The project uses Python and CustomTkinter to create a modern, intuitive interface that makes weather information easily accessible.

## Project Directory Structure
```
weather-project/
├── project.py              # Main application file
├── .env                    # Environment variables (API key)
├── requirements.txt        # Project dependencies
└── tests/
    ├── test_weather_fetch.py
    ├── test_city_operations.py
    ├── test_gui_update.py
    └── test_initialization.py
```

## How It Works

The application starts by initializing a clean, modern interface with a search bar at the top. Users can either type a city name and press `Enter` or click the search button to fetch weather data. The app uses the OpenWeather API to retrieve real-time weather information and 3-day forecasts. I chose to limit the forecast to 3 days to keep the interface clean and focused, and also due to API limitations.

When a city is searched, the application:
1. Makes an API call to OpenWeather to fetch current weather data
2. Retrieves forecast data for the next 3 days
3. Updates the GUI with temperature, weather description, humidity, and wind speed
4. Automatically adds the city to the recent cities list (limited to 5 cities)
5. Displays weather icons and descriptions for both current and forecast conditions

## Design Decisions and Challenges

One of the biggest challenges I faced was handling API errors gracefully. I implemented comprehensive error handling to ensure users always get meaningful feedback when something goes wrong. For example, if the API call fails, the application displays a clear error message instead of crashing.

I chose CustomTkinter over traditional Tkinter because it provides modern, customizable widgets that make the application look professional. The built-in theme support also made it easier to implement dark/light mode switching.

The recent cities feature was a personal addition I made after realizing how often users check the same cities repeatedly. I limited it to 5 cities to maintain a clean interface while still providing useful quick access.

## API Integration

The application uses the OpenWeather API, which I chose for its reliability and comprehensive weather data. Users need to:
1. Sign up for a free API key at OpenWeather
2. Create a `.env` file in the project directory
3. Add their API key as `OPENWEATHER_API_KEY=your_key_here`

## Test Cases

I implemented comprehensive testing using pytest to ensure the application works reliably. The test suite covers:
- Weather data fetching and error handling
- City operations and history management
- GUI updates and temperature conversions
- Application initialization and configuration

Tests can be run using:
```bash
pytest -v
```

This project represents my journey in creating a practical, user-friendly weather application. I focused on making it both functional and aesthetically pleasing while ensuring it's reliable and easy to use.