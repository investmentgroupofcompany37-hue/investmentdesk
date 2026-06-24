# wsgi.py
from app import app, init_db

# Initialize database when the app starts
print("🔄 Initializing database on Render...")
init_db()
print("✅ Database initialization complete")

if __name__ == "__main__":
    app.run()
