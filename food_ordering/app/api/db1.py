from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

DATABASE_URL = 'postgresql://ana:ana@localhost:5432/food_ordering'

engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Order(Base):
    __tablename__ = 'orders'

    item_id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)
    customer_id = Column(Integer, nullable=False)
    order_id = Column(Integer, nullable=False)

Base.metadata.create_all(engine)
