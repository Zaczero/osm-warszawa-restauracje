import traceback
from pprint import pprint

from mistralai.models.chat_completion import ChatMessage
from tenacity import retry, stop_after_attempt, wait_exponential

from config import MISTRAL
from utils import file_cache


@file_cache(ttl=float('inf'))
@retry(wait=wait_exponential(), stop=stop_after_attempt(5))
def _complete(messages: list[ChatMessage]) -> str:
    try:
        completion = MISTRAL.chat(
            messages,
            model='open-mixtral-8x7b',
            temperature=0,
            max_tokens=1024,
        )

        response: str = completion.choices[0].message.content.strip()
        pprint(response)
    except Exception as e:
        pprint(messages)
        traceback.print_exc()
        raise e

    return response


def complete(system: str, *conversation: str) -> str:
    if len(conversation) % 2 == 0:
        raise ValueError('Conversation must be of odd length')

    messages = [ChatMessage(role='system', content=system)]

    for i, message in enumerate(conversation):
        role = 'user' if i % 2 == 0 else 'assistant'
        messages.append(ChatMessage(role=role, content=message))

    return _complete(messages).strip()
