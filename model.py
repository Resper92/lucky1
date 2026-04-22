from sqlalchemy import Column, Integer, BigInteger, String, DateTime, REAL, ForeignKey, func, Boolean
import datetime
from sqlalchemy.orm import mapped_column
from conectdb_Roman import Base


class User(Base):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    user_id = Column(BigInteger, unique=True)
    email = Column(String)
    balance = Column(REAL)
    demo_balance = Column(REAL)
    is_admin = Column(Boolean, default=False)
    
    
    def __init__(self, user_id, username, balance=0, demo_balance=100, email="", is_admin=False):
        self.username = username
        self.user_id = user_id
        self.email = email
        self.balance = balance
        self.demo_balance = demo_balance
        self.is_admin = is_admin

    
    
class Versamento(Base):
    __tablename__ = 'versamenti'
    id = Column(Integer, primary_key=True)
    invoice_id = Column(BigInteger, unique=True, nullable=False) 
    user_id = Column(BigInteger, ForeignKey('User.user_id')) 
    
    username = Column(String)
    importo = Column(REAL) 
    valuta = Column(String) 
    stato = Column(String)  
    data_pagamento = Column(DateTime, server_default=func.now())
    
    def __init__(self, invoice_id, user_id, username, importo, valuta, stato):
        self.invoice_id = invoice_id
        self.user_id = user_id
        self.username = username
        self.importo = importo
        self.valuta = valuta
        self.stato = stato
        self.data_pagamento = datetime.datetime.now()