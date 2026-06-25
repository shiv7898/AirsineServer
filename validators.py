import re
from typing import Optional
from exception import ValidationException

def validate_email(email: str) -> str:
    """
    Validate email format
    Returns the email if valid, raises ValidationException if invalid
    """
    if not email:
        raise ValidationException("Email is required", field="email")
    
    # Email regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        raise ValidationException(
            "Invalid email format. Please provide a valid email address.",
            field="email"
        )
    
    # Check email length
    if len(email) > 255:
        raise ValidationException(
            "Email address is too long (maximum 255 characters)",
            field="email"
        )
    
    return email.lower().strip()

def validate_password(password: str) -> str:
    """
    Validate password strength
    Returns the password if valid, raises ValidationException if invalid
    """
    if not password:
        raise ValidationException("Password is required", field="password")
    
    if len(password) < 6:
        raise ValidationException(
            "Password must be at least 6 characters long",
            field="password"
        )
    
    if len(password) > 28:
        raise ValidationException(
            "Password is too long (maximum 28 characters)",
            field="password"
        )
    
    # Check for at least one letter and one number
    if not re.search(r'[A-Za-z]', password):
        raise ValidationException(
            "Password must contain at least one letter",
            field="password"
        )
    
    if not re.search(r'[0-9]', password):
        raise ValidationException(
            "Password must contain at least one number",
            field="password"
        )
    
    return password

def validate_phone(phone) -> str:
    """
    Validate phone number (Indian format)
    Returns the phone if valid, raises ValidationException if invalid
    """
    if phone is None:
        raise ValidationException("Phone number is required", field="phone")
    phone_str = str(phone).strip()
    if not phone_str:
        raise ValidationException("Phone number is required", field="phone")
    
    # Remove spaces, hyphens, and parentheses
    cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone_str)
    
    # Indian phone number: 10 digits, optionally starting with +91 or 91
    phone_pattern = r'^(\+91|91)?[6-9]\d{9}$'
    
    if not re.match(phone_pattern, cleaned_phone):
        raise ValidationException(
            "Invalid phone number. Please provide a valid 10-digit Indian mobile number.",
            field="phone"
        )
    
    # Return normalized format (10 digits only)
    if cleaned_phone.startswith('+91'):
        return cleaned_phone[3:]
    elif cleaned_phone.startswith('91'):
        return cleaned_phone[2:]
    
    return cleaned_phone

def validate_pincode(pincode) -> str:
    """
    Validate Indian pincode
    Returns the pincode if valid, raises ValidationException if invalid
    """
    if pincode is None:
        raise ValidationException("Pincode is required", field="pincode")
    pincode_str = str(pincode).strip()
    if not pincode_str:
        raise ValidationException("Pincode is required", field="pincode")
    
    # Indian pincode: 6 digits
    pincode_pattern = r'^\d{6}$'
    
    if not re.match(pincode_pattern, pincode_str):
        raise ValidationException(
            "Invalid pincode. Please provide a valid 6-digit Indian pincode.",
            field="pincode"
        )
    
    return pincode_str

def validate_age(age) -> str:
    """
    Validate age
    Returns the age if valid, raises ValidationException if invalid
    """
    if age is None:
        raise ValidationException("Age is required", field="age")
    age_str = str(age).strip()
    if not age_str:
        raise ValidationException("Age is required", field="age")
    
    try:
        age_int = int(age_str)
        if age_int < 0 or age_int > 150:
            raise ValidationException(
                "Age must be between 0 and 150",
                field="age"
            )
    except ValueError:
        raise ValidationException(
            "Age must be a valid number",
            field="age"
        )
    
    return age_str

def validate_role(role: str) -> str:
    """
    Validate user role
    Returns the role if valid, raises ValidationException if invalid
    """
    valid_roles = ["patient", "doctor", "distributor", "sub_admin", "super_admin", "admin"]  # ✅ ADDED ADMIN ROLES
    
    if not role:
        raise ValidationException("Role is required", field="role")
    
    if role.lower() not in valid_roles:
        raise ValidationException(
            f"Invalid role. Must be one of: {', '.join(valid_roles)}",
            field="role"
        )
    
    return role.lower()

def to_numeric_or_string(val):
    if val is None:
        return None
    val_str = str(val).strip()
    if not val_str:
        return ""
    try:
        if val_str.isdigit():
            return int(val_str)
        if '.' in val_str:
            return float(val_str)
        return int(val_str)
    except ValueError:
        return val_str