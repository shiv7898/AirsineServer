import sys
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from auth import hash_password

def create_superadmin(name, email, password, phone):
    db = SessionLocal()
    try:
        # Check if any super admin already exists
        existing = db.query(models.User).filter(models.User.role == "super_admin").first()
        if existing:
            print("Error: A Super Admin already exists in the system!")
            return

        new_admin = models.User(
            name=name.strip(),
            email=email.lower().strip(),
            password=hash_password(password),
            role="super_admin",
            phone=phone,
            gender="Other",
            age=30,
            dob="1990-01-01",
            home_address="Admin HQ",
            area="Admin Area",
            district="Admin District",
            state="Admin State",
            pincode="000000",
        )
        db.add(new_admin)
        db.commit()
        print(f"Super admin '{name}' created successfully with email: {email}")
    except Exception as e:
        db.rollback()
        print(f"Failed to create super admin: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) == 5:
        create_superadmin(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("=== Super Admin Creation ===")
        name = input("Enter Full Name: ")
        email = input("Enter Email: ")
        password = input("Enter Password: ")
        phone = input("Enter Phone Number (10 digits): ")
        
        if name and email and password and phone:
            create_superadmin(name, email, password, phone)
        else:
            print("All fields are required!")
