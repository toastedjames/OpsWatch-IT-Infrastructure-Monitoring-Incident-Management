from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text
)

from datetime import datetime

from database import Base


class Metric(Base):

    __tablename__ = "metrics"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    cpu_percent = Column(
        Float,
        nullable=False
    )

    memory_percent = Column(
        Float,
        nullable=False
    )

    disk_percent = Column(
        Float,
        nullable=False
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )


class Incident(Base):

    __tablename__ = "incidents"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    incident_type = Column(
        String(100),
        nullable=False
    )

    severity = Column(
        String(30),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    status = Column(
        String(30),
        default="OPEN"
    )

    detected_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    resolved_at = Column(
        DateTime,
        nullable=True
    )


class Service(Base):

    __tablename__ = "services"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    url = Column(
        String(255),
        nullable=False
    )

    status = Column(
        String(30),
        default="UNKNOWN"
    )

    response_time = Column(
        Float,
        default=0
    )

    last_checked = Column(
        DateTime,
        nullable=True
    )