import os
import sys
from flask import Flask
from flask_migrate import upgrade, stamp
from sqlalchemy import inspect, text

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Book, Author, Rating, UserLibrary, Admin

def table_exists(table_name):
    """Check if a table exists in the database"""
    inspector = inspect(db.engine)
    return table_name in inspector.get_table_names()

def is_database_empty():
    """Check if essential tables are empty"""
    try:
        # Check if tables exist first
        if not table_exists('usuarios') or not table_exists('libros'):
            return True
        
        # Check if tables are empty
        user_count = db.session.query(User).count()
        book_count = db.session.query(Book).count()
        admin_count = db.session.query(Admin).count()
        
        return user_count == 0 and book_count == 0 and admin_count == 0
    except Exception as e:
        print(f"⚠️  Error checking database state: {e}")
        return True

def run_migrations():
    """Run database migrations"""
    try:
        print("🔄 Running database migrations...")
        
        # Check if alembic_version table exists
        if not table_exists('alembic_version'):
            print("📌 Initializing migration tracking...")
            # If migrations folder exists but DB has no history, stamp it
            try:
                stamp()
                print("✅ Migration tracking initialized")
            except Exception as e:
                print(f"⚠️  Could not stamp database: {e}")
        
        # Run migrations
        upgrade()
        print("✅ Migrations completed successfully")
        return True
    except Exception as e:
        print(f"❌ Migration error: {e}")
        # If migrations fail, try creating tables directly
        print("🔄 Attempting to create tables directly...")
        try:
            db.create_all()
            print("✅ Tables created successfully")
            return True
        except Exception as e2:
            print(f"❌ Could not create tables: {e2}")
            return False

def seed_database():
    """Import and run the seed script"""
    try:
        print("🌱 Seeding database with initial data...")
        from app.seed import seed_database as run_seed
        run_seed()
        print("✅ Database seeded successfully")
        return True
    except Exception as e:
        print(f"❌ Seeding error: {e}")
        return False

def main():
    """Main initialization function"""
    print("=" * 60)
    print("🚀 INITIALIZING DATABASE FOR RENDER DEPLOYMENT")
    print("=" * 60)
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        # Step 1: Run migrations
        print("\n📊 Step 1: Database Migrations")
        if not run_migrations():
            print("❌ Failed to set up database structure")
            sys.exit(1)
        
        # Step 2: Check if database needs seeding
        print("\n🔍 Step 2: Checking Database State")
        if is_database_empty():
            print("📭 Database is empty - proceeding with seeding")
            
            if not seed_database():
                print("⚠️  Seeding failed, but database structure is ready")
                # Don't exit with error - structure is ready even if seeding failed
        else:
            print("✅ Database already contains data - skipping seed")
        
        # Step 3: Verify database state
        print("\n📈 Step 3: Database Summary")
        try:
            print(f"   👥 Users: {User.query.count()}")
            print(f"   👨‍💼 Admins: {Admin.query.count()}")
            print(f"   ✍️  Authors: {Author.query.count()}")
            print(f"   📚 Books: {Book.query.count()}")
            print(f"   ⭐ Ratings: {Rating.query.count()}")
            print(f"   📖 Library Items: {UserLibrary.query.count()}")
        except Exception as e:
            print(f"   ⚠️  Could not retrieve counts: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 DATABASE INITIALIZATION COMPLETE")
        print("=" * 60)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
