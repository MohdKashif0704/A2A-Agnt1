import os
from dotenv import load_dotenv

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.utils.errors import InternalError
from a2a.helpers import new_task_from_user_message


from a2a.types import TaskState, Part
from nate_agent import NATE


load_dotenv()

class NATEAgentExecutor(AgentExecutor):

    def __init__(self):
        self.nate_agent = NATE()

    async def execute(
        self,
        request_context: RequestContext,
        event_queue: EventQueue
    ):
        print("1. Executor started")

        user_input = request_context.get_user_input()
        print("2. User input:", user_input)

        if not user_input:
            raise InternalError(
                "User input is required for NATE agent execution."
            )

        task = request_context.current_task

        if task is None:
            print("3. Creating and enqueueing Task")

            task = new_task_from_user_message(
                request_context.message
            )

            await event_queue.enqueue_event(task)

        updater = TaskUpdater(
            event_queue=event_queue,
            task_id=task.id,
            context_id=task.context_id,
        )

        print("4. Calling NATE")

        try:
            response = await self.nate_agent.ainvoke(user_input)

            print("5. NATE returned")

            

            print("6. Structured response:", response)

            await updater.add_artifact(
                parts=[Part(text=response)]
            )

            print("7. Artifact added")

            await updater.update_status(
                state=TaskState.TASK_STATE_COMPLETED
            )

            print("8. Task completed")
            print("9. Executor returning")

        except Exception as e:
            print("NATE ERROR:", repr(e))

            raise InternalError(
                f"Error executing NATE agent: {str(e)}"
            )

    async def cancel(self, context, event_queue):
        return await super().cancel(context, event_queue)