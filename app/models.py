from dataclasses import dataclass
from datetime import date
from typing import Literal

@dataclass
class User():
    id: int = None 
    name: str = None
    surname: str = None
    username: str = None
    email: str = None # TODO: proveri ali msm da je bespotrebno jer ima vec username
    phone: str = None
    date_of_birth: date = None
    bio: str = None
    role: Literal['admin', 'user'] = 'user'

if __name__ == '__main__':
    u = User()
    u.name = 'alek'
    print(u)
