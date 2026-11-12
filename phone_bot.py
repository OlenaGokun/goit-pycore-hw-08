import logging
import os
import tempfile
import pickle
from functools import wraps
from pathlib import Path
from phone_book import AddressBook, Record

DATA_FILE = Path(__file__).resolve().parent / "addressbook.pkl"


def input_error(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            return f"Contact '{e.args[0]}' not found."
        except (ValueError, TypeError) as e:
            return str(e)

    return inner


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.lower()
    return cmd, *args


@input_error
def add_contact(args, book: AddressBook):
    if len(args) != 2:
        raise ValueError("Usage: add [name] [phone]")

    name, phone = args
    record = book.find(name)

    if record is None:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return "Contact added."

    record.add_phone(phone)
    return "Contact updated."


@input_error
def change_contact(args, book: AddressBook):
    if len(args) != 3:
        raise ValueError("Usage: change [name] [old phone] [new phone]")

    name, old_phone, new_phone = args
    record = book.find(name)

    if record is None:
        raise KeyError(name)

    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args, book: AddressBook):
    if len(args) != 1:
        raise ValueError("Usage: phone [name]")

    name = args[0]
    record = book.find(name)

    if record is None:
        raise KeyError(name)

    if not record.phones:
        return f"No phone numbers found for {record.name.value}."

    phones = "; ".join(phone.value for phone in record.phones)
    return f"{record.name.value}: {phones}"


@input_error
def show_all(book: AddressBook):
    if not book:
        return "No contacts found."

    return "\n".join(str(record) for record in book.data.values())


@input_error
def add_birthday(args, book: AddressBook):
    if len(args) != 2:
        raise ValueError("Usage: add-birthday [name] [DD.MM.YYYY]")

    name, birthday = args
    record = book.find(name)

    if record is None:
        raise KeyError(name)

    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book: AddressBook):
    if len(args) != 1:
        raise ValueError("Usage: show-birthday [name]")

    name = args[0]
    record = book.find(name)

    if record is None:
        raise KeyError(name)

    if record.birthday is None:
        return f"Birthday is not set for {record.name.value}."

    return f"{record.name.value}: {record.birthday}"


@input_error
def birthdays(args, book: AddressBook):
    if args:
        raise ValueError("Usage: birthdays")

    upcoming = book.get_upcoming_birthdays()

    if not upcoming:
        return "No upcoming birthdays."

    return "\n".join(
        f"{user['name']}: {user['congratulation_date']}"
        for user in upcoming
    )


def confirm_exit(book: AddressBook) -> bool:
    try:
        save_data(book)
        return True

    except (OSError, pickle.PickleError) as e:
        print(f"Failed to save address book: {e}")

        while True:
            choice = input(
                "Exit without saving? (yes/no): "
            ).strip().casefold()

            if choice in ("yes", "y"):
                return True

            if choice in ("no", "n"):
                return False

            print("Please enter yes or no.")


def save_data(book: AddressBook, filename = DATA_FILE):
    directory = os.path.dirname(os.path.abspath(filename))
    temp_filename = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=directory,
            delete=False
        ) as file:
            temp_filename = file.name
            pickle.dump(book, file)

        os.replace(temp_filename, filename)
        temp_filename = None

    finally:
        if temp_filename is not None:
            try:
                os.remove(temp_filename)
            except OSError as e:
                logging.warning(
                    "Failed to remove temporary file '%s': %s",
                    temp_filename,
                    e
                )

def load_data(filename = DATA_FILE) -> AddressBook:
    try:
        with open(filename, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return AddressBook()

def main():
    book = load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")

        if not user_input.strip():
            print("Invalid command.")
            continue

        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            if confirm_exit(book):
                print("Good bye!")
                break
            continue

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
