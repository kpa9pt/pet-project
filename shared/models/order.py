from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from . import Base


class Order(Base):
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    status = Column(String, default="created")
    created_at = Column(DateTime, server_default=func.now(), default=func.now())
    # delivery_address = Column(String, nullable=True)  # новое поле

    def __str__(self):
        return (
            f"{self.__class__.__name__}("
            f"id={self.id}, "
            f"product_name={self.product_name!r}, "
            f"user_id={self.user_id}, "
            f"status={self.status!r})"
        )
