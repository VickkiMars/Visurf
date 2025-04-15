from google import genai
from google.genai import types
from google.api_core import retry
from utils import websites, prompt, prompt_wi
from ast import literal_eval
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")

is_retriable = lambda e: (isinstance(e, genai.errors.APIError) and e.code in {429, 503})

if not hasattr(genai.models.Models.generate_content, '__wrapped__'):
    genai.models.Models.generate_content = retry.Retry(
        predicate=is_retriable
    )(genai.models.Models.generate_content)

config = types.GenerateContentConfig(temperature=0.0)
client = genai.Client(api_key=api_key)
chat = client.chats.create(model='gemini-1.5-flash')

def ffo(text, letter):
    for i, char in enumerate(text):
        if char == letter:
            return i
    return False

def flo(text, letter):
    id = False
    for i, char in enumerate(text):
        if char == letter:
            id = i
    return id
    
def remove_trailers(text):
    try:
        fid = ffo(text, '{')
        if fid != False:
            text = text[fid:]
            print(text)
            lid = flo(text, '}')
            text = text[:lid+1]
            text = literal_eval(text.strip())
            return text
    except Exception as e:
        print(f"An Exception occurred: {e}, {text}")

def prompt_gemini(mega_prompt, website_info=False):
    """
    Prompts the Gemini model with a given prompt and returns the response.

    Args:
        prompt (str): The prompt to send to the Gemini model.

    Returns:
        str: The generated response from the Gemini model, or None if an error occurs.
    """
    if website_info:
        prompt_ = prompt_wi.format(mega_prompt, website_info)
        print(f"\n{website_info}\n")
    else:
        prompt_ = prompt.format(websites, mega_prompt)

    try:
        response = chat.send_message(
            message=prompt_
        )
        print(f"\n{response.text}\n")
        text = remove_trailers(
            response.text
        )
        if text is not None:
            return text
        else:
            raise ValueError(f"There was an error with the model response: {text}")
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
