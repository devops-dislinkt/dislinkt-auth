from dataclasses import dataclass
from typing import Literal


@dataclass
class User:
    username: str = None  # ID
    password: str = None
    role: Literal["admin", "user"] = "user"


if __name__ == "__main__":
    u = User()
    u.name = "alek"
    print(u)
