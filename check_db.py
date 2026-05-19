from sqlalchemy import create_engine, inspect
from config import settings

def check_columns():
    try:
        engine = create_engine(settings.DATABASE_URL)
        inspector = inspect(engine)
        columns = inspector.get_columns('orders')
        print("Columns in 'orders' table:")
        for column in columns:
            print(f"- {column['name']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_columns()
