import pickle
import re
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
console = Console()
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
    def edit_email(self, new_email):
        self.email = Email(new_email)
    def edit_name(self, new_name):
        self.name = Name(new_name)
    def edit_address(self, new_address):
        self.address = Address(new_address)
    def edit_birthday(self, new_birthday):
        self.birthday = Birthday(new_birthday)    
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
    def remove_email(self):
        self.email = None
    def remove_address(self):
        self.address = None
    def remove_birthday(self):
        self.birthday = None
    def remove_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)
    def remove_all_tags(self):
        self.tags = []
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

    def find_by_phone(self, phone):
        for record in self.data.values():
            if any(str(p) == phone for p in record.phones):
                return record
        return None    

    def find_by_email(self, email):
        for record in self.data.values():
            if record.email and str(record.email) == email:
                return record
        return None

    def delete_contact(self, name):
        if name in self.data:
            del self.data[name]
    def delete_email(self, name):
        record = self.find(name)
        if record and record.email:
            record.remove_email()
    def delete_address(self, name):
        record = self.find(name)
        if record and record.address:
            record.remove_address()
    def delete_phone(self, name, phone):
        record = self.find(name)
        if record and record.find_phone(phone):
            record.remove_phone(phone)
    def delete_birthday(self, name):
        record = self.find(name)
        if record and record.birthday:
            record.remove_birthday()
    def delete_all_tags(self, name):
        record = self.find(name)
        if record:
            record.remove_all_tags()
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
def delete_contact_command(args, book):
    name = args[0]
    book.delete_contact(name)
    return f"Contact '{name}' deleted."
@input_error
def delete_email_command(args, book):
    name = args[0]
    book.delete_email(name)
    return f"Email for contact '{name}' deleted."
@input_error
def delete_address_command(args, book):
    name = args[0]
    book.delete_address(name)
    return f"Address for contact '{name}' deleted."
@input_error
def delete_phone_command(args, book):
    name, phone = args
    book.delete_phone(name, phone)
    return f"Phone number '{phone}' for contact '{name}' deleted."
@input_error
def delete_birthday_command(args, book):
    name = args[0]
    book.delete_birthday(name)
    return f"Birthday for contact '{name}' deleted."
@input_error
def delete_all_tags_command(args, book):
    name = args[0]
    book.delete_all_tags(name)
    return f"All tags for contact '{name}' deleted."
@input_error
def change_email_command(args, book):
    name, new_email = args
    record = book.find(name)
    if record:
        if record.email:
            record.edit_email(new_email)
            return "Email updated."
        else:
            record.add_email(new_email)
            return "Email added."
    else:
        return "Contact not found."
@input_error
def change_name_command(args, book):
    old_name, new_name = args
    record = book.find(old_name)
    if record:
        record.edit_name(new_name)
        book.data[new_name] = book.data.pop(old_name)
        return "Name updated."
    else:
        return "Contact not found."
@input_error
def change_address_command(args, book):
    name, new_address = args
    record = book.find(name)
    if record:
        if record.address:
            record.edit_address(new_address)
            return "Address updated."
        else:
            record.add_address(new_address)
            return "Address added."
    else:
        return "Contact not found."
@input_error
def change_phone_command(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        if record.find_phone(old_phone):
            record.edit_phone(old_phone, new_phone)
            return "Phone number updated."
        else:
            record.add_phone(new_phone)
            return "Phone number added."
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
    """Creating output rich styles for the "all" command"""
    table = Table(show_header=True, header_style="bold yellow")
    table.add_column("Name", style="bold bright_blue")
    table.add_column("Phone", style="bold white")
    table.add_column("Email", style="bold bright_blue")
    table.add_column("Address", style="bold white")
    table.add_column("Birthday", style="bold bright_blue")
    table.add_column("Notes", style="bold white")
    table.add_column("Tags", style="bold bright_blue")
    for name, record in book.data.items():
        phones_str = '; '.join(str(p) for p in record.phones)
        email_str = str(record.email) if record.email else "Not specified"
        address_str = str(record.address) if record.address else "Not specified"
        birthday_str = str(record.birthday) if record.birthday else "Not specified"
        notes_str = record.show_notes()
        tags_str = record.show_tags()
        table.add_row(name, phones_str, email_str, address_str, birthday_str, notes_str, tags_str)
    console.print(table)
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
def rich_print(*args, **kwargs):
    """Sets the "bold bright_blue" style for output if no other style has been specified"""
    kwargs.setdefault("style", "bold bright_blue")
    console.print(*args, **kwargs)
    
@input_error
def rich_input(prompt):
    """Sets the "bold yellow" style for input if no other style has been specified"""
    console.print(prompt, end="", style="bold yellow")
    return input()
def show_help_command():
    """Initialize the console and table"""
    console = Console()
    table = Table(show_header=True, header_style="bold dark_blue")
    # Define the columns for the table
    table.add_column("Command", justify="left")
    table.add_column("Description", justify="left")
    table.add_column("Example", justify="left")
    # List of commands and descriptions for the application
    commands = [
        ("hello", "Greets the user", "hello"),
        ("add <name> <phone>", "Adds a new contact with the specified name and phone number", "add John 1234567890"),
        ("change <name> <new phone>", "Updates the phone number for the specified contact", "change John 0987654321"),
        ("phone <name>", "Shows the phone number of the specified contact", "phone John"),
        ("all", "Displays all contacts in the address book", "all"),
        ("add-birthday <name> <birthday>", "Adds a birthday to the specified contact", "add-birthday John 01.01.1990"),
        ("show-birthday <name>", "Shows the birthday of the specified contact", "show-birthday John"),
        ("birthdays", "Lists upcoming birthdays within the next week", "birthdays"),
        ("add-notes <name> <notes>", "Adds notes to the specified contact", "add-notes John Note1"),
        ("show-notes <name>", "Shows the notes of the specified contact", "show-notes John"),
        ("add-tag <name> <tag>", "Adds a tag to the specified contact", "add-tag John friend"),
        ("show-tags <name>", "Shows the tags of the specified contact", "show-tags John"),
        ("search-by-tag <tag>", "Searches for contacts by tag", "search-by-tag friend"),
        ("sort-by-tags <tag>", "Sorts contacts by tag", "sort-by-tags friend"),
        ("save", "Saves the address book to a file", "save mybook.pkl"),
        ("load", "Loads the address book from a file", "load mybook.pkl"),
        ("change-contact <name> <new phone>", "Changes the contact's phone number", "change-contact John 9876543210"),
        ("delete-email <name>", "Deletes the email of the specified contact", "delete-email John"),
        ("delete-address <name>", "Deletes the address of the specified contact", "delete-address John"),
        ("delete-phone <name> <phone>", "Deletes a specific phone number for the contact", "delete-phone John 1234567890"),
        ("delete-birthday <name>", "Deletes the birthday of the specified contact", "delete-birthday John"),
        ("delete-all-tags <name>", "Deletes all tags from the specified contact", "delete-all-tags John"),
    ]
    # Fill the table with the commands and their descriptions
    for command, description, example in commands:
        table.add_row(command, description, example)
    # Print the table to the console
    console.print(table)
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args
def main():
    book = AddressBook()
    rich_print("Welcome to the assistant bot!")
    while True:
        user_input = rich_input("Enter a command: ")
        command, args = parse_input(user_input)
        if command in ["close", "exit"]:
            rich_print("Goodbye!", style="bold white")
            break
        elif command == "help":
            show_help_command()
        elif command == "hello":
            rich_print("How can I help you?")
        elif command == "add":
            rich_print(add_contact_command(args, book), style="bold white")
        elif command == "change":
            rich_print(change_contact_command(args, book))
        elif command == "search-by-tag":
            rich_print(search_by_tag_command(args, book))
        elif command == "sort-by-tags":
            rich_print(sort_by_tags_command(args, book))
        elif command == "phone":
            rich_print(show_phone_command(args, book))
        elif command == "find-by-phone":
            phone = args[0]
            record = book.find_by_phone(phone)
            rich_print(f"Contact found: {record}" if record else "Contact not found.")
        elif command == "find-by-email":
            email = args[0]
            record = book.find_by_email(email)
            rich_print(f"Contact found: {record}" if record else "Contact not found.")        
        elif command == "all":
            print(show_all_command(args, book))
            rich_print(show_all_command(args, book))
        elif command == "add-birthday":
            rich_print(add_birthday_command(args, book), style="bold white")
        elif command == "show-birthday":
            rich_print(show_birthday_command(args, book), style="bold white")
        elif command == "birthdays":
            rich_print(birthdays_command(args, book), style="bold white")
        elif command == "notes":
            rich_print(show_notes_command(args, book))
        elif command == "add-notes":
            rich_print(add_notes_command(args, book))
        elif command == "add-tag":
            rich_print(add_tag_command(args, book))
        elif command == "show-tags":
            rich_print(show_tags_command(args, book))
        elif command == "delete-contact":
            rich_print(delete_contact_command(args, book))
        elif command == "delete-email":
            rich_print(delete_email_command(args, book))
        elif command == "delete-address":
            rich_print(delete_address_command(args, book))
        elif command == "delete-phone":
            rich_print(delete_phone_command(args, book))
        elif command == "delete-birthday":
            rich_print(delete_birthday_command(args, book))
        elif command == "delete-all-tags":
            rich_print(delete_all_tags_command(args, book))
        elif command == "save":
            filename = input("Enter the filename to save: ")
            book.save_to_file(filename)
            rich_print("Address book saved.")
        elif command == "load":
            filename = input("Enter the filename to load: ")
            book.load_from_file(filename)
            rich_print("Address book loaded.")
        else:
            rich_print("Invalid command.")
if __name__ == "__main__":
    main()