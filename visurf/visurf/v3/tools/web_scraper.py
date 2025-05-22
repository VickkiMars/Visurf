# tools/web_scraper.py
from playwright.async_api import async_playwright, Page, BrowserContext
from typing import List, Dict, Any, Optional
import asyncio
from bs4 import BeautifulSoup

class WebScraper:
    def __init__(self):
        self.browser = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def _initialize_browser(self):
        """Initializes the browser and context if not already initialized."""
        if not self.browser:
            self.browser = await async_playwright().start()
            self.context = await self.browser.chromium.launch(headless=True).new_context()
            self.context = await self.browser.chromium.launch(headless=True).new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            self.context.set_default_timeout(30000) # 30 seconds default timeout

    async def _get_page(self) -> Page:
        """Ensures a page is available, creates one if not."""
        await self._initialize_browser()
        if not self.page or self.page.is_closed():
            self.page = await self.context.new_page()
        return self.page

    async def navigate(self, url: str) -> Dict[str, Any]:
        """
        Navigates to a given URL and returns the page content and elements.
        """
        try:
            page = await self._get_page()
            print(f"WebScraper: Navigating to {url}")
            response = await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle") # Wait for network to be idle
            print(f"WebScraper: Navigated to {page.url}")

            html_content = await page.content()
            page_elements = self._extract_elements(html_content)

            return {
                "success": True,
                "url": page.url,
                "html_content": html_content,
                "page_elements": page_elements,
                "message": f"Successfully navigated to {page.url}"
            }
        except Exception as e:
            print(f"WebScraper Error (navigate): {e}")
            return {"success": False, "error": str(e), "url": url}

    async def click_element(self, selector: str) -> Dict[str, Any]:
        """
        Clicks an element identified by a CSS selector.
        """
        try:
            page = await self._get_page()
            print(f"WebScraper: Attempting to click selector: {selector}")
            await page.locator(selector).click(timeout=10000) # 10 seconds timeout for click
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_load_state("networkidle") # Wait for network to be idle

            html_content = await page.content()
            page_elements = self._extract_elements(html_content)

            return {
                "success": True,
                "url": page.url,
                "html_content": html_content,
                "page_elements": page_elements,
                "message": f"Successfully clicked element: {selector}"
            }
        except Exception as e:
            print(f"WebScraper Error (click_element): {e}")
            return {"success": False, "error": str(e), "selector": selector}

    async def type_text(self, selector: str, text: str) -> Dict[str, Any]:
        """
        Types text into an element identified by a CSS selector.
        """
        try:
            page = await self._get_page()
            print(f"WebScraper: Attempting to type '{text}' into selector: {selector}")
            await page.locator(selector).fill(text, timeout=10000) # 10 seconds timeout
            await page.wait_for_load_state("domcontentloaded")
            # No networkidle for type, as it might not trigger a new page load
            print(f"WebScraper: Typed into {selector}")

            html_content = await page.content()
            page_elements = self._extract_elements(html_content)

            return {
                "success": True,
                "url": page.url,
                "html_content": html_content,
                "page_elements": page_elements,
                "message": f"Successfully typed '{text}' into element: {selector}"
            }
        except Exception as e:
            print(f"WebScraper Error (type_text): {e}")
            return {"success": False, "error": str(e), "selector": selector, "text": text}

    async def extract_data(self, selector: str) -> Dict[str, Any]:
        """
        Extracts text content from elements identified by a CSS selector.
        Returns a list of texts found.
        """
        try:
            page = await self._get_page()
            print(f"WebScraper: Attempting to extract data using selector: {selector}")
            elements = await page.locator(selector).all_text_contents()
            extracted_texts = [text.strip() for text in elements if text.strip()]
            print(f"WebScraper: Extracted data for {selector}: {extracted_texts}")

            return {
                "success": True,
                "extracted_data": extracted_texts,
                "message": f"Successfully extracted data for selector: {selector}"
            }
        except Exception as e:
            print(f"WebScraper Error (extract_data): {e}")
            return {"success": False, "error": str(e), "selector": selector}

    def _extract_elements(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Parses HTML content using BeautifulSoup and extracts key interactive elements
        and their simplified representation (tags and attributes).
        This helps the Website Analyzer understand the page structure.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        elements = []
        interactive_tags = ['a', 'button', 'input', 'select', 'textarea']

        for tag in interactive_tags:
            for element in soup.find_all(tag):
                element_info = {
                    'tag': tag,
                    'text': element.get_text(strip=True),
                    'id': element.get('id'),
                    'name': element.get('name'),
                    'class': element.get('class'),
                    'href': element.get('href') if tag == 'a' else None,
                    'type': element.get('type') if tag == 'input' else None,
                    'value': element.get('value') if tag == 'input' or tag == 'button' else None
                }
                # Clean up None values
                cleaned_info = {k: v for k, v in element_info.items() if v is not None and v != []}
                elements.append(cleaned_info)

        # Add common text elements for context
        # You might want to refine this to avoid overwhelming the LLM
        # For example, only extract headings, or paragraphs near interactive elements
        for heading_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a', 'button', 'span', 'audio', 'form', 'img', 'table', 'ul', 'video']:
            for element in soup.find_all(heading_tag):
                text_content = element.get_text(strip=True)
                if text_content and len(text_content) > 10 and len(text_content) < 200: # Filter short/long texts
                    elements.append({
                        'tag': heading_tag,
                        'text': text_content,
                        'id': element.get('id'),
                        'class': element.get('class')
                    })
        return elements

    async def close(self):
        """Closes the browser instance."""
        if self.browser:
            print("WebScraper: Closing browser.")
            await self.browser.stop()
            self.browser = None
            self.context = None
            self.page = None

# Example of how you might use it (for testing purposes, not part of agent flow)
async def main():
    scraper = WebScraper()
    try:
        # Test navigation
        result = await scraper.navigate("https://www.google.com")
        print("Navigate Result:", result)

        if result["success"]:
            # Test typing into search bar (assuming Google's search input has name='q' or id='APjFqb')
            # You'll need to inspect the page to get the correct selector
            # For Google, the search input might be '[name="q"]' or '#APjFqb'
            # result_type = await scraper.type_text('[name="q"]', "langchain github")
            # print("Type Result:", result_type)

            # if result_type["success"]:
            #     # Test clicking search button (assuming Google's search button has name='btnK')
            #     # For Google, the search button is often an input with type="submit" and name="btnK"
            #     # result_click = await scraper.click_element('[name="btnK"]')
            #     # print("Click Result:", result_click)
            pass

    finally:
        await scraper.close()

if __name__ == "__main__":
    # To run this standalone for testing, use: python -m asyncio tools/web_scraper.py
    # or just: python tools/web_scraper.py
    asyncio.run(main())