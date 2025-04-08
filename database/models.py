from sqlalchemy import Column, Integer, String
from database.database import Base

class Url_Short(Base):
    __tablename__ = "urls"
    
    id = Column(Integer, primary_key=True)
    short_code = Column(String, unique=True)
    original_url = Column(String)
    clicks = Column(Integer, default=0)