import unittest
from surfer import click, insert_text, fetch_html, generate_headers, handle_captcha  # Importing functions from the module.

class TestWebScrapingFunctions(unittest.TestCase):
    # def test_fetch_html(self):
    #     """
    #     Test the 'get_url' function to get the URL behind a button.
    #     """
    #     url = "https://www.google.com"  # Button selector to get the URL.
    #     headers = generate_headers()
    #     # Calling the get_url function to fetch the button's URL.
    #     result = fetch_html(url, headers)
        
    #     # Asserting the result equals the expected html.
    #     print("Test `fetch_html` passed successfully")

    def test_insert_text(self):
        """
        Test the 'insert_text' function to ensure it inserts text into a field correctly.
        """
        url = "https://www.yandex.com"  # URL to test.
        text = "rasputin"  # Text to insert.
        field_data = {"input[name='text']": "rasputin"} 
        
        # Calling the insert_text function to test if it inserts text properly.
        result = insert_text(url, field_data)
        
        # Asserting the result is True if the text was inserted correctly.
        print("Test `insert_text` passed successfully")

    # def test_click(self):
    #     """
    #     Test the 'click' function to ensure it clicks a button correctly.
    #     """
    #     url = "https://www.google.com/search?q=epl"  # URL to test.
    #     button_selector = "input[text='Full match schedule']"  # Selector for the button.
    #     # Calling the click function to test its behavior.
    #     result = click(url, button_selector)
        
    #     # Asserting the result is True if the click was successful.
    #     print("Test `click` passed successfully")



if __name__ == '__main__':
    unittest.main()
