import httpx
import os
from dotenv import load_dotenv

load_dotenv()

class WeatherPlugin:
    """Real weather data using OpenWeatherMap (Free)"""

    name = "Weather"
    slug = "weather"
    API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    BASE_URL = "https://api.openweathermap.org/data/2.5"

    @classmethod
    def get_weather(cls, city: str) -> dict:
        """Get current weather for a city"""

        if not cls.API_KEY:
            return {
                "success": False,
                "error": "OpenWeather API key not configured"
            }

        try:
            print(f"🌤️ Getting weather for: {city}")

            with httpx.Client(timeout=10) as client:
                response = client.get(
                    f"{cls.BASE_URL}/weather",
                    params={
                        "q": city,
                        "appid": cls.API_KEY,
                        "units": "metric",
                    }
                )

                if response.status_code == 200:
                    data = response.json()

                    weather = {
                        "success": True,
                        "city": data["name"],
                        "country": data["sys"]["country"],
                        "temperature": round(data["main"]["temp"]),
                        "feels_like": round(data["main"]["feels_like"]),
                        "humidity": data["main"]["humidity"],
                        "description": data["weather"][0]["description"].title(),
                        "icon": cls._get_icon(data["weather"][0]["main"]),
                        "wind_speed": data["wind"]["speed"],
                        "visibility": data.get("visibility", 0) // 1000,
                        "min_temp": round(data["main"]["temp_min"]),
                        "max_temp": round(data["main"]["temp_max"]),
                    }

                    print(f"✅ Weather: {weather['city']} {weather['temperature']}°C")
                    return weather

                elif response.status_code == 404:
                    return {
                        "success": False,
                        "error": f"City '{city}' not found"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}"
                    }

        except Exception as e:
            print(f"❌ Weather error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    @classmethod
    def get_forecast(cls, city: str, days: int = 3) -> dict:
        """Get weather forecast"""

        if not cls.API_KEY:
            return {
                "success": False,
                "error": "OpenWeather API key not configured"
            }

        try:
            with httpx.Client(timeout=10) as client:
                response = client.get(
                    f"{cls.BASE_URL}/forecast",
                    params={
                        "q": city,
                        "appid": cls.API_KEY,
                        "units": "metric",
                        "cnt": days * 8,
                    }
                )

                if response.status_code == 200:
                    data = response.json()

                    # Group by day
                    daily = {}
                    for item in data["list"]:
                        date = item["dt_txt"].split(" ")[0]
                        if date not in daily:
                            daily[date] = {
                                "date": date,
                                "temps": [],
                                "description": item["weather"][0]["description"].title(),
                                "icon": cls._get_icon(item["weather"][0]["main"]),
                            }
                        daily[date]["temps"].append(item["main"]["temp"])

                    forecast = []
                    for date, info in list(daily.items())[:days]:
                        forecast.append({
                            "date": date,
                            "min_temp": round(min(info["temps"])),
                            "max_temp": round(max(info["temps"])),
                            "description": info["description"],
                            "icon": info["icon"],
                        })

                    return {
                        "success": True,
                        "city": data["city"]["name"],
                        "forecast": forecast
                    }

                else:
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}"
                    }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def _get_icon(condition: str) -> str:
        icons = {
            "Clear": "☀️",
            "Clouds": "☁️",
            "Rain": "🌧️",
            "Drizzle": "🌦️",
            "Thunderstorm": "⛈️",
            "Snow": "❄️",
            "Mist": "🌫️",
            "Fog": "🌫️",
            "Haze": "🌫️",
            "Smoke": "🌫️",
            "Dust": "🌫️",
            "Sand": "🌫️",
            "Ash": "🌫️",
            "Squall": "💨",
            "Tornado": "🌪️",
        }
        return icons.get(condition, "🌡️")