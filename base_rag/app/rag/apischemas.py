from pydantic import BaseModel

class Url(BaseModel):
    url: str

class Question(BaseModel):
    question: str