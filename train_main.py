import pickle
import re
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Invalid phone number format. It should contain 10 digits.")
        super().__init__(value)

class Email(Field):
    def __init__(self, value):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError("Invalid email format.")
        super().__init__(value)

class Address(Field):
    pass

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError("Invalid birthday format. It should be in DD.MM.YYYY format.")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.email = None # Added field for email
        self.address = None # Added address field
        self.birthday = None
        self.notes = None # Added field for text notes
        self.tags = []  # Added field for tags

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def add_email(self, email):
        self.email = Email(email)

    def add_address(self, address):
        self.address = Address(address)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def add_notes(self, notes):
        self.notes = notes

    def add_tag(self, tag):
        self.tags.append(tag)

    def show_tags(self):
        return ', '.join(self.tags) if self.tags else "No tags"

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]

    def edit_phone(self, old_phone, new_phone):
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def find_phone(self, phone):
        for p in self.phones:
            if str(p) == phone:
                return p
        return None

    def show_notes(self):
        return str(self.notes) if self.notes else "No notes"

    def __str__(self):
        phones_str = '; '.join(str(p) for p in self.phones)
        email_str = str(self.email) if self.email else "Not specified"
        address_str = str(self.address) if self.address else "Not specified"
        birthday_str = str(self.birthday) if self.birthday else "Not specified"
        notes_str = self.show_notes()
        tags_str = self.show_tags()
        return f"Contact name: {self.name.value}, phones: {phones_str}, email: {email_str}, address: {address_str}, birthday: {birthday_str}, notes: {notes_str}, tags: {tags_str}"

class AddressBook:
    def __init__(self):
        self.data = {}

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_birthdays_per_week(self):
        today = datetime.now()
        next_week = today + timedelta(days=7)
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday_date = datetime.strptime(str(record.birthday), '%d.%m.%Y')
                if today <= birthday_date < next_week:
                    upcoming_birthdays.append(record.name.value)

        return upcoming_birthdays

    def save_to_file(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.data, file)

    def load_from_file(self, filename):
        try:
            with open(filename, 'rb') as file:
                self.data = pickle.load(file)
        except FileNotFoundError:
            self.data = {}

    def search_by_tag(self, tag):
        matching_records = [record for record in self.data.values() if tag in record.tags]
        return matching_records

    def sort_by_tags(self, tag):
        sorted_records = sorted(self.data.values(), key=lambda record: tag in record.tags)
        return sorted_records

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Invalid command or missing argument."

    return inner

@input_error
def add_contact_command(args, book):
    name, phone = args
    record = Record(name)
    record.add_phone(phone)
    book.add_record(record)
    return "Contact added."

@input_error
def change_contact_command(args, book):
    name, phone = args
    record = book.find(name)
    if record:
        record.edit_phone(record.phones[0], phone)  # Assume that the contact has only one phone
        return "Contact updated."
    else:
        return "Contact not found."

@input_error
def search_by_tag_command(args, book):
    tag = args[0]
    matching_records = book.search_by_tag(tag)
    if matching_records:
        return "\n".join(str(record) for record in matching_records)
    else:
        return "No contacts found with the specified tag."

@input_error
def sort_by_tags_command(args, book):
    tag = args[0]
    sorted_records = book.sort_by_tags(tag)
    if sorted_records:
        return "\n".join(str(record) for record in sorted_records)
    else:
        return "No contacts found with the specified tag."

@input_error
def show_phone_command(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.phones:
        return f"{name}'s phone: {record.phones[0]}"
    else:
        return "Contact not found or phone not specified."

@input_error
def show_all_command(args, book):
    if not book.data:
        return "No contacts found."
    else:
        return "\n".join(str(record) for record in book.data.values())

@input_error
def add_birthday_command(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        return "Contact not found."

@input_error
def show_birthday_command(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday: {record.birthday}"
    else:
        return "Contact not found or birthday not specified."

@input_error
def birthdays_command(args, book):
    upcoming_birthdays = book.get_birthdays_per_week()
    if upcoming_birthdays:
        return f"Upcoming birthdays: {', '.join(upcoming_birthdays)}"
    else:
        return "No upcoming birthdays."

@input_error
def show_notes_command(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.notes:
        return f"{name}'s notes: {record.show_notes()}"
    else:
        return "Contact not found or notes not specified."

@input_error
def add_notes_command(args, book):
    name, notes = args
    record = book.find(name)
    if record:
        record.add_notes(notes)
        return "Notes added."
    else:
        return "Contact not found."

@input_error
def add_tag_command(args, book):
    name, tag = args
    record = book.find(name)
    if record:
        record.add_tag(tag)
        return "Tag added."
    else:
        return "Contact not found."

@input_error
def show_tags_command(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.tags:
        return f"{name}'s tags: {record.show_tags()}"
    else:
        return "Contact not found or tags not specified."

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Goodbye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact_command(args, book))
        elif command == "change":
            print(change_contact_command(args, book))
        elif command == "search-by-tag":
            print(search_by_tag_command(args, book))
        elif command == "sort-by-tags":
            print(sort_by_tags_command(args, book))
        elif command == "phone":
            print(show_phone_command(args, book))
        elif command == "all":
            print(show_all_command(args, book))
        elif command == "add-birthday":
            print(add_birthday_command(args, book))
        elif command == "show-birthday":
            print(show_birthday_command(args, book))
        elif command == "birthdays":
            print(birthdays_command(args, book))
        elif command == "notes":
            print(show_notes_command(args, book))
        elif command == "add-notes":
            print(add_notes_command(args, book))
        elif command == "add-tag":
            print(add_tag_command(args, book))
        elif command == "show-tags":
            print(show_tags_command(args, book))
        elif command == "save":
            filename = input("Enter the filename to save: ")
            book.save_to_file(filename)
            print("Address book saved.")
        elif command == "load":
            filename = input("Enter the filename to load: ")
            book.load_from_file(filename)
            print("Address book loaded.")
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()