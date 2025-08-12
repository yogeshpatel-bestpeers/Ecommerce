from pydantic import BaseModel


class User_Created(BaseModel):
    email : str
    first_name : str
    last_name : str
    passwords : str

class User_Login(BaseModel):
    email : str
    passwords : str