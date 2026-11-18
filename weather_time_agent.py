from datetime import datetime
from zoneinfo import ZoneInfo
from agent_core import run_agent

CITY_TIMEZONES = {
    "delhi": "Asia/Kolkata",
    "kanpur": "Asia/Kolkata",
    "london": "Europe/London",
    "new york": "America/New_York",
    "tokyo": "Asia/Tokyo",
}

SAMPLE_WEATHER = {
    "delhi": (31, "Sunny"),
    "kanpur": (29, "Hazy"),
    "london": (12, "Light rain"),
    "new york": (8, "Cloudy"),
    "tokyo": (16, "Clear"),
}

def get_time(city):
    if city not in CITY_TIMEZONES:
        raise ValueError(f"I do not know the city {city}")
    now = datetime.now(ZoneInfo(CITY_TIMEZONES[city]))
    return f"{city.title()} time: {now.strftime('%I:%M %p')}"

def get_weather(city):
    if city not in SAMPLE_WEATHER:
        raise ValueError(f"I have no weather for {city}")
    temp, sky = SAMPLE_WEATHER[city]
    return f"{city.title()} weather: {temp} C, {sky} (sample data)"

TOOLS = {"get_time": get_time, "get_weather": get_weather}

def find_city(text):
    for city in CITY_TIMEZONES:
        if city in text.lower():
            return city
    return None

def weather_time_brain(goal, history):
    city = find_city(goal)
    if city is None:
        known = ", ".join(CITY_TIMEZONES)
        return {"action": "finish", "answer": f"Which city do you mean? I know: {known}"}

    wanted = []
    if "time" in goal.lower():
        wanted.append("get_time")
    if "weather" in goal.lower():
        wanted.append("get_weather")
    if not wanted:
        return {"action": "finish", "answer": "Ask me about the time or the weather."}

    done = [step["action"] for step in history]
    for tool_name in wanted:
        if tool_name not in done:
            return {"action": tool_name, "input": {"city": city}}

    answer = " | ".join(str(step["result"]) for step in history)
    return {"action": "finish", "answer": answer}

if __name__ == "__main__":
    questions = [
        "What is the time and weather in Delhi?",
        "Weather in Tokyo",
        "What time is it in Paris?",
    ]
    for question in questions:
        print("\nQuestion:", question)
        print("Final answer:", run_agent(question, weather_time_brain, TOOLS))
