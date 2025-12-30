import json
import aiohttp
import requests

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role

class CustomDialClient(BaseClient):
    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self._endpoint = f"{DIAL_ENDPOINT}/openai/deployments/{deployment_name}/chat/completions"

    def get_completion(self, messages: list[Message]) -> Message:
        headers = {"api-key": self._api_key, "Content-Type": "application/json"}
        payload = {"messages": [msg.to_dict() for msg in messages]}
        resp = requests.post(self._endpoint, headers=headers, json=payload)
        if resp.status_code == 200:
            data = resp.json()
            choices = data.get("choices", [])
            if choices:
                msg = choices[0].get("message", {})
                content = msg.get("content")
                print(content)
                return Message(Role.AI, content)
            raise ValueError("No Choice has been present in the response")
        raise Exception(f"HTTP {resp.status_code}: {resp.text}")

    async def stream_completion(self, messages: list[Message]) -> Message:
        headers = {"api-key": self._api_key, "Content-Type": "application/json"}
        payload = {"stream": True, "messages": [msg.to_dict() for msg in messages]}
        contents = []
        async with aiohttp.ClientSession() as session:
            async with session.post(self._endpoint, headers=headers, json=payload) as resp:
                if resp.status == 200:
                    async for line in resp.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith("data: "):
                            data = line_str[6:].strip()
                            if data != "[DONE]":
                                snippet = self._get_content_snippet(data)
                                print(snippet, end='')
                                contents.append(snippet)
                            else:
                                print()
                else:
                    error_text = await resp.text()
                    print(f"{resp.status} {error_text}")
                return Message(Role.AI, ''.join(contents))

    def _get_content_snippet(self, data: str) -> str:
        obj = json.loads(data)
        choices = obj.get("choices")
        if choices:
            delta = choices[0].get("delta", {})
            return delta.get("content", '')
        return ''