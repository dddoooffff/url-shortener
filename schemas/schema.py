from pydantic import BaseModel

class Url(BaseModel):
    id: int
    original_url: str
    short_code: str
    clicks: int
    
    class Config:
        orm_mode = True

class UrlCreate(BaseModel):
    original_url: str
