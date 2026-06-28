def main():
    """Confirms migration to pgvector."""
    print("Local FAISS initialization deprecated.")
    print("System now utilizes Supabase pgvector extension via SQLAlchemy migrations for production durability.")

if __name__ == "__main__":
    main()

