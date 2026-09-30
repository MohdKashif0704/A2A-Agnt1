import os 
import asyncio
import json
from uuid import uuid4
import httpx
from a2a.types import SendMessageConfiguration
from dotenv import load_dotenv
from a2a.types import SendMessageRequest,SendMessageResponse,Task,Message,Part,Role,Artifact
from typing import  List
from a2a.client import A2ACardResolver
from remote_agent_connection import RemoteAgentConnection
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
import nest_asyncio
from langchain_groq import ChatGroq

nest_asyncio.apply()

load_dotenv()

gemini_api_key=os.getenv("GEMINI_API_KEY")
groq_api_key=os.getenv("GROQ_API_KEY")
print("Key loaded:", bool(gemini_api_key))
class HostAgent:

    def __init__(self):
        self.remote_agent_connections={}
        self.cards={}
        self.agents=""
        self._agent=None
        self._user_id="host_agent"

    async def async_init_component(self,remoteAgentAddress:List[str]):
        async with httpx.AsyncClient(timeout=120.0) as client:
            for address in remoteAgentAddress:
                card_resolver=A2ACardResolver(client,address) 
                try:
                    card=await card_resolver.get_agent_card()
                    remote_connections=RemoteAgentConnection(
                        agentcard=card,agent_url=address
                    )
                    self.remote_agent_connections[card.name]=remote_connections
                    self.cards[card.name]=card
                except httpx.ConnectError as e:
                    print(f"ERROR: Failed to get agent card from {address}: {e}")
                except Exception as e:
                    print(f"ERROR: Failed to initialize connection for {address}: {e}")
        agent_info = [
            json.dumps({"name": card.name, "description": card.description})
            for card in self.cards.values()
        ]
        print("agent_info:", agent_info)
        self.agents = "\n".join(agent_info) if agent_info else "No friends found"

    @classmethod
    async def create(cls,remoteAgentAddresses:List[str]):
        instance=cls()
        await instance.async_init_component(remoteAgentAddresses)
        instance._agent = instance.create_agent()
        return instance
    
    def create_agent(self):

        @tool
        def greet_msg():
            """
            Greet the user with a friendly message.

            Returns:
                str: A greeting message for the user.
            """
            return "Good Evening, Kashif this side"

        @tool
        async def send_message(agent_name: str, task: str):
            """
            Send a task or question to a remote agent and return its response.

            Args:
                agent_name (str): The exact name of the remote agent that should
                    handle the task.
                task (str): The task, question, or request that should be sent
                    to the remote agent.

            Returns:
                list[Part]: A list of response parts returned by the remote agent.

            Raises:
                ValueError: If the specified agent does not exist or its client
                    connection is unavailable.
            """
            return await self._send_message(agent_name, task)


        #llm=ChatGoogleGenerativeAI(model="gemini-3.6-flash",api_key=gemini_api_key)
        new_llm=ChatGroq(
            model="openai/gpt-oss-20b",
            api_key=os.getenv("GROQ_API_KEY"),
            reasoning_format="hidden"
        )


        agent=create_agent(

            model=new_llm,
            system_prompt=self.root_instruction(),
            tools=[send_message,greet_msg]
        )
        return agent
    
    def root_instruction(self) -> str:
        return f"""
            You are the Host Agent.

            Your primary responsibility is to communicate and coordinate with
            remote agents using the available tools.

            ### Available Tools

            1. `greet_msg`
            - Use this when the user asks you to greet them or when a greeting
                is appropriate.

            2. `send_message`
            - Use this tool whenever you need information, an action, or a response
                from a remote agent.
            - The `agent_name` must be the exact name of one of the available
                remote agents.
            - Put the actual request for the remote agent in the `task` argument.

            ### Remote Agent Communication

            When the user asks for something that requires a remote agent:

            1. Identify which remote agent should handle the request.
            2. Call `send_message` with the correct `agent_name`.
            3. Clearly describe the user's request in the `task`.
            4. Wait for the remote agent's response.
            5. Interpret the response and provide the relevant information to the user.

            Do not pretend that you contacted a remote agent if you did not actually
            use the `send_message` tool.

            Do not invent information that should come from a remote agent.

            If multiple remote agents are relevant, you may contact them separately
            and combine their responses.

            ### Available Remote Agents

            {self.agents}

            ### General Behavior

            - Be concise and clear.
            - Use tools when they are appropriate.
            - Do not expose internal implementation details such as A2A requests,
            UUIDs, or connection objects to the user.
            - When reporting a remote agent's response, explain it naturally to the user.
            """
    
    
    async def _send_message(self, agent_name: str, task: str):

        if agent_name not in self.remote_agent_connections:
            raise ValueError(f"Agent {agent_name} not found")

        client = self.remote_agent_connections[agent_name]

        if not client:
            raise ValueError(
                f"Client not available for agent {agent_name}"
            )

        context_id = str(uuid4())
        message_id = str(uuid4())

        message = Message(
            role=Role.ROLE_USER,
            message_id=message_id,
            context_id=context_id,
            parts=[Part(text=task)],
        )

        request_message = SendMessageRequest(
            message=message,
            configuration=SendMessageConfiguration(
                return_immediately=False
            )
        )

        print("Sending request to remote agent...")

        send_response = await client.send_message(request_message)

        print("REMOTE RESPONSE:")
        print(send_response)

        print("RESPONSE TYPE:")
        print(type(send_response))

        if not send_response:
            return "Remote agent returned no response."

        return send_response
            

async def main():

    friend_agent_url = [
        "http://localhost:10003"
    ]

    print("Initializing remote agents")

    host_agent_instance = await HostAgent.create(
        remoteAgentAddresses=friend_agent_url
    )

    print("Host Agent initialized")

    response = await host_agent_instance._agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "What is the current weather at latitude 28.5355 and longitude 77.3910?"
                }
            ]
        }
    )

    print(response)


if __name__ == "__main__":
    asyncio.run(main())