from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from database import Base
import datetime
class Product(Base): 
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    base_unit = Column(String, default='kg')
class PriceHistory(Base):
    __tablename__ = 'price_history'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    vendor = Column(String)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)