import requests
from bs4 import BeautifulSoup

def extract_relevant_elements_with_attributes(url, relevant_keywords):
    """
    Extracts HTML elements containing relevant keywords or sub-elements with keywords,
    and shows only class, href, id, and text.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        relevant_elements = []

        def process_element(element):
            """Extracts and formats relevant attributes and text."""
            element_data = {}
            if 'class' in element.attrs:
                element_data['class'] = element.attrs['class']
            if 'href' in element.attrs:
                element_data['href'] = element.attrs['href']
            if 'id' in element.attrs:
                element_data['id'] = element.attrs['id']
            element_data['text'] = element.get_text(strip=True) #get text, removing extra whitespace.
            return element_data

        def contains_relevant_text(element):
            """Checks if an element or its sub-elements contain relevant text."""
            if element.string and any(keyword.lower() in element.string.lower() for keyword in relevant_keywords):
                return True
            for child in element.descendants:
                if isinstance(child, str) and any(keyword.lower() in child.lower() for keyword in relevant_keywords):
                    return True
            return False

        for element in soup.find_all(True):
            if contains_relevant_text(element):
                relevant_elements.append(process_element(element))

        return relevant_elements

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return []

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Example usage:
url = "https://www.livescore.com/en/football/team/arsenal/2773/overview/"  # Replace with the target URL
keywords = ["arsenal"]  # Replace with your keywords

relevant_elements = extract_relevant_elements_with_attributes(url, keywords)

if relevant_elements:
    for element_data in relevant_elements:
        print(element_data)
        print("-" * 20)
else:
    print("No relevant elements found.")