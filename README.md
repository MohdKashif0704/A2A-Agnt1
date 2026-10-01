# A2A-Agnt1
Demostrate A2A protocol

# A2A Agent Project

## Project Structure

```text
A2A-Agnt1/
├── agents/
│   ├── host/
│   │   ├── host.py
│   │   └── remote_agent_connection.py
│   │
│   └── server/
│       ├── nate_agent.py
│       ├── nate_agent_executor.py
│       └── nate_main.py
│
├── .env
├── .gitignore
├── README.md
└── requirements.txt

How to Set Up
1. Create a Virtual Environment
Create a virtual environment in the project root:
python -m venv .venv

2. Activate the Virtual Environment
On macOS/Linux:
source .venv/bin/activate

On Windows:
.venv\Scripts\activate

3. Install Dependencies
After activating the virtual environment, install the required libraries:
pip install -r requirements.txt

Environment Variables
Create a .env file in the project root and add your API keys:
GROQ_API_KEY=your_groq_api_key
WEATHER_API_KEY=your_openweather_api_key

Do not commit the .env file to GitHub.
How to Run
The project contains two agents:
- NATE Agent – Remote weather agent
- Host Agent – Communicates with the NATE Agent using A2A
Both need to run at the same time.
1. Start the NATE Server
Open the first terminal and activate the virtual environment:
source .venv/bin/activate

Then run:
python -m agents.server.nate_main

The NATE agent will run at:
http://localhost:10003

2. Start the Host Agent
Open a second terminal.
Activate the virtual environment:
source .venv/bin/activate

Then run:
python -m agents.host.host

The Host Agent will discover the NATE Agent and communicate with it through A2A.
Example
Ask the Host Agent:
What is the current weather at latitude 28.5355 and longitude 77.3910?

The Host Agent sends the request to the NATE Agent, which retrieves the weather information and returns the result to the Host Agent.
```
