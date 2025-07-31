from sqlalchemy import Column, Integer, String, ForeignKey, REAL, DateTime,  BigInteger, Boolean
import datetime
from sqlalchemy.orm import mapped_column
from conectdb import Base


class User(Base):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    user_id = Column(BigInteger, unique=True)
    email = Column(String)
    balance = Column(REAL)
    demo_balance = Column(REAL)
    is_admin = Column(Boolean, default=False)
    
    
    def init__(self, username, user_id,email, balance, demo_balance, is_admin):
        self.username = username
        self.user_id = user_id
        self.email = email
        self.balance = balance
        self.demo_balance = balance
        self.is_admin = is_admin

    
    
class Versamento(Base):
    __tablename__ = 'versamenti'
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('User.user_id'))
    username = Column(String)
    importo = Column(Integer)
    tipo = Column(String)
    
    def init__(self, user_id, username, importo,tipo):
        self.user_id = user_id
        self.username = username
        self.importo = importo
        self.tipo = tipo