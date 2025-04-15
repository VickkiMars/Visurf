from playwright.sync_api import sync_playwright as sp

def click(query):
    with sp() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.google.com")
        page.fill("textarea[name='q']", query)
        page.wait_for_selector('ul.G43f7e > li:first-child', timeout=5000)
        page.click('ul.G43f7e > li:first-child')
        page.wait_for_load_state('networkidle')
        browser.close()

s = "hello by"
click(s)
