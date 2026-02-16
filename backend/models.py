from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Column, JSON
from pydantic import EmailStr


class User(SQLModel, table=True):
    """User model for authentication."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True, index=True)
    hashed_password: str
    name: Optional[str] = None
    display_name: str
    initials: str = Field(default="U")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ScrapeHistory(SQLModel, table=True):
    """Scrape history model."""

    __tablename__ = "scrape_history"

    id: Optional[int] = Field(default=None, primary_key=True)
    pull_id: str = Field(unique=True, index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str  # success, error
    items_found: int = Field(default=0)
    error_message: Optional[str] = None


class ScrapeItem(SQLModel, table=True):
    """Individual scraped items."""

    __tablename__ = "scrape_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    pull_id: str = Field(foreign_key="scrape_history.pull_id", index=True)
    title: str
    url: str
    image_url: Optional[str] = None
    current_bid: float
    retail_price: Optional[float] = None
    deal_score: Optional[int] = None
    bids: int = Field(default=0)
    end_date: str
    interest_category: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Pydantic models for API
class UserCreate(SQLModel):
    """Schema for user creation."""

    email: EmailStr
    password: str
    name: Optional[str] = None


class UserLogin(SQLModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserResponse(SQLModel):
    """Schema for user response."""

    id: int
    email: str
    display_name: str
    initials: str


class Token(SQLModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None


class TokenData(SQLModel):
    """Token payload data."""

    user_id: Optional[int] = None
    email: Optional[str] = None


class ScrapeHistoryResponse(SQLModel):
    """Schema for scrape history response."""

    pull_id: str
    timestamp: datetime
    status: str
    items_found: int
    error: Optional[str] = None


class ScrapeItemResponse(SQLModel):
    """Schema for scrape item response."""

    title: str
    url: str
    image_url: Optional[str] = None
    current_bid: float
    retail_price: Optional[float] = None
    deal_score: Optional[int] = None
    bids: int
    end_date: str
    interest_category: str


class InterestCreate(SQLModel):
    """Schema for creating interest."""

    category: str
    keywords: str  # comma-separated


class ScheduleUpdate(SQLModel):
    """Schema for schedule update."""

    enabled: bool
