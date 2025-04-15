import asyncio
import logging
from playwright.async_api import async_playwright
from funcall import prompt_gemini
from bs4 import BeautifulSoup
import tempfile
import random
import traceback


logging.basicConfig(level=logging.INFO)

# Dummy external system call functions (replace with your actual implementations)
def call(prompt, html):
    return prompt_gemini(mega_prompt=prompt, website_info=html)

def alpha_call(prompt):
    return prompt_gemini(mega_prompt=prompt)

def find_matches(data, word):
    matches = []
    for item in data:
        if 'textarea' in str(item).lower() or 'input' in str(item).lower():
            matches.append(item)
        elif word.lower() in str(item).lower():
            matches.append(item)
    return matches

def mainer(html_content, subject):
        main_match = []
        for word in subject.split():
            word = str(word).lower()
            matches = find_matches(html_content, word)
            main_match.append(matches)
        return main_match

def extract_tag_content(page):
    soup = BeautifulSoup(page, "html.parser")

    # Tags you want to extract
    tags_to_extract = ['a', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'input', 'textarea', 'button', 'tl', 'td', 'tr',]

    extracted_data = []

    for tag in soup.find_all(tags_to_extract):
        tag_name = tag.name
        tag_text = tag.get_text(strip=True)
        tag_attrs = tag.attrs
        extracted_data.append({
            "tag": tag_name,
            "text": tag_text,
            "attributes": tag_attrs
        })

    return extracted_data

async def web_surfer(prompt):
    """
    A web surfer that interacts with external systems using provided call functions.
    """
    async with async_playwright() as p:
        browser_type = p.chromium
        
        with tempfile.TemporaryDirectory() as user_data_dir:
            browser = await browser_type.launch_persistent_context(user_data_dir=user_data_dir, headless=False)
            page = await browser.new_page()

            try:
                # Get the initial URL from the alpha external system
                initial_url = alpha_call(prompt)
                print(initial_url, type(initial_url))
                if not initial_url["url"]:
                    logging.error("Failed to get initial URL from alpha system.")
                    return

                if initial_url["action"] == "open":
                    await page.goto(initial_url["url"], timeout=50000)
                    logging.info("Opening %s", initial_url["url"])
                    await page.wait_for_load_state('load')
                    await page.wait_for_load_state('networkidle')
                    await page.wait_for_load_state('domcontentloaded')


                while True:
                    html = await page.content()
                    html = extract_tag_content(html)
                    try:
                        # Interact with the main external system
                        action = call(prompt=prompt, html=html)
                        print(f"ACTION: {action}")

                        if not action:
                            logging.error("External system call failed.")
                            break

                        if action["action"] == "exit":
                            print(f"Model Response: {action['response']}")
                            break

                        if action["action"] == "click":
                            try:
                                element = page.query_selector(action["button_selector"])
                                if await element:
                                    try:
                                        await element.click()
                                    except Exception:
                                    # await page.click(action["button_selector"], timeout=15000, force=True)
                                    # await page.wait_for_timeout(15000)
                                    # await page.wait_for_load_state('domcontentloaded')
                                    # await time.sleep(4)
                                        button_locator = page.locator(action["button_selector"])
                                        logging.info("Clicking Selector %s ", action["button_selector"])
                                        await button_locator.click()
                                        logging.info("Clicked!")
                                        await page.wait_for_load_state('load')
                                        await page.wait_for_load_state('networkidle')
                                        await page.wait_for_load_state('domcontentloaded')
                                        await asyncio.sleep(4)
                                        await page.wait_for_load_state('load')
                                        await page.wait_for_load_state('networkidle')
                                        await page.wait_for_load_state('domcontentloaded')
                                        html = await page.content()
                                        with open("page.html", "w", encoding="utf-8") as f:
                                            f.write(html)
                                else:
                                    logging.error("Selector not found: %s", action["button_selector"])
                            except Exception as e:
                                logging.error("Selector not found: %s, error: %s", action['button_selector'], e)
                        elif action["action"] == "insert_text":
                            try:
                                for selector, text in action["field_data"].items():
                                    if await page.query_selector(selector):
                                        for char in text:
                                            #input_ = await page.input_value(selector)
                                            await page.fill(selector, await page.input_value(selector) + char)
                                            await asyncio.sleep(random.uniform(0.001, 0.02))
                                            await page.wait_for_load_state('load')
                                            await page.wait_for_load_state('networkidle')
                                            await page.wait_for_load_state('domcontentloaded')
                                if "google.com" in page.url:
                                    await page.wait_for_selector('ul.G43f7e > li:first-child', timeout=5000)
                                    await page.click("ul.G43f7e > li:first-child")
                                    await page.wait_for_load_state('networkidle')
                                    #await page.press(selector, "Enter")
                                    await asyncio.sleep(4)
                                #await page.type(action["selector"], action["text"])
                            except Exception as e:
                                logging.error(f"Selector not found: {action['field_data']}, error: {e}")
                                logging.error(f"A selector in {action['field_data']} has not been found")
                        elif action["action"] == "open":
                            print(action.keys())
                            await page.goto(action['url'], timeout=50000)
                            await page.wait_for_load_state('load')
                            await page.wait_for_load_state('networkidle')
                            await page.wait_for_load_state('domcontentloaded')
                        else:
                            logging.warning(f"Unknown action: {action}")

                    except Exception as e:
                        logging.error(f"oops, something went wrong: {e, traceback.print_exc()}")
                        break

            except Exception as e:
                logging.error(f"Error during initial navigation or main loop: {e}")

            finally:
                await browser.close()

async def main():
    while True:
        PROMPT = input("Enter a prompt: ")
        await web_surfer(PROMPT)
        if PROMPT == "exit" or PROMPT == "":
            break

if __name__ == "__main__":
    asyncio.run(main())