import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT")
            )
            self.cur = self.conn.cursor()
            self.create_table()
        except Exception as e:
            print("❌ Failed to connect to the database:", e)

    def create_table(self):
        try:
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                );
            """)
            self.conn.commit()
        except Exception as e:
            print("❌ Failed to create table:", e)
            self.conn.rollback()

    def insert(self, name, email, password):
        try:
            self.cur.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, password)
            )
            self.conn.commit()
            return 1  # success
        except psycopg2.errors.UniqueViolation:
            self.conn.rollback()
            return 0  # email already exists
        except Exception as e:
            print("❌ Error inserting user:", e)
            self.conn.rollback()
            return 0

    
    def get_user_by_email(self, email):
        try:
            self.cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = self.cur.fetchone()
            if user:
                return {
                    "id": user[0],
                    "name": user[1],
                    "email": user[2],
                    "password": user[3]  # hashed password
                }
            return None
        except Exception as e:
            print("❌ Error fetching user by email:", e)
            return None
