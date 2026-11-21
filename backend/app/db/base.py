
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import models so SQLAlchemy registers all tables in Base.metadata.
from app.models import entities  # noqa: E402, F401
