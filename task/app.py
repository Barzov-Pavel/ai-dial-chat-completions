import asyncio

from task.clients.client import DialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role

async def start(stream: bool) -> None:
    client = DialClient(deployment_name='gpt-4o')
    custom_client = DialClient(deployment_name='gpt-4o')
    conversation = Conversation()

    print("Provide System prompt or press 'enter' to continue.")
    prompt = input("> ").strip()
    sys_prompt = prompt if prompt else DEFAULT_SYSTEM_PROMPT
    conversation.add_message(Message(Role.SYSTEM, sys_prompt))
    print("System prompt successfully added to conversation." if prompt else f"No System prompt provided. Will be used default System prompt: '{DEFAULT_SYSTEM_PROMPT}'")
    print()

    print("Type your question or 'exit' to quit.")
    while True:
        user_input = input("> ").strip()
        if user_input.lower() == "exit":
            print("Exiting the chat. Goodbye!")
            break
        conversation.add_message(Message(Role.USER, user_input))
        print("AI:")
        ai_message = await custom_client.stream_completion(conversation.get_messages()) if stream else custom_client.get_completion(conversation.get_messages())
        print(ai_message.content)
        conversation.add_message(ai_message)

asyncio.run(start(True))