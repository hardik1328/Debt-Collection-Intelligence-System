from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class Contract(Base):
    """Contract document model"""
    __tablename__ = "contracts"
    
    id = Column(String, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    file_path = Column(String)
    raw_text = Column(Text)
    pages = Column(Integer)
    file_size = Column(Integer)
    upload_date = Column(DateTime, default=datetime.utcnow, index=True)
    processed = Column(Integer, default=0)
    processing_time_ms = Column(Float, default=0)


class ExtractedFields(Base):
    """Extracted contract fields"""
    __tablename__ = "extracted_fields"
    
    id = Column(String, primary_key=True, index=True)
    contract_id = Column(String, index=True)
    parties = Column(JSON)
    effective_date = Column(String)
    term = Column(String)
    governing_law = Column(String)
    payment_terms = Column(String)
    termination = Column(String)
    auto_renewal = Column(String)
    confidentiality = Column(String)
    indemnity = Column(String)
    liability_cap = Column(JSON)
    signatories = Column(JSON)
    extraction_date = Column(DateTime, default=datetime.utcnow)
    extraction_time_ms = Column(Float, default=0)


class AuditFinding(Base):
    """Audit findings"""
    __tablename__ = "audit_findings"
    
    id = Column(String, primary_key=True, index=True)
    contract_id = Column(String, index=True)
    clause_type = Column(String)
    severity = Column(String)
    description = Column(Text)
    evidence = Column(JSON)
    recommendation = Column(Text)
    audit_date = Column(DateTime, default=datetime.utcnow)


class QueryLog(Base):
    """Query logging"""
    __tablename__ = "query_logs"
    
    id = Column(String, primary_key=True, index=True)
    question = Column(Text)
    answer = Column(Text)
    document_ids = Column(JSON)
    query_time_ms = Column(Float)
    query_date = Column(DateTime, default=datetime.utcnow)


class WebhookEvent(Base):
    """Webhook events"""
    __tablename__ = "webhook_events"
    
    id = Column(String, primary_key=True, index=True)
    url = Column(String)
    event_type = Column(String)
    task_id = Column(String)
    status = Column(String)
    payload = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)


def get_engine(database_url: str):
    """Create database engine"""
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    
    return create_engine(database_url, connect_args=connect_args)


def create_tables(database_url: str):
    """Create all tables"""
    engine = get_engine(database_url)
    Base.metadata.create_all(bind=engine)
    return engine


def get_session_local(database_url: str):
    """Create SessionLocal"""
    engine = get_engine(database_url)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
