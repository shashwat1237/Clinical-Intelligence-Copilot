from app.db.session import SessionLocal, engine
from app.db.models_and_crud import Base, create_user, create_patient_profile

def main():
    print("Creating tables and pgvector extension...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Seed test user (use UUID format to match Supabase)
        test_user_id = "00000000-0000-0000-0000-000000000000"
        print("Seeding test user...")
        create_user(db, test_user_id, "test@example.com")
        create_patient_profile(db, test_user_id)
        print("Database seeded successfully.")
    except Exception as e:
        print(f"Seed failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()

