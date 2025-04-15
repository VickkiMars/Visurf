from collections import Counter
class loop:
    def __init__(self, text):
        self.text = text

    def mod(self):
        letter_count = Counter(self.text)
        msl = list(letter_count.values())
        msl.sort(reverse=True)
        print(msl[:2])
        if letter_count[" "] == msl[0]:
            mostCommonLetter = [l for l in dict(letter_count).keys() if letter_count[l] == msl[1]]
        return mostCommonLetter
    
    def rep(self, let1, let2):
        self.text.replace(let1, let2)
        return self.text


tes = loop("Hello, it's me, i was wondering if after all these years youv'e lied to me, to go over evrything, they say love is california but i hope you'd like to sing hello from the other side, other side, i wish i had ten thousand lives, thousand live, to tell you i'm sorry for everything that i've done and no matter if you think i'm breaking your heart anymore")


while True:
    print(f"Most occuring letter: {tes.mod()}")
    user = input("Which letter would you like to replace: ")
    user2 = input(f"What would you like to replace {user} with: ")
    print(tes.rep(user, user2))
    