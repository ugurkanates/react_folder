import openai
from openai import OpenAI
import time
import json
from pydantic import BaseModel, ValidationError, ConfigDict
from typing import Type

def check_openai_api_key(api_key):
    client = openai.OpenAI(api_key=api_key)
    try:
        client.models.list()
    except openai.AuthenticationError:
        return False
    else:
        return True


OPENAI_API_KEY = "sk......"
model = 'gpt-4'


def client_setup(api_key=OPENAI_API_KEY):
    if check_openai_api_key(OPENAI_API_KEY):
        print("Valid OpenAI API key.")
    else:
        print("Invalid OpenAI API key.")
    return OpenAI(api_key=api_key)

def is_valid_json_for_model(text: str, model: Type[BaseModel]) -> bool: 
    model.model_config = ConfigDict(strict=True)

    try:
        parsed_data = json.loads(text)
        model(**parsed_data)
        return True
    except (json.JSONDecodeError, ValidationError):
        return False

def output_representation(model_output: Type[BaseModel]) -> str:
    fields = model_output.__annotations__
    return ', '.join(f'{key}: {value}' for key, value in fields.items())

def generator(client, prompt, max_tokens=None,output=None):
    valid_responses = []
    retry_delay = 0.1
    while len(valid_responses) < 1: # We want at least one valid response
            try:
                system_message = "You are a helpful assistant."
                if output:
                    system_message += f" Respond in a JSON format that contains the following keys: {output_representation(output)}" # 

                params = {
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": system_message
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.5, # saw this used in the 
                    # OpenAI docs https://www.coltsteele.com/tips/understanding-openai-s-temperature-parameter
                    "n": 1
                }
                if max_tokens is not None:
                    params["max_tokens"] = max_tokens
                response = client.chat.completions.create(**params)
                choices = response.choices
                responses = [choice.message.content
                             for choice in choices]

                if output:
                    valid_responses.extend(
                        [json.loads(res) for res in responses
                         if is_valid_json_for_model(res, output)]
                    )
                else:
                    valid_responses.extend(responses)
            except openai.RateLimitError:
                print(f"Hit rate limit. Retrying in {retry_delay} seconds.")
                time.sleep(retry_delay)
                retry_delay *= 2
            except Exception as err:
                print(f"Error: {err}")
                break
    return valid_responses[0]
# Check the validity of the API key
api_key_valid = check_openai_api_key(api_key=OPENAI_API_KEY)
print("API key is valid:", api_key_valid)