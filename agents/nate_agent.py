import os 
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
#from langchain_google_genai import ChatGoogleGenerativeAI
import requests
import json
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from datetime import datetime
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=os.getenv("GROQ_API_KEY"),
    reasoning_format="hidden"
)
#nate_llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", api_key=gemini_api_key)

class WeatherToolResponse(BaseModel):
    city: str = Field(..., description="City name")
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: int = Field(..., description="Humidity percentage")
    weather: str = Field(..., description="Weather description")
    time: str = Field(..., description="Current time in the city")
    sunrise: str = Field(..., description="Sunrise time in the city")
    sunset: str = Field(..., description="Sunset time in the city")



@tool
def get_weather_data(lat=28.47192, lon=77.47947)->str:
    """description: Get current weather data for a given latitude and longitude.
    Args:
        lat (float): Latitude of the location. Default is 28.47192.
        lon (float): Longitude of the location. Default is 77.47947.
    Returns:
        JSON string containing current weather information.
    """

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={weather_api_key}"
    
    response = requests.get(url)
    data = response.json()
    
    from datetime import timezone

    # Convert timestamps
    current_time = datetime.fromtimestamp(data["dt"] + data["timezone"], tz=timezone.utc)
    sunrise = datetime.fromtimestamp(data["sys"]["sunrise"] + data["timezone"], tz=timezone.utc)
    sunset = datetime.fromtimestamp(data["sys"]["sunset"] + data["timezone"], tz=timezone.utc)

    return json.dumps({
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "weather": data["weather"][0]["description"],
        "time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "sunrise": sunrise.strftime("%H:%M:%S"),
        "sunset": sunset.strftime("%H:%M:%S")
    })
class NATE:

    NATE_AGENT_SYSTEM_PROMPT = """
    
    You are NATE, a specialized agent designed to provide accurate and up-to-date weather information. 
    Your primary function is to retrieve and present weather data based on user queries.

    """
    def __init__(self):
        self.agent = create_agent(
        model=llm,
        tools=[get_weather_data],
        system_prompt=self.NATE_AGENT_SYSTEM_PROMPT,
        #response_format=WeatherToolResponse
        )

    async def ainvoke(self, query):
        result = await self.agent.ainvoke({
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ]
        })

        return result["messages"][-1].content




