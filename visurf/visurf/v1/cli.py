import time
from InquirerPy import inquirer
from InquirerPy.utils import color_print
from requests.exceptions import RequestException
from function_caller import chat

# Function to simulate text input from the user
def ask_for_input():
    while True:
        try:
            answer = inquirer.text(
                message="Enter your prompt (or press Enter to exit): ",
                default=""
            ).execute()

            # Pressing Enter with no input exits
            if not answer.strip():
                result = inquirer.text(message="Exiting VISURF. Goodbye!").execute()
                exit(0)

            color_print([("blue",f"\nLoading...")])
            color_print([("blue",f"\nSearching the web...\n")])

            data = chat.send_message(answer)
            if data.text:
                color_print([("yellow",f"{data.text}")])

            # Ask user if they want to continue or exit
            follow_up = inquirer.text(
                message="Ask another question or press Enter to exit: ",
                default=""
            ).execute()

            if not follow_up.strip():
                print("Exiting VISURF. Goodbye!")
                exit(0)
            else:
                answer = chat.send_message(follow_up)
                if answer.text:
                    print(f"\n{answer.text}\n")

        except ValueError as ve:
            print(f"Input Error: {ve}")
        except Exception as e:
            print(f"Unexpected Error: {e}")

# Function to display the main menu and interact with the user
def main_menu():
    try:
        print("VISURF!!!\n")
        while True:
            choice = inquirer.select(
                message="What would you like to do?",
                choices=["Enter a prompt", "Exit"],
                default="Enter a prompt"
            ).execute()

            if choice == "Enter a prompt":
                ask_for_input()
            else:
                print("Exiting VISURF. Goodbye!")
                break
    except KeyboardInterrupt:
        print("\nOperation cancelled by user. Exiting...")
        exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)

# Main function to start the application
if __name__ == "__main__":
    main_menu()
