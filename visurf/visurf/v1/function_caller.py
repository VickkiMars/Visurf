from google import genai
from google.genai import types
from google.api_core import retry

from surfer import click, open_website_and_insert_text, download_all_audio, download_all_images, download_single_audio, download_single_image, get_websites, write_response_to_file, store_temp, read_cache, get_from_cache, create_folder, get_time, open_website_and_insert_text_and_click, open_google
genai.__version__

GOOGLE_API_KEY = ""


is_retriable = lambda e: (isinstance(e, genai.errors.APIError) and e.code in {429, 503})

if not hasattr(genai.models.Models.generate_content, '__wrapped__'):
    genai.models.Models.generate_content = retry.Retry(
        predicate=is_retriable
    )(genai.models.Models.generate_content)

surfer_tools = [click, open_website_and_insert_text, download_all_audio, download_all_images, download_single_audio, download_single_image, write_response_to_file, store_temp, read_cache, get_from_cache, create_folder, get_time, get_websites, open_website_and_insert_text_and_click, open_google]

instruction = """You are a helpful web surfer that can interact with websites for Netflix Inc. You will take the users questions, outline and understand the actions you will take and execute the actions using the given functions. Once you have the information you need, you will answer the user's question(s) using the data at your disposal as an helpful highly conversational AI assistant.

Use fetch_html to retrieve the html code of websites,
use click to click on a clickable element, takes in url, css selector, and a maximum of two meaningful words describing the subject at hand,
open_website_and_insert_text to insert text into an editable field, takes in a url, a css selector and a maximum of two meaningful words describing the subject at hand, 
download_all_audio to download multiple audio given a list of links to the direct audio resource, 
download_all_images to download multiple images given a list of links to the direct image resource, 
download_single_audio to download an audio file from a single link, 
download_single_image to download an image file from a single link, 
store_temp to store temporary information to cache, takes in the id and the information,  
read_cache to read all available information in the cache, 
get_from_cache to get a specific temporary information from cache, takes in the id of the information to be queried,
create_folder to create a folder, takes in a folder name, 
get_time to get the current time, 
get_websites to get a list of searchable websites.
open_website_and_insert_text_and_click to open a website, insert a text and click, takes in a url, text to be inserted, field_data to insert text, css selector to click and a maximum of two meaningful words describing the subject at hand.
open_google to open google's search website, takes in the text to be searched.

Use any of these functions fully to perform the given task.
Use google firstly, if that doesn't progressively attain success, try a more nuanced website.
If your first two trials do not work, try another way.
Do not return an 'I cannot directly access' statement or any thing like that. Utilize the tools to answer any given question regardless of the 'how'!

Remember: Most search input fields have the placeholder='Search' tag, use that in trials.
You can always store relevant data using the functions, then retrieve it and use it for another function call.
Make helpful suggestions whenever you are unable to fultill a request.
Do not try to squeeze in extra words in the subject.

Examples of CSS selectors:
-   input[text='Submit']
-   span[placeholder='Search'[]
-   //button[@id='signup']
-   a[href*='product']
example of calling the open_website_and_insert_text function:
    open_website_and_insert_text(url="https://google.com", {"input[placeholder='Search']": 'Hello by Adele'})
"""


client = genai.Client(api_key=GOOGLE_API_KEY)

chat = client.chats.create(
    model="gemini-2.0-flash",
    config=types.GenerateContentConfig(
        system_instruction=instruction,
        tools=surfer_tools,
    )
)

import textwrap


def print_chat_turns(chat):
    """Prints out each turn in the chat history, including function calls and responses."""
    for event in chat.get_history():
        print(f"{event.role.capitalize()}:")

        for part in event.parts:
            try:
                if txt := part.text:
                    print(f'  "{txt}"')
                elif fn := part.function_call:
                    args = ", ".join(f"{key}={val}" for key, val in fn.args.items())
                    print(f"  Function call: {fn.name}({args})")
                elif resp := part.function_response:
                    print("  Function response:")
                    print(textwrap.indent(str(resp.response['result']), "    "))
            except KeyError:
                pass

        print()

def analyze_and_click(page, external):
    html_content = page.content()
    relevant_info = ""
    response_from_gemini = chat.send_message()
    
    
    
    