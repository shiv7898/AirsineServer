import sys
import os

# Add parent directory to sys.path so we can import from database/app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import engine, SessionLocal, Base
import app.models as models
from sqlalchemy import text

def migrate():
    # 1. Ensure new tables are created
    print("Creating new database tables if they do not exist...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Drop foreign key constraints if they exist in PostgreSQL
        print("Dropping foreign key constraints if they exist...")
        db.execute(text("ALTER TABLE products DROP CONSTRAINT IF EXISTS products_distributor_id_fkey;"))
        db.execute(text("ALTER TABLE orders DROP CONSTRAINT IF EXISTS orders_user_id_fkey;"))
        db.execute(text("ALTER TABLE support_queries DROP CONSTRAINT IF EXISTS support_queries_user_id_fkey;"))
        db.execute(text("ALTER TABLE notifications DROP CONSTRAINT IF EXISTS notifications_user_id_fkey;"))
        db.execute(text("ALTER TABLE therapy_data DROP CONSTRAINT IF EXISTS therapy_data_patient_id_fkey;"))
        db.execute(text("ALTER TABLE machine_settings DROP CONSTRAINT IF EXISTS machine_settings_patient_id_fkey;"))
        db.execute(text("ALTER TABLE machine_settings DROP CONSTRAINT IF EXISTS machine_settings_doctor_id_fkey;"))
        db.execute(text("ALTER TABLE pdf_report_data DROP CONSTRAINT IF EXISTS pdf_report_data_user_id_fkey;"))
        db.commit()

        # 2. Fetch all users from the users table using a raw connection or direct query
        # Since SQLAlchemy User model definition has changed, querying models.User will only yield User columns.
        # But we can query raw SQL from 'users' table to read the old columns!
        print("Reading existing users from 'users' table...")
        conn = engine.connect()
        
        # Read all rows using raw SQL select
        result = conn.execute(Base.metadata.tables["users"].select()).fetchall()
        column_keys = Base.metadata.tables["users"].columns.keys()
        
        users_list = []
        for row in result:
            user_dict = dict(zip(column_keys, row))
            users_list.append(user_dict)
            
        print(f"Found {len(users_list)} total users in 'users' table.")
        
        migrated_distributors = 0
        migrated_staff = 0
        kept_users = 0
        
        for u in users_list:
            role = u.get("role")
            user_id = u.get("id")
            
            if role == "distributor":
                # Check if already migrated to avoid duplicates
                existing = db.query(models.Distributor).filter(
                    (models.Distributor.email == u["email"]) | (models.Distributor.custom_id == u["custom_id"])
                ).first()
                if not existing:
                    dist = models.Distributor(
                        custom_id=u.get("custom_id"),
                        name=u.get("name"),
                        email=u.get("email"),
                        password=u.get("password"),
                        role=u.get("role", "distributor"),
                        phone=u.get("phone"),
                        gender=u.get("gender"),
                        age=u.get("age"),
                        dob=u.get("dob"),
                        home_address=u.get("home_address"),
                        area=u.get("area"),
                        district=u.get("district"),
                        state=u.get("state"),
                        pincode=u.get("pincode"),
                        company_name=u.get("company_name"),
                        business_type=u.get("business_type"),
                        distributor_type=u.get("distributor_type"),
                        license_number=u.get("license_number"),
                        profile_image=u.get("profile_image"),
                        status=u.get("status", "Active"),
                        verification_status=u.get("verification_status", "Pending"),
                        created_at=u.get("created_at"),
                        last_login=u.get("last_login"),
                        commission=u.get("commission", 0.0),
                        discount=u.get("discount", 0.0)
                    )
                    db.add(dist)
                    migrated_distributors += 1
                
                # Delete from old table
                db.execute(Base.metadata.tables["users"].delete().where(Base.metadata.tables["users"].c.id == user_id))
                
            elif role == "super_admin":
                # Check if already migrated
                existing = db.query(models.SuperAdmin).filter(
                    (models.SuperAdmin.email == u["email"]) | (models.SuperAdmin.custom_id == u["custom_id"])
                ).first()
                if not existing:
                    staff = models.SuperAdmin(
                        custom_id=u.get("custom_id"),
                        name=u.get("name"),
                        email=u.get("email"),
                        password=u.get("password"),
                        role=u.get("role"),
                        phone=u.get("phone"),
                        gender=u.get("gender"),
                        age=u.get("age"),
                        dob=u.get("dob"),
                        home_address=u.get("home_address"),
                        area=u.get("area"),
                        district=u.get("district"),
                        state=u.get("state"),
                        pincode=u.get("pincode"),
                        profile_image=u.get("profile_image"),
                        status=u.get("status", "Active"),
                        created_at=u.get("created_at"),
                        last_login=u.get("last_login")
                    )
                    db.add(staff)
                    migrated_staff += 1
                
                # Delete from old table
                db.execute(Base.metadata.tables["users"].delete().where(Base.metadata.tables["users"].c.id == user_id))
                
            elif role in ["admin", "sub_admin"]:
                # Check if already migrated
                existing = db.query(models.AdminStaff).filter(
                    (models.AdminStaff.email == u["email"]) | (models.AdminStaff.custom_id == u["custom_id"])
                ).first()
                if not existing:
                    staff = models.AdminStaff(
                        custom_id=u.get("custom_id"),
                        name=u.get("name"),
                        email=u.get("email"),
                        password=u.get("password"),
                        role=u.get("role"),
                        phone=u.get("phone"),
                        gender=u.get("gender"),
                        age=u.get("age"),
                        dob=u.get("dob"),
                        home_address=u.get("home_address"),
                        area=u.get("area"),
                        district=u.get("district"),
                        state=u.get("state"),
                        pincode=u.get("pincode"),
                        permissions=u.get("permissions"),
                        profile_image=u.get("profile_image"),
                        status=u.get("status", "Active"),
                        created_at=u.get("created_at"),
                        last_login=u.get("last_login")
                    )
                    db.add(staff)
                    migrated_staff += 1
                
                # Delete from old table
                db.execute(Base.metadata.tables["users"].delete().where(Base.metadata.tables["users"].c.id == user_id))
                
            else:
                kept_users += 1
                
        db.commit()
        print(f"Migration completed successfully!")
        print(f"- Migrated Distributors: {migrated_distributors}")
        print(f"- Migrated Admin Staff: {migrated_staff}")
        print(f"- Kept Patients & Doctors: {kept_users}")
        
    except Exception as e:
        db.rollback()
        print(f"Migration failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
