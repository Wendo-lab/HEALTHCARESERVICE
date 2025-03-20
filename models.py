from sqlalchemy import Column, Integer, String, VARCHAR, ForeignKey,DateTime,Date,Boolean
from configs.configs import Base
from sqlalchemy.orm import relationship
from datetime import datetime


class ClientNames(Base):
    __tablename__ = 'clientnames'
    id = Column(Integer, primary_key=True)
    client_name = Column(VARCHAR(255), nullable=False)
    cDetails = relationship("ExtraClientDetails", back_populates="client")
    AServicePlan = relationship("AnnualServicePlan", back_populates="client")
    ServicePlan = relationship("ServicePlan", back_populates="client")
    client_details = relationship("ClientDetails", back_populates="client")
    signout = relationship("SignOut", back_populates="client")


class ClientDetails(Base):
    __tablename__ = 'clientdetails'
    id = Column(Integer, primary_key=True)
    relationship_manager = Column(VARCHAR(50), nullable=False)
    co_handler = Column(VARCHAR(50), nullable=False)
    policy_period = Column(VARCHAR(50), nullable=False)
    premium = Column(VARCHAR(50), nullable=False)
    admin_fee = Column(VARCHAR(50), nullable=False)
    income = Column(VARCHAR(50), nullable=False)
    cover_type = Column(VARCHAR(50), nullable=False)
    non_government = Column(Boolean, default=False)
    government = Column(Boolean, default=False)
    client_main_contact = Column(VARCHAR(50), nullable=False)
    client_designation = Column(VARCHAR(50), nullable=False)
    client_cell = Column(VARCHAR(50), nullable=False)
    client_email = Column(VARCHAR(50), nullable=False)
    client_id = Column(Integer, ForeignKey('clientnames.id'))
    client = relationship("ClientNames", back_populates="client_details")
    

class ExtraClientDetails(Base):
    __tablename__ = 'extraclientdetails'
    id = Column(Integer, primary_key=True)
    other_client_personel = Column(VARCHAR(50), nullable=False)
    designation = Column(VARCHAR(50), nullable=False)
    cell = Column(VARCHAR(50), nullable=False)
    email = Column(VARCHAR(50), nullable=False)
    client_id = Column(Integer, ForeignKey('clientnames.id'))
    client = relationship("ClientNames", back_populates="cDetails")

class AnnualServicePlan(Base):
    __tablename__ = 'annualserviceplan'
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, nullable=False)  # Matches static question IDs
    selected_months = Column(VARCHAR(50), nullable=True)  # Stores selected months as a comma-separated string
    client_id = Column(Integer, ForeignKey('clientnames.id'))
    client = relationship("ClientNames", back_populates="AServicePlan")

class ServicePlan(Base):
    __tablename__ ='serviceplan'
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, nullable=False)  # Matches static question IDs
    response = Column(Boolean, nullable=True)  # Yes = True, No = False
    response_date = Column(Date, nullable=True)  # For date-type questions
    reason = Column(VARCHAR(50), nullable=True)  # For reason-type questions
    file_path = Column(String(255), nullable=True)
    client_id = Column(Integer, ForeignKey('clientnames.id'))
    client = relationship("ClientNames", back_populates="ServicePlan")
    
class SignOut(Base):
    __tablename__ ='signout'
    id = Column(Integer, primary_key=True)
    role = Column(String(50), nullable=False)
    confirmed_by = Column(String(50), nullable=True)
    status = Column(String(50), default="No")
    timestamp = Column(DateTime, default=datetime.utcnow)
    client_id = Column(Integer, ForeignKey('clientnames.id'))
    client = relationship("ClientNames", back_populates="signout")
