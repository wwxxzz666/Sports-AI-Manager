import uuid
from datetime import datetime, date
from sqlalchemy import String, Integer, Float, Boolean, Text, Date, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    nickname: Mapped[str] = mapped_column(String(50), default="用户")
    avatar_url: Mapped[str] = mapped_column(String(500), default="")
    gender: Mapped[str] = mapped_column(String(10), default="")
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    fitness_goal: Mapped[str] = mapped_column(String(100), default="")
    daily_calorie_goal: Mapped[int] = mapped_column(Integer, default=2200)
    hashed_password: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    conversations: Mapped[list["Conversation"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    diet_records: Mapped[list["DietRecord"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    health_metrics: Mapped[list["HealthMetric"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    ai_ratings: Mapped[list["AIRating"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    workout_records: Mapped[list["WorkoutRecord"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    agent_type: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(100), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id"), index=True)
    role: Mapped[str] = mapped_column(String(20))  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, default="")
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")


class DietRecord(Base):
    __tablename__ = "diet_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    meal_type: Mapped[str] = mapped_column(String(20))  # breakfast, lunch, dinner, snack
    image_url: Mapped[str] = mapped_column(String(500), default="")
    total_calories: Mapped[float] = mapped_column(Float, default=0)
    total_protein: Mapped[float] = mapped_column(Float, default=0)
    total_carbs: Mapped[float] = mapped_column(Float, default=0)
    total_fat: Mapped[float] = mapped_column(Float, default=0)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    record_date: Mapped[date] = mapped_column(Date, default=date.today)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="diet_records")
    food_items: Mapped[list["FoodItem"]] = relationship(back_populates="diet_record", cascade="all, delete-orphan")


class FoodItem(Base):
    __tablename__ = "food_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    diet_record_id: Mapped[str] = mapped_column(String(36), ForeignKey("diet_records.id"), index=True)
    food_name: Mapped[str] = mapped_column(String(100))
    portion_description: Mapped[str] = mapped_column(String(100), default="")
    portion_grams: Mapped[float] = mapped_column(Float, default=0)
    calories: Mapped[float] = mapped_column(Float, default=0)
    protein_g: Mapped[float] = mapped_column(Float, default=0)
    carbs_g: Mapped[float] = mapped_column(Float, default=0)
    fat_g: Mapped[float] = mapped_column(Float, default=0)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    user_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)

    diet_record: Mapped["DietRecord"] = relationship(back_populates="food_items")


class HealthMetric(Base):
    __tablename__ = "health_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    metric_date: Mapped[date] = mapped_column(Date, default=date.today)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    body_fat_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    bmi: Mapped[float | None] = mapped_column(Float, nullable=True)
    daily_step_count: Mapped[int] = mapped_column(Integer, default=0)
    sleep_minutes: Mapped[int] = mapped_column(Integer, default=0)
    calories_burned: Mapped[int] = mapped_column(Integer, default=0)
    exercise_minutes: Mapped[int] = mapped_column(Integer, default=0)
    heart_rate_avg: Mapped[int] = mapped_column(Integer, default=0)
    extra: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    user: Mapped["User"] = relationship(back_populates="health_metrics")


class AIRating(Base):
    __tablename__ = "ai_ratings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    composite_score: Mapped[float] = mapped_column(Float, default=0)
    tier: Mapped[str] = mapped_column(String(20), default="青铜")
    percentile: Mapped[float] = mapped_column(Float, default=0)
    endurance_score: Mapped[float] = mapped_column(Float, default=0)
    strength_score: Mapped[float] = mapped_column(Float, default=0)
    flexibility_score: Mapped[float] = mapped_column(Float, default=0)
    consistency_score: Mapped[float] = mapped_column(Float, default=0)
    nutrition_score: Mapped[float] = mapped_column(Float, default=0)
    rating_date: Mapped[date] = mapped_column(Date, default=date.today)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="ai_ratings")


class WorkoutRecord(Base):
    __tablename__ = "workout_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    sport_type: Mapped[str] = mapped_column(String(50))
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0)
    calories_burned: Mapped[float] = mapped_column(Float, default=0)
    notes: Mapped[str] = mapped_column(Text, default="")
    video_url: Mapped[str] = mapped_column(String(500), default="")
    analysis_result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    workout_date: Mapped[date] = mapped_column(Date, default=date.today)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="workout_records")


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    file_type: Mapped[str] = mapped_column(String(20))  # image, video, audio, file
    original_name: Mapped[str] = mapped_column(String(200))
    storage_path: Mapped[str] = mapped_column(String(500))
    thumbnail_path: Mapped[str] = mapped_column(String(500), default="")
    mime_type: Mapped[str] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
