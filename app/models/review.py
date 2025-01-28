from app.backend.db import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime
import sqlalchemy as sa


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    grade = Column(Integer)
    comment = Column(String)
    review_date = Column(DateTime, server_default=sa.text('now()'))
    user_id = Column(Integer, ForeignKey('users.id'))
    is_active = Column(Boolean, default=True)



