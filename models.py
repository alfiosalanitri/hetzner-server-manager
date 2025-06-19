from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass
from typing import Optional

db = SQLAlchemy()

class Project(db.Model):
    """Represents a Hetzner project with an encrypted API token."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    # Store the encrypted token as bytes in the database
    encrypted_api_token = db.Column(db.LargeBinary, nullable=False)

    def __repr__(self):
        return f'<Project {self.name}>'
    

@dataclass
class Server:
    id: int
    name: str
    status: Optional[str] = None
    ipv4: Optional[str] = None
    ipv6: Optional[str] = None