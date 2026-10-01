
from a2a.client import ClientFactory,ClientConfig
from a2a.types import AgentCard
import httpx
class RemoteAgentConnection:
    def __init__(self,agentcard:AgentCard,agent_url:str):
        print(f"Agent Card : {agentcard}")
        print(f"Agent_url: {agent_url}")
        self.card=agentcard
        self.conversation_name=None
        self.conversation=None
        self.pending_task=set()
        self.http_client = httpx.AsyncClient(
            timeout=120.0
        )
        
        config = ClientConfig(
            streaming=True,
            polling=False,
            httpx_client=self.http_client
        )

        factory = ClientFactory(config)
        self.agent_client = factory.create(agentcard)

    def get_agent(self) -> AgentCard:
        """
        Return the Agent Card of the remote agent.

        Returns:
            AgentCard:
                The remote agent's Agent Card.
        """
        return self.card
    
    async def send_message(self, message_request):
        print("Sending A2A message...")

        result_text = None

        async for response in self.agent_client.send_message(message_request):


            response_type = response.WhichOneof("payload")

            if response_type == "task":
                print("TASK SUBMITTED")

            elif response_type == "artifact_update":
                print("ARTIFACT UPDATE FOUND")

                parts = []

                for part in response.artifact_update.artifact.parts:
                    if part.text:
                        parts.append(part.text)

                if parts:
                    result_text = "\n".join(parts)

            elif response_type == "message":
                print("MESSAGE FOUND")

                parts = []

                for part in response.message.parts:
                    if part.text:
                        parts.append(part.text)

                if parts:
                    result_text = "\n".join(parts)

            elif response_type == "status_update":
                print(
                    "STATUS UPDATE:",
                    response.status_update.status.state
                )

        print("A2A stream finished")
        
        return result_text