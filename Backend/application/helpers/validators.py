import re


def validate_email(email):
    if not email or not isinstance(email, str):
        return False, "Email is required"

    email = email.strip()
    if not re.match(r'^[^@ \t\r\n]+@[^@ \t\r\n]+$', email):
        return False, "Invalid email format"

    return True, email


def validate_password(password):
    if not password or not isinstance(password, str):
        return False, "Password is required"

    password = password.strip()
    if len(password) < 5:
        return False, "Password must be at least 5 characters long"

    return True, password


def validate_name(name):
    if not name or not isinstance(name, str):
        return False, "Name is required"

    name = name.strip()
    if len(name) < 2:
        return False, "Name must be at least 2 characters long"

    return True, name


def validate_address(address):
    if not address or not isinstance(address, str):
        return False, "Address is required"

    address = address.strip()
    if len(address) < 5:
        return False, "Address must be at least 5 characters long"

    return True, address


def validate_pincode(pincode):
    if not pincode:
        return False, "Pincode is required"

    pincode_str = str(pincode).strip()
    if not pincode_str.isdigit() or len(pincode_str) != 6:
        return False, "Pincode must be a 6-digit number"

    return True, pincode_str


def validate_phone(phone):
    if not phone:
        return True, None

    phone = str(phone).strip()
    if not re.match(r'^\d{10}$', phone):
        return False, "Phone must be a 10-digit number"

    return True, phone


def validate_title(title):
    if not title or not isinstance(title, str):
        return False, "Title is required"

    title = title.strip()
    if len(title) < 5:
        return False, "Title must be at least 5 characters long"
    if len(title) > 200:
        return False, "Title must be at most 200 characters long"

    return True, title


def validate_description(description):
    if not description or not isinstance(description, str):
        return False, "Description is required"

    description = description.strip()
    if len(description) < 10:
        return False, "Description must be at least 10 characters long"

    return True, description


def validate_price(price):
    try:
        price_float = float(price)
        if price_float <= 0:
            return False, "Price must be greater than 0"
        return True, price_float
    except (ValueError, TypeError):
        return False, "Invalid price format"


def validate_amount(amount):
    try:
        amount_float = float(amount)
        if amount_float <= 0:
            return False, "Amount must be greater than 0"
        return True, amount_float
    except (ValueError, TypeError):
        return False, "Invalid amount format"
