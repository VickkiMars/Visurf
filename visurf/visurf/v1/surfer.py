import requests
from bs4 import BeautifulSoup
import random
import time
import os
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, unquote
from typing import Optional, Any
from extractag import extract_tag_content
import ntplib
from time import ctime

DEFAULT_CACHE = {}
MAIN_CONTEXT = None

def find_matches(data, word):
    matches = []
    for item in data:
        if word.lower() in str(item).lower():
            matches.append(item)
    return matches

def move_mouse_randomly(page, steps=30):
    """Simulate random mouse movement around the page."""
    viewport = page.viewport_size
    if viewport:
        width = viewport['width']
        height = viewport['height']
        
        for _ in range(steps):
            x = random.randint(0, width)
            y = random.randint(0, height)
            page.mouse.move(x, y, steps=random.randint(5, 20))
            time.sleep(random.uniform(0.05, 0.2))

def get_time() -> str:
    ntp_server="time.windows.com"
    client = ntplib.NTPClient()
    response = client.request(ntp_server)
    return str(ctime(response.tx_time))

def get_websites() -> list:
    websites = [
    "https://www.google.com",
    "https://www.wikipedia.org",                # General knowledge
    "https://www.howstuffworks.com",            # Explainers
    "https://www.khanacademy.org",              # Education
    "https://www.nationalgeographic.com",       # Geography, science
    "https://www.worldtimebuddy.com",           # World time
    "https://www.timeanddate.com",              # Time, calendar, sun/moon
    "https://www.weather.com",                  # Weather
    "https://www.accuweather.com",              # Weather
    "https://www.wolframalpha.com",             # Computations, facts
    "https://www.unitconverters.net",           # Unit conversion
    "https://www.metric-conversions.org",       # Unit conversion
    "https://www.geonames.org",                 # Country data
    "https://www.britannica.com",               # Encyclopedia
    "https://www.ducksters.com",                # Kids knowledge
    "https://www.coolmath.com",                 # Math help
    "https://www.mathsisfun.com",               # Math concepts
    "https://www.codecademy.com",               # Programming education
    "https://www.geeksforgeeks.org",            # CS concepts
    "https://www.tutorialspoint.com",           # Tutorials
    "https://www.stackoverflow.com",            # Programming Q&A
    "https://www.askdruniverse.wsu.edu",        # Kid-friendly science Q&A
    "https://www.nationalatlas.gov",            # US geography
    "https://www.nutritionvalue.org",           # Food info
    "https://www.cdc.gov",                      # Health
    "https://www.nih.gov",                      # Health research
    "https://www.mayoclinic.org",               # Medical Q&A
    "https://www.medlineplus.gov",              # Health info
    "https://www.webmd.com",                    # Medical questions
    "https://www.biblegateway.com",             # Bible Q&A
    "https://www.quran.com",                    # Quran questions
    "https://www.gotquestions.org",             # Christian Q&A
    "https://www.imdb.com",                     # Movie info
    "https://www.rottentomatoes.com",           # Movie reviews
    "https://www.metacritic.com",               # Game/movie/music reviews
    "https://www.goodreads.com",                # Book Q&A and reviews
    "https://www.bartleby.com",                 # Literature and study help
    "https://www.sparknotes.com",               # Study guides
    "https://www.history.com",                  # History questions
    "https://www.loc.gov",                      # Library of Congress
    "https://www.encyclopedia.com",             # Reference info
    "https://www.50states.com",                 # US states info
    "https://www.duolingo.com",                 # Language learning
    "https://www.omniglot.com",                 # Language systems
    "https://www.ethnologue.com",               # Language data
    "https://www.fueleconomy.gov",              # Car fuel efficiency
    "https://www.autoblog.com",                 # Car info
    "https://www.kbb.com",                      # Car pricing
    "https://www.bankrate.com",                 # Finance
    "https://www.investopedia.com",             # Financial terms
    "https://www.irs.gov",                      # Taxes (US)
    "https://www.bls.gov",                      # Labor and stats
    "https://www.bea.gov",                      # Economic data
    "https://www.usgs.gov",                     # Geological info
    "https://www.nasa.gov",                     # Space info
    "https://solarsystem.nasa.gov",             # Planetary data
    "https://www.astronomy.com",                # Astronomy
    "https://www.space.com",                    # Space Q&A
    "https://www.worldometers.info",            # Live world stats
    "https://www.statista.com",                 # Statistics
    "https://www.ourworldindata.org",           # Global data and trends
    "https://www.sciencedaily.com",             # Science news
    "https://www.livescience.com",              # Science Q&A
    "https://www.scientificamerican.com",       # Scientific insights
    "https://www.science.org",                  # Journals and discoveries
    "https://www.zooniverse.org",               # Citizen science
    "https://www.nationalzoo.si.edu",           # Animals
    "https://www.animaldiversity.org",          # Animal facts
    "https://www.allaboutbirds.org",            # Bird data
    "https://www.gutenberg.org",                # Public domain books
    "https://www.poetryfoundation.org",         # Poetry
    "https://www.archive.org",                  # Internet archive
    "https://www.openlibrary.org",              # Book info
    "https://www.wikiquote.org",                # Quotes
    "https://www.brainyquote.com",              # Quotes and authors
    "https://www.sporcle.com",                  # Trivia quizzes
    "https://www.factmonster.com",              # Kids knowledge
    "https://www.infoplease.com",               # General facts
    "https://www.pluralsight.com",              # Tech learning
    "https://www.edx.org",                      # Online courses
    "https://www.udemy.com",                    # Learn anything
    "https://www.coursera.org",                 # Academic learning
    "https://www.stackexchange.com",            # Expert Q&A
    "https://www.nolo.com",                     # Legal help
    "https://livescore.com",                    # Sports
    "https://www.justia.com",                   # US law info
    "https://www.usa.gov",                      # US government info
    "https://www.wto.org",                      # Trade and economics
    "https://www.un.org",                       # Global affairs
    "https://www.who.int",                      # World Health Organization
    "https://www.immunize.org",                 # Vaccine facts
    "https://www.drugs.com",                    # Drug info
    "https://www.ncbi.nlm.nih.gov",             # Research & PubMed
    "https://www.researchgate.net",             # Research Q&A
    "https://www.stackshare.io",                # Dev tools comparisons
    "https://www.programmableweb.com",          # APIs
    "https://jsonplaceholder.typicode.com",     # Dummy APIs
    "https://reqres.in",                        # REST API simulation
    "https://opendata.stackexchange.com",       # Open data Q&A
    "https://www.openstreetmap.org",            # Maps and geo
    "https://www.mapsofworld.com",              # Country maps
    "https://www.visalist.io",                  # Visa rules
    "https://www.numbeo.com",                   # Cost of living
    "https://www.exchangerates.org.uk",         # Currency exchange
    "https://www.oanda.com",                    # Currency info
    "https://www.forexfactory.com",             # Forex info
    "https://www.thetoptens.com",               # Rankings/lists
    ]
    return websites

def parse_string(string):
    arr = string.split(" ")
    print(arr)
    new_String = ""
    for token in arr:
        if token == arr[-1]:
            new_String += token
        else:
            new_String += token+"%20"
    return new_String

def random_delay(min_seconds=2, max_seconds=5):
    """Mimic human-like delays between actions."""
    time.sleep(random.uniform(min_seconds, max_seconds))

def use_stealth_settings(context):
    """Configure stealth-like settings to make browser less detectable."""
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        window.navigator.chrome = { runtime: {} };
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    """)

def generate_headers() -> str:
    """Generate randomized headers to avoid detection."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
    ]
    return random.choice(user_agents)

def launch_undetectable_browser(playwright):
    """Launch browser with stealth settings and non-headless mode."""
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent=generate_headers(),
        viewport={"width": 1280, "height": 800}
    )
    use_stealth_settings(context)
    MAIN_CONTEXT = context
    return browser, context

def fetch_html(url:str) -> list[str]:
    """Fetch HTML content using requests."""
    try:
        response = requests.get(url, headers={"User Agent":generate_headers()})
        response.raise_for_status()  # Raise an error for failed requests
        return extract_tag_content(response.text)
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_html(html:str) -> Optional[BeautifulSoup]:
    """Parse the HTML content using BeautifulSoup."""
    return BeautifulSoup(html, "html.parser") if html else None

def open_website_and_insert_text_and_click(url:str, field_data:dict, button_selector:str, subject:str) -> list[str]:
    with sync_playwright() as p:
        browser, context = launch_undetectable_browser(p)
        page = context.new_page()
        page.goto(url)
        random_delay()
        move_mouse_randomly(page=page)

        try:
            page.click("text=Accept all")
        except:
            pass
        print("ENtering text")
        for selector, text in field_data.items():
            if page.query_selector(selector):
                for char in text:
                    page.fill(selector, page.input_value(selector) + char)
                    time.sleep(random.uniform(0.1, 0.3))

                random_delay()
        print("clicking button")
        try:
            page.wait_for_selector(button_selector)
        except Exception as e:
            pass
        page.click(button_selector, timeout=30000)
        print("button clicked")
        html = page.content()

        main_match = []
        for item in subject.split():
            word = str(item).lower()
            matches = find_matches(html, word)
            main_match.append(matches)
        url = page.url
        
    return [main_match, url]

def open_google(search_term:str):
    """Opens Google, inserts text into the search field, and performs a search (synchronous)."""
    with sync_playwright() as p:
        browser, context = launch_undetectable_browser(p)
        page = context.new_page()

        page.goto("https://www.google.com")
        selector = 'textarea[name="q"]'
        for text in search_term:
            random_delay
            page.fill(selector, page.input_value(selector) + text)  # Fill the search field.
        move_mouse_randomly(page=page, steps=2)
        page.wait_for_selector('ul[role="listbox"] li:first-child', state="visible")
        page.click('ul[role="listbox"] li:first-child')

        page.wait_for_load_state("networkidle")
        page.wait_for_load_state("domcontentloaded")  # Wait for the search results to load. arsenals last match
        print(f"Search results for '{search_term}' loaded.")
        return extract_tag_content(page.content())

def open_website_and_insert_text(url:str, field_data:dict, subject:str) -> list[str, list]:
    """
    Inserts text into multiple input fields on a webpage using Playwright.
    
    :param url: URL of the webpage containing the input fields.
    :param field_data: A dictionary where keys are the field selectors and values are the text to input.
    """
    with sync_playwright() as p:
        browser, context = launch_undetectable_browser(p)
        page = context.new_page()
        page.goto(url)  # Open page with 10s timeout
        random_delay()

        try:
            page.click("text=Accept all")  # Adjust if different
        except:
            pass

        # Loop through each field and insert corresponding text
        for selector, text in field_data.items():
            if page.query_selector(selector):
                for char in text:
                    page.fill(selector, page.input_value(selector) + char)
                    time.sleep(random.uniform(0.1, 0.3))

                random_delay()
                #input_field = page.locator(selector)
            #page.wait_for_selector('#search')
            
        # Optionally, press the 'Enter' key for the last field or submit the form
        
        # Retrieve the HTML after filling in the fields (useful for debugging or further processing)
        time.sleep(3)
        html_content = extract_tag_content(page.content())
        main_match = []
        for item in subject.split():
            word = str(item)
            matches = find_matches(html_content, word)
            main_match.append(matches)


        url = page.url
        browser.close()
    
    return [url, main_match]

def mainer(html_content, subject):
            main_match = []
            for word in subject.split():
                word = str(word).lower()
                matches = find_matches(html_content, word)
                main_match.append(matches)
            return main_match

def click(url:str, button_selector:str, subject:str) -> list[str]:
    """
    Clicks a button using Playwright.
    
    :param url: URL of the webpage containing the button.
    :param button_selector: CSS selector for the button to click.
    """
    with sync_playwright() as p:
        browser, context = launch_undetectable_browser(p)
        page = browser.new_page()
        page.goto(url, timeout=30000)  # Open page with 10s timeout
        try:
            page.click("text=Accept all")  # Adjust if different
        except:
            pass

        page.click(button_selector, timeout=15000, force=True)  # Click the button
        page.wait_for_load_state('domcontentloaded')
        time.sleep(30)
        html_content = extract_tag_content(page.content())  # Get updated HTML after clicking

        url = page.url
        main_info = mainer(html_content=html_content, subject=subject)

        browser.close()
    return [url, main_info]

def conitional_navigator(url:str, action:str, subject:str, button_selector:str=None, field_data:dict=None):
    page_ = None
    browser_ = None
    context_ = None
    main_info_ = None
    with sync_playwright() as p:
        if action.lower().strip == "open":
            browser, context = launch_undetectable_browser(p)
            page = browser.new_page()
            page_ = page
            page.goto(url, timeout=10000)
            html_content = extract_tag_content(page.content())
            main_info_ = mainer(subject, html_content)

        if action.lower().strip() == "click":
            browser, context, page = browser_, context_, page_
            page.click(button_selector, timeout=30000)
            page.wait_for_load_state('domcontentloaded')
            html_content = extract_tag_content(page.content)
            main_info_ = mainer(subject, html_content)
            browser_, context_, page_ = browser, context, page

        if action.lower().strip() == "insert":
            browser, context, page = browser_, context_, page_
            for selector, text in field_data.items():
                if page.query_selector(selector):
                    for char in text:
                        page.fill(selector, page.input_value(selector) + char)
                        time.sleep(random.uniform(0.1, 0.3))
                    random_delay()
            main_info_ = mainer(extract_tag_content(page.content()), subject)








def handle_pagination(soup):
    """Find the next page URL if pagination exists."""
    next_button = soup.select_one(".next-page")  # Modify selector as needed
    return next_button["href"] if next_button else None


def create_folder(folder_name:str) -> str:
    """
    Creates a folder with the given folder name
    """
    os.makedirs(folder_name, exist_ok=True)
    return f"Folder created at: {os.getcwd()}"

def sanitize_filename(src):
    """Sanitize the filename from the URL."""
    parsed_url = urlparse(src)
    filename = os.path.basename(parsed_url.path)
    return unquote(filename) if filename else "file_from_src"


def save_media_from_src(src_url, media_type):
    """Download and save media (image/audio) using src URL."""
    try:
        response = requests.get(src_url, stream=True, timeout=10)
        response.raise_for_status()

        filename = sanitize_filename(src_url)
        folder = f"{media_type}s"
        os.makedirs(folder, exist_ok=True)

        with open(os.path.join(folder, filename), "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Saved {media_type}: {filename}")
    except Exception as e:
        print(f"Failed to save {media_type} from {src_url}: {e}")


def download_single_image(url:str) -> None:
    """Download a single image from the direct URL."""
    save_media_from_src(url, "image")


def download_all_images(url_list:list[str]) -> None:
    """Download multiple images from a list of direct URLs."""
    for url in url_list:
        save_media_from_src(url, "image")

def download_single_audio(url:str) -> None:
    """Download a single audio file from the direct URL."""
    save_media_from_src(url, "audio")


def download_all_audio(url_list:list[str]) -> None:
    """Download multiple audio files from a list of direct URLs."""
    for url in url_list:
        save_media_from_src(url, "audio")


def write_response_to_file(filename:str, text:str) -> str:
    with open(f"{filename}.txt", "w", encoding="utf-8") as f:
        f.write(text)
        f.close()
        return "File written to successfully"

def store_temp(data:dict, data_id:str) -> str:
    """
    Args:
        data: the dictionary where data is stored
        data_id: an identifier for the data
    
    Example:
        data["image_url"] = "https://xyz.com/image.jpeg"
    """
    DEFAULT_CACHE[data_id] = data
    return "Successfully added to cache"

def read_cache() -> dict:
    return DEFAULT_CACHE

def get_from_cache(data_id:str) -> Any: 
    return DEFAULT_CACHE[data_id]