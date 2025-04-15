from InquirerPy import inquirer
from InquirerPy.utils import color_print

# Example usage
color_print(["red", "hello"])

result = inquirer.text(message="Enter some text:").execute()

print(f"You entered: {result}")

question = inquirer.text(
    message="What is your favorite color?"
).execute()

print(f"Your favorite color is: {question}")