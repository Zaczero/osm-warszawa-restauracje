import traceback
from pprint import pprint

from tenacity import retry, stop_after_attempt, wait_exponential

from config import OPENAI
from utils import file_cache


@file_cache(ttl=float('inf'))
@retry(wait=wait_exponential(), stop=stop_after_attempt(5))
def _complete(messages: list) -> str:
    try:
        completion = OPENAI.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=messages,
            temperature=0,  # more randomness
            max_tokens=1024,
            frequency_penalty=0,  # less repetition
            presence_penalty=0,  # more diversity
            timeout=30,
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

    messages = [{'role': 'system', 'content': system}]

    for i, message in enumerate(conversation):
        messages.append({'role': 'user' if i % 2 == 0 else 'assistant', 'content': message})

    return _complete(messages).strip()
