import traceback
from collections.abc import Iterable
from pprint import pprint

from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from tenacity import retry, stop_after_attempt, wait_exponential

from config import OPENAI
from utils import file_cache


@file_cache(ttl=float('inf'))
@retry(wait=wait_exponential(), stop=stop_after_attempt(5))
def _complete(messages: Iterable[ChatCompletionMessageParam]) -> str:
    try:
        completion = OPENAI.chat.completions.create(
            messages=messages,
            model='gpt-4o',
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

    messages = (
        ChatCompletionSystemMessageParam(role='system', content=system),
        *(
            (
                ChatCompletionUserMessageParam(role='user', content=message)
                if i % 2 == 0
                else ChatCompletionAssistantMessageParam(role='assistant', content=message)
            )
            for i, message in enumerate(conversation)
        ),
    )

    return _complete(messages).strip()
