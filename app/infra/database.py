from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.domain.entities.texts import Base

engine = create_engine('sqlite:///tfidf.db', echo=False)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)