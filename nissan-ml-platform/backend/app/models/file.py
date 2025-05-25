# backend/app/models/file.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import json

from app.core.database import Base

class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    _columns = Column("columns", Text, nullable=True)
    rows_count = Column(Integer, nullable=True)
    is_processed = Column(Boolean, default=False)
    processing_status = Column(String, default="pending")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    @property
    def columns(self):
        if self._columns:
            try:
                return json.loads(self._columns)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    @columns.setter
    def columns(self, value):
        if value is None:
            self._columns = None
        else:
            self._columns = json.dumps(value)
    
    def __repr__(self) -> str:
        return f"<File(id={self.id}, filename={self.original_filename}, user_id={self.user_id})>"