import random
import string

from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

secret_key = ''.join(random.choice(
    string.ascii_uppercase + string.digits) for x in range(32))


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    email = Column(String(150))
    password_hash = Column(String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

    def __repr__(self):
        return "username: %s, email: %s, password: %s" % (
            self.username, self.email, self.password_hash)

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        user_id = data['id']
        return user_id



class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    def __repr__(self):
        return "id: %d, name: %s, user_id: %d" % (self.id, self.name, self.user_id)

    @property
    def serialize(self):
        """returns data in easily serializable format"""
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id
        }



class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(300))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    def __repr__(self):
        return "id: %d, name: %s, description: %s, category_id: %d, user_id: %d" % (
            self.id, self.name, self.description, self.category_id, self.user_id)

    @property
    def serialize(self):
        """returns data in easily serializable format"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category_id,
            "user_id": self.user_id
        }


DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user='postgres', pw='wwzzaa', url='127.0.0.1:5432', db='catalog')

engine = create_engine(DB_URL)


Base.metadata.create_all(engine)
