from sqlalchemy import Column, Integer, String, ForeignKey, REAL, DateTime, func
import datetime
from sqlalchemy.orm import mapped_column
from conectdb import Base


class User(Base):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    user_id = Column(Integer)
    balance = Column(REAL)
    n_card = Column(Integer)
    pay_pal = Column(Integer)
    
    def init__(self, username, user_id, balance, n_card, pay_pal):
        self.username = username
        self.user_id = user_id
        self.balance = balance
        self.n_card = n_card
        self.pay_pal = pay_pal
    
    
class Versamento(Base):
    __tablename__ = 'versamenti'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    username = Column(String)
    importo = Column(Integer)
    
    def init__(self, user_id, username, importo):
        self.user_id = user_id
        self.username = username
        self.importo = importo