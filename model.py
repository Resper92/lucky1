from sqlalchemy import Column, Integer, String, ForeignKey, REAL, DateTime,  BigInteger, Boolean
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
    
    
    def __init__(self, username, user_id,email, balance, demo_balance, is_admin):
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
    data_pagamento = Column(DateTime, default=datetime.timezone.utc)

    def __init__(self, invoice_id, user_id, username, importo, valuta, stato):
        self.invoice_id = invoice_id
        self.user_id = user_id
        self.username = username
        self.importo = importo
        self.valuta = valuta
        self.stato = stato