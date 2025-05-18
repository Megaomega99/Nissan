# backend/app/models/file.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from typing import Optional, List, Any

from app.core.database import Base
import json
from sqlalchemy.ext.hybrid import hybrid_property

class File(Base):
    """
    Model for representing uploaded CSV files in the database.
    
    Attributes:
        id: Unique identifier for the file
        filename: System filename for storage
        original_filename: Original name provided by the user
        file_path: Path to the file on disk
        file_size: Size of the file in bytes
        columns: JSON string of column names
        rows_count: Number of rows in the file
        is_processed: Flag indicating if preprocessing was applied
        processing_status: Current status of file processing
        user_id: Foreign key to the user who owns this file
        created_at: Timestamp when the file was created
        updated_at: Timestamp when the file was last updated
    """
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    
    # Metadata for the CSV
    columns = Column(Text, nullable=True)  # JSON serialized column names
    rows_count = Column(Integer, nullable=True)
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    processing_status = Column(String, default="pending")
    
    # Relationship with user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", backref="files")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Store JSON as string in database
    _columns = Column("columns", Text, nullable=True)
    
    # Add property to handle serialization/deserialization
    @hybrid_property
    def columns(self):
        """Convert stored JSON string to Python list."""
        if self._columns:
            try:
                return json.loads(self._columns)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    @columns.setter
    def columns(self, value):
        """Convert Python list to JSON string for storage."""
        if value is None:
            self._columns = None
        else:
            self._columns = json.dumps(value)
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<File(id={self.id}, filename={self.original_filename}, user_id={self.user_id})>"