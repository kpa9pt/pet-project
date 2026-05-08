from sqlalchemy import Column, Integer
from sqlalchemy.orm import declared_attr, declarative_base


class Base:
    @declared_attr
    def __tablename__(cls):
        # Например, Order → "orders"
        return f"{cls.__name__.lower()}s"

    id = Column(Integer, primary_key=True, index=True)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"


# Единая декларативная база для всего проекта
DeclarativeBase = declarative_base(cls=Base)
