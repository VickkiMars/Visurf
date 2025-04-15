from collections.abc import Iterable

def flatten(lst):
    for item in lst:
        if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
            yield from flatten(item)
        else:
            yield item

data = {'tag': 'a', 'text': 'Manchester UnitedEngland', 'attributes': {'href': '/en/football/team/manchester-united/2810/overview/'}}
print("manchester" in str(data).lower())
print(str(data).lower())