from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models to register them with SQLAlchemy
from models.user import User
from models.document import Document
from models.result import Result
from models.institution_record import InstitutionRecord
