def hellp(word):
    BROWSER, CONTEXT, PAGE = None, None, None
    word = word[:3]
    word = list(word)
    BROWSER, CONTEXT, PAGE = word
    return BROWSER, CONTEXT, PAGE

def open():
    print(hellp("ajdkasjd"))

open()