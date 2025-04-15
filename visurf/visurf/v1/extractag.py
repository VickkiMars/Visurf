import requests
from bs4 import BeautifulSoup

def extract_tag_content(page):
    soup = BeautifulSoup(page, "html.parser")

    # Tags you want to extract
    tags_to_extract = ['a', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']

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

# Example usage
#url = "https://www.yandex.com/search?text=time%20in%20Nigeria"
# url="https://time.is"
# results = extract_tag_content(url)

# for item in results:
#     print(f"<{item['tag']} {item['attributes']}> {item['text']}")

