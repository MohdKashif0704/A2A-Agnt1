import os 
from dotenv import load_dotenv
from a2a.server.request_handlers import DefaultRequestHandler
import uvicorn
from a2a.server.tasks import InMemoryTaskStore
from starlette.applications import Starlette
from a2a.types import (AgentCapabilities,AgentCard,AgentSkill,AgentInterface)
from nate_agent_executor import NATEAgentExecutor
from nate_agent import NATE
from a2a.server.routes import (create_agent_card_routes,create_jsonrpc_routes)

load_dotenv()

gemini_api_key=os.getenv("GEMINI_API_KEY")

def main():
    host="localhost"
    port=10003
    try:
        capabilities=AgentCapabilities(streaming=True)
        agent_skill=AgentSkill(
            id="waeather_checker",
            name="weather",
            description="Provides weather information using latitude and longitude.",
            tags=["weather", "humidity","temperature","location"],
            examples=[
                "Get weather for latitude 28.6139 and longitude 77.2090",
                "What is the current weather at 28.5355, 77.3910?"
                
                ]
        )

        agent_host_url=f"http://{host}:{port}"

        agent_card=AgentCard(
            name="Nate Agent",
            description="Agent that help you to find weather information using latitude and longitude co-ordinates",
            supported_interfaces=[AgentInterface(url=agent_host_url,protocol_binding="JSONRPC")],
            capabilities=capabilities,
            version="1.0.0",
            default_input_modes=["text/plain"],
            default_output_modes=["text/plain"],
            skills=[agent_skill],
        )

        request_handler=DefaultRequestHandler(
            agent_card=agent_card,
            agent_executor=NATEAgentExecutor(),
            task_store=InMemoryTaskStore()
            )

        routes=[]
        # Agent Card endpoint
        routes.extend(
            create_agent_card_routes(agent_card=agent_card)
        )
        # A2A JSON-RPC endpoint
        routes.extend(
            create_jsonrpc_routes(request_handler=request_handler,rpc_url="/")
        )

        app=Starlette(routes=routes)
        uvicorn.run(
            app=app,
            host=host,
            port=port
        )


    except Exception as e:
        print(f"ERROR: {e}")
        raise

if __name__ == "__main__":
    main()