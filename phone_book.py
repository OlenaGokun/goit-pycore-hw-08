from collections import UserDict
from datetime import date, datetime, timedelta


class Field:
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise TypeError("Name must be a string")

        if not value.strip():
            raise ValueError("Name cannot be empty")

        super().__init__(value)

    @property
    def key(self) -> str:
        return self.value.casefold()


class Phone(Field):
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise TypeError("Phone must be a string")

        if len(value) != 10 or not value.isascii() or not value.isdigit():
            raise ValueError("Phone number must contain exactly 10 digits")

        super().__init__(value)


class Birthday(Field):
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise TypeError("Birthday must be a string")

        try:
            birthday = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

        super().__init__(birthday)

    @property
    def value(self) -> date:
        return self._value

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Record:
    def __init__(self, name: str):
        self._name = Name(name)
        self._phones = []
        self._birthday = None

    @property
    def name(self) -> Name:
        return self._name

    @property
    def phones(self) -> tuple[Phone, ...]:
        return tuple(self._phones)

    @property
    def birthday(self) -> Birthday | None:
        return self._birthday

    def add_phone(self, phone: str):
        self._phones.append(Phone(phone))

    def find_phone(self, phone: str) -> Phone | None:
        for phone_obj in self._phones:
            if phone_obj.value == phone:
                return phone_obj

        return None

    def remove_phone(self, phone: str):
        found_phone = self.find_phone(phone)

        if found_phone is not None:
            self._phones.remove(found_phone)

    def edit_phone(self, old_phone: str, new_phone: str):
        found_phone = self.find_phone(old_phone)

        if found_phone is None:
            raise ValueError(f"Phone number {old_phone} not found")

        new_phone_obj = Phone(new_phone)
        index = self._phones.index(found_phone)
        self._phones[index] = new_phone_obj

    def add_birthday(self, birthday: str):
        self._birthday = Birthday(birthday)

    def __str__(self):
        phones = "; ".join(p.value for p in self._phones)
        birthday = str(self._birthday) if self._birthday else "Not specified"

        return (
            f"Contact name: {self.name.value}, "
            f"phones: {phones}, "
            f"birthday: {birthday}"
        )


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.key] = record

    def find(self, name: str) -> Record | None:
        return self.data.get(name.casefold())

    def delete(self, name: str):
        self.data.pop(name.casefold(), None)

    def get_upcoming_birthdays(self) -> list[dict[str, str]]:
        today = date.today()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday = record.birthday.value

            # Підставляємо поточний рік
            try:
                birthday_this_year = birthday.replace(year=today.year)
            except ValueError:
                # Цей виняток можливий тільки якщо ми намагаємося створити 
                # 29 лютого у невисокосному році. В такому випадку вітаємо 1 березня.
                birthday_this_year = date(today.year, 3, 1)

            # Якщо день народження вже минув, беремо наступний рік
            if birthday_this_year < today:
                try:
                    birthday_this_year = birthday.replace(year=today.year + 1)
                except ValueError:
                    # 29 лютого у наступному невисокосному році
                    birthday_this_year = date(today.year + 1, 3, 1)

            # Перевіряємо найближчі 7 днів, включаючи сьогодні
            if (birthday_this_year - today).days >= 7:
                continue

            # Переносимо привітання з вихідних на понеділок
            weekday = birthday_this_year.weekday()
            if weekday >= 5:
                birthday_this_year += timedelta(days=7 - weekday)

            # Додаємо користувача до результату
            upcoming_birthdays.append({
                "name": record.name.value,
                "congratulation_date": birthday_this_year.strftime("%Y.%m.%d")
            })

        return upcoming_birthdays


if __name__ == "__main__":
    book = AddressBook()

    john = Record("John")
    john.add_phone("1234567890")
    john.add_birthday("15.11.1990")
    book.add_record(john)

    jane = Record("Jane")
    jane.add_phone("9876543210")
    jane.add_birthday("18.11.1995")
    book.add_record(jane)

    alex = Record("Alex")
    alex.add_phone("1112223333")
    book.add_record(alex)

    for record in book.data.values():
        print(record)

    print("\nUpcoming birthdays:")
    print(book.get_upcoming_birthdays())