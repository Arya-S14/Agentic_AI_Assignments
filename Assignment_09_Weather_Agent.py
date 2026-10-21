"""
Weather Agent (LangChain + Open-Meteo, free, NO API key needed)

Install:  pip install langchain-core requests matplotlib
Run:      python weather_agent.py                    (interactive prompt)
          python weather_agent.py Kolhapur           (one-shot)
          python weather_agent.py Pune --plot        (also shows 7-day chart)
          python weather_agent.py Pune --fahrenheit  (use °F / mph)
"""

import argparse
import re
import sys

import requests
from langchain_core.runnables import RunnableLambda
from langchain_core.tools import tool

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT = 10  # seconds

# WMO weather codes -> readable text
WMO = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime fog", 51: "Light drizzle", 53: "Drizzle",
    55: "Dense drizzle", 56: "Freezing drizzle", 57: "Heavy freezing drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain", 66: "Freezing rain",
    67: "Heavy freezing rain", 71: "Light snow", 73: "Snow", 75: "Heavy snow",
    77: "Snow grains", 80: "Light showers", 81: "Showers", 82: "Violent showers",
    85: "Snow showers", 86: "Heavy snow showers", 95: "Thunderstorm",
    96: "Thunderstorm with hail", 99: "Severe thunderstorm with hail",
}


class WeatherError(Exception):
    """Friendly, user-facing error."""


# ---------------------------------------------------------------------------
# LangChain TOOLS
# ---------------------------------------------------------------------------
@tool
def get_coordinates(city: str) -> dict:
    """Look up latitude/longitude for a city name."""
    try:
        r = requests.get(GEOCODE_URL, params={"name": city, "count": 1}, timeout=TIMEOUT)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise WeatherError(f"Could not reach the geocoding service: {e}")
    results = r.json().get("results")
    if not results:
        raise WeatherError(f"City '{city}' not found. Check the spelling.")
    p = results[0]
    return {
        "name": p["name"],
        "country": p.get("country", ""),
        "admin": p.get("admin1", ""),
        "lat": p["latitude"],
        "lon": p["longitude"],
    }


@tool
def get_weather(lat: float, lon: float, fahrenheit: bool = False) -> dict:
    """Fetch current weather and a 7-day forecast for coordinates."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,"
                   "precipitation,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto",
        "forecast_days": 7,
    }
    if fahrenheit:
        params["temperature_unit"] = "fahrenheit"
        params["wind_speed_unit"] = "mph"
    try:
        r = requests.get(FORECAST_URL, params=params, timeout=TIMEOUT)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise WeatherError(f"Could not reach the weather service: {e}")
    return r.json()


# ---------------------------------------------------------------------------
# CHAIN STEPS
# ---------------------------------------------------------------------------
def parse_city(text: str) -> dict:
    """'what's the weather in Pune?' -> {'city': 'Pune'}"""
    text = text.strip().rstrip("?.! ")
    m = re.search(r"\b(?:in|for|at)\s+(.+)$", text, flags=re.I)
    city = m.group(1) if m else re.sub(r"^(weather|forecast)\s*", "", text, flags=re.I)
    city = city.strip()
    if not city:
        raise WeatherError("Please give a city name, e.g. 'weather in Pune'.")
    return {"city": city}


def locate(state: dict) -> dict:
    state["place"] = get_coordinates.invoke({"city": state["city"]})
    return state


def fetch(state: dict) -> dict:
    p = state["place"]
    state["data"] = get_weather.invoke(
        {"lat": p["lat"], "lon": p["lon"], "fahrenheit": state.get("fahrenheit", False)}
    )
    return state


def build_report(state: dict) -> dict:
    d, p = state["data"], state["place"]
    cu, cur = d["current_units"], d["current"]
    du, daily = d["daily_units"], d["daily"]

    where = ", ".join(x for x in (p["name"], p["admin"], p["country"]) if x)
    lines = [
        "=" * 56,
        f"WEATHER REPORT: {where}",
        f"Time: {cur['time'].replace('T', ' ')} ({d.get('timezone', '')})",
        "=" * 56,
        f"Condition   : {WMO.get(cur['weather_code'], 'Unknown')}",
        f"Temperature : {cur['temperature_2m']}{cu['temperature_2m']} "
        f"(feels like {cur['apparent_temperature']}{cu['apparent_temperature']})",
        f"Humidity    : {cur['relative_humidity_2m']}{cu['relative_humidity_2m']}",
        f"Wind        : {cur['wind_speed_10m']} {cu['wind_speed_10m']}",
        f"Precip.     : {cur['precipitation']} {cu['precipitation']}",
        "",
        "7-day forecast:",
    ]
    for i, day in enumerate(daily["time"]):
        lines.append(
            f"  {day}  {daily['temperature_2m_min'][i]:>5}{du['temperature_2m_min']} to "
            f"{daily['temperature_2m_max'][i]:>5}{du['temperature_2m_max']}  "
            f"rain {daily['precipitation_sum'][i]:>5}{du['precipitation_sum']}  "
            f"{WMO.get(daily['weather_code'][i], 'Unknown')}"
        )
    state["report"] = "\n".join(lines)
    return state


def ask(text: str, fahrenheit: bool = False) -> dict:
    """Run the agent. Returns the final state dict (with 'report')."""
    chain = (
        RunnableLambda(parse_city)
        | RunnableLambda(lambda s: {**s, "fahrenheit": fahrenheit})
        | RunnableLambda(locate)
        | RunnableLambda(fetch)
        | RunnableLambda(build_report)
    )
    return chain.invoke(text)


def plot_forecast(state: dict) -> None:
    import matplotlib.pyplot as plt

    d = state["data"]["daily"]
    unit = state["data"]["daily_units"]["temperature_2m_max"]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(d["time"], d["temperature_2m_max"], "o-", color="#E45756", label="Max")
    ax.plot(d["time"], d["temperature_2m_min"], "o-", color="#4C78A8", label="Min")
    ax.set_ylabel(f"Temperature ({unit})")
    ax.set_title(f"7-day forecast: {state['place']['name']}")
    ax.grid(alpha=0.3)
    ax.legend()
    ax2 = ax.twinx()
    ax2.bar(d["time"], d["precipitation_sum"], alpha=0.25, color="#54A24B")
    ax2.set_ylabel("Rain (mm)")
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.show()


def main():
    ap = argparse.ArgumentParser(description="Weather agent (Open-Meteo)")
    ap.add_argument("city", nargs="*", help="city name or question")
    ap.add_argument("--plot", action="store_true", help="show 7-day chart")
    ap.add_argument("--fahrenheit", action="store_true", help="use °F and mph")
    args = ap.parse_args()

    def handle(text):
        try:
            state = ask(text, args.fahrenheit)
        except WeatherError as e:
            print(f"\n[!] {e}")
            return
        print("\n" + state["report"])
        if args.plot:
            plot_forecast(state)

    if args.city:
        handle(" ".join(args.city))
        return

    print("Weather agent. Ask e.g. 'weather in Pune'. Type 'quit' to exit.")
    while True:
        try:
            text = input("\nYou > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if text.lower() in {"quit", "exit", "q"}:
            break
        if text:
            handle(text)


if __name__ == "__main__":
    sys.exit(main())