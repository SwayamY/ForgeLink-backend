from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import crud, models

# Ensure tables are created (if not already)
models.Base.metadata.create_all(bind=engine)

# Create a session
db: Session = SessionLocal()

# Test Data
long_url = "https://www.example.com"
short_url = "exmpl123"

# ✅ Test Create
print("Testing Create URL...")
created_url = crud.create_url(db, long_url, short_url)
print("Created:", created_url.id, created_url.long_url, created_url.short_url)

# ✅ Test Retrieve by Short URL
print("\nTesting Get by Short URL...")
retrieved_url = crud.get_url_by_short(db, short_url)
print("Retrieved:", retrieved_url.id, retrieved_url.long_url, retrieved_url.short_url)

# ✅ Test Retrieve by Long URL
print("\nTesting Get by Long URL...")
retrieved_long_url = crud.get_url_by_long(db, long_url)
print("Retrieved:", retrieved_long_url.id, retrieved_long_url.long_url, retrieved_long_url.short_url)

# ✅ Test Delete
print("\nTesting Delete URL...")
delete_status = crud.delete_url(db, short_url)
print("Deleted:", delete_status)

# ✅ Verify Deletion
print("\nVerifying Deletion...")
deleted_entry = crud.get_url_by_short(db, short_url)
print("Entry Exists After Deletion?", deleted_entry is not None)

# Close the database session
db.close()
