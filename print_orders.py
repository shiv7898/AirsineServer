import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
import models

def print_orders():
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    print("--- USERS ---")
    users = session.query(models.User).all()
    for u in users:
        print(f"ID: {u.id}, Name: {u.name}, Email: {u.email}, Role: {u.role}")

    print("\n--- ORDERS ---")
    orders = session.query(models.Order).all()
    for o in orders:
        print(f"ID: {o.id}, UserID: {o.user_id}, ProductID: {o.product_id}, Qty: {o.quantity}, Date: {o.order_date}, Final: {o.final_amount}")

if __name__ == "__main__":
    print_orders()
