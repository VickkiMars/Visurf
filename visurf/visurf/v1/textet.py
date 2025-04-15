from surfer import open_website_and_insert_text_and_click

print(open_website_and_insert_text_and_click(subject="Manchester City", url="https://livescore.com", button_selector="button[class='Header_searchSubmit__YR_QS']", field_data={"input[placeholder='Search']": 'Manchester City'}))