# db/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Update with your actual credentials and database name
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://myuser:mypassword@localhost:5432/mydatabase")
TEST_DATABASE_URL = "postgresql://myuser:mypassword@localhost:5432/test_database"
# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=True  # echo=True logs all SQL to stdout (helpful for debugging)
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()
