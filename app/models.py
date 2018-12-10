from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
import string
import random
from flask_login import UserMixin
from app import db

secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    email = db.Column(db.String(150))
    password_hash = db.Column(db.String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

    def __repr__(self):
        return "username: %s, email: %s, password: %s" % (self.username, self.email, self.password_hash)

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


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return "id: %d, name: %s" % (self.id, self.name)

    @property
    def serialize(self):
        """returns data in easily serializable format"""
        return {
            "id": self.id,
            "name": self.name
        }


class Item(db.Model):
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(300))
    category_id = db.Column(db.Integer, ForeignKey('category.id'))
    category = relationship(Category)

    def __repr__(self):
        return "id: %d, name: %s, description: %s, category_id: %d" % (
            self.id, self.name, self.description, self.category_id)

    @property
    def serialize(self):
        """returns data in easily serializable format"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category_id
        }
