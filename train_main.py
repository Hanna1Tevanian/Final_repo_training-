import pickle
import re
from datetime import datetime, timedelta

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
        self.tags = [] # Added field for tags

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

    @input_error
    def edit_contact_command(self, args):
        name, field, value = args
        record = self.find(name)
        if record:
            if field.lower() == "name":
                record.name.value = value
            elif field.lower() == "phone":
                old_phone = value.split(',')[0]
                new_phone = value.split(',')[1]
                record.edit_phone(old_phone, new_phone)
            elif field.lower() == "email":
                record.add_email(value)
            elif field.lower() == "address":
                record.add_address(value)
            elif field.lower() == "birthday":
                record.add_birthday(value)
            else:
                return "Invalid field name. Supported fields: name, phone, email, address, birthday."
            return f"{field.capitalize()} updated."
        else:
            return "Contact not found."

    @input_error
    def remove_contact_command(self, args):
        name = args[0]
        if self.remove_contact(name):
            return f"{name} removed from the address book."
        else:
            return "Contact not found."

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
            print(book.edit_contact_command(args))
        elif command == "search-by-tag":
            print(book.search_by_tag(args[0]))
        elif command == "sort-by-tags":
            print(book.sort_by_tags(args[0]))
        elif command == "phone":
            print(book.show_phone_command(args[0]))
        elif command == "all":
            print(book.show_all_command(args))
        elif command == "add-birthday":
            print(book.add_birthday_command(args))
        elif command == "show-birthday":
            print(book.show_birthday_command(args[0]))
        elif command == "birthdays":
            print(book.birthdays_command(args))
        elif command == "notes":
            print(book.show_notes_command(args[0]))
        elif command == "add-notes":
            print(book.add_notes_command(args))
        elif command == "add-tag":
            print(book.add_tag_command(args))
        elif command == "show-tags":
            print(book.show_tags_command(args[0]))
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