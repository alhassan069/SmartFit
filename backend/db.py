from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import URL

DATABASE_URL = "sqlite:///./test.db"
DB_URL = URL.create(
    drivername="postgresql",
    username="postgres",
    password="",
    host="localhost",
    database="hassan",
    port=5432
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()