from pydantic import BaseModel

class UserOut(BaseModel):
    username: str

class UserSchema(UserOut):
    password: str
    
class ChangePassword(BaseModel):
    old_password: str
    new_password: str