data = [
    {
        'tag': 'a',
        'text': 'Manchester UnitedEngland',
        'attributes': {
            'href': '/en/football/team/manchester-united/2810/overview/'
        }
    },
    {
        'tag': 'div',
        'text': 'Other Team',
        'attributes': {
            'class': 'team-card'
        }
    }
]

# Word to search
word = "manchester"

# Case-insensitive search
matches = [
    item for item in data
    if any(
        word.lower() in str(k).lower() or word.lower() in str(v).lower()
        for k, v in item.items()
    ) or any(
        word.lower() in str(attr_k).lower() or word.lower() in str(attr_v).lower()
        for attr_k, attr_v in item.get("attributes", {}).items()
    )
]

print(matches)
