import os
import sys
import math
import json
import time
from functools import reduce
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI


def get_openai_key():
    _ = load_dotenv(find_dotenv())
    return os.environ['OPENAI_API_KEY']


def get_completion_from_messages(messages, model="gpt-4o-2024-08-06", temperature=0, max_tokens=500, json_format=False):
    paid_api_key = 'XXX'
    base_url = f"https://api.openai.com/v1"

    client = OpenAI(
        api_key=paid_api_key,
        base_url=base_url,
        timeout=6,
        max_retries=1,
    )

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        response_format={"type": "json_object"} if json_format else {"type": "text"},
        frequency_penalty=0,
        presence_penalty=0,
        stream=False,
    )
    # for chunk in response:
    #     if chunk.choices[0].delta.content is not None:
    #         print(chunk.choices[0].delta.content, end="")

    reply = response.choices[0].message.content
    return reply


def chat_input_completion_mode1(context: str, utterance: str):
    system_prompt = f"""
    You are an advanced input method chat assistant, giving users helpful word and utterance options for conversation.

    You will be provided with the conversation delimited by ```. According to the context of this conversation, your task is to predict appropriate inputs of the word and user utterance in three steps:
    Step 1. complete or predict the word based on its prefix delimited by angle brackets i.e. < >, give five appropriate words.
    Step 2. based on Step 1, use the first one to replace its prefix.
    Step 3. based on Step 2, complete or predict the entire user utterance delimited by square brackets i.e. [ ], give two appropriate user utterances in sentences with no bracket.

    Ensure to take the context of the conversation into account in all steps.
    You can also proofread and correct the predicted words and user utterances if necessary.

    Response in the json format only as follows, with no extra description:
    {{"prefix": the prefix of the predicted words, "words": a list of five appropriate words, "user utterances": a list of two appropriate user utterances}}
    """

    user_prompt = f"""
    Conversation:
    ```
    {context}
    {utterance}
    ```
    """

    few_shot_user_1 = """   
    Conversation:
    ```
    User: [<h>]
    ```
    """
    few_shot_assistant_1 = """ 
{
    "prefix": "h",
    "words": ["How", "Have", "Hello", "He", "Help"],
    "user utterances": ["How are you?", "How can I assist you?"]
}
"""

    few_shot_user_2 = """   
    Conversation:
    ```
    User: [The dog is < >]
    ```
    """
    few_shot_assistant_2 = """ 
{
    "prefix": "",
    "words": ["cute", "playing", "sleeping", "running", "braking"],
    "user utterances": ["The dog is cute.", "The dog is cute and friendly."]
}
"""

    few_shot_user_3 = """
    Conversation:
    ```
    Interlocutor: Do you like sports?
    User: Yes, [i like playing <c>]
    ```
    """
    few_shot_assistant_3 = """
{
    "prefix": "c",
    "words": ["cricket", "cycling", "canoeing", "climbing", "chess"],
    "user utterances": ["I like playing cricket.", "I like playing cricket with my friends."]
}
"""

    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': few_shot_user_1},
        {'role': 'assistant', 'content': few_shot_assistant_1},
        {'role': 'user', 'content': few_shot_user_2},
        {'role': 'assistant', 'content': few_shot_assistant_2},
        {'role': 'user', 'content': few_shot_user_3},
        {'role': 'assistant', 'content': few_shot_assistant_3},
        {'role': 'user', 'content': user_prompt},
    ]

    response = get_completion_from_messages(messages, json_format=True)
    response = json.loads(response)
    return response


def get_word_completer(corpus_file = 'utils/corpus.txt'):
    from fast_autocomplete import AutoComplete
    import string, re, collections

    def tokens(text):
        """
        Get all words from the corpus
        """
        return re.findall("[a-z']+", text.lower())

    with open(corpus_file, 'r', encoding='utf-8') as f:
        WORDS = tokens(f.read())
    WORD_COUNTS = collections.Counter(WORDS)
    words = {k: {'count': v} for k, v in WORD_COUNTS.items()}
    valid_chars = "'" + string.ascii_lowercase
    word_completer = AutoComplete(words=words, valid_chars_for_string=valid_chars)
    return word_completer


if __name__ == '__main__':
    response = chat_input_completion_mode1('', "User: [my favorite sport is <>]")
    print(response)