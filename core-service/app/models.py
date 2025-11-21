from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    # Здесь мог бы быть password_hash, но для простоты не храним

    projects: Mapped[list["ProjectORM"]] = relationship(back_populates="user")
    pipelines: Mapped[list["PipelineGenerationORM"]] = relationship(back_populates="user")


class ProjectORM(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    clone_token: Mapped[str] = mapped_column(String(4096), nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    # Для простоты храним JSON анализа как текст (можно заменить на JSONB)
    analysis_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["UserORM"] = relationship(back_populates="projects")
    pipelines: Mapped[list["PipelineGenerationORM"]] = relationship(back_populates="project")


class PipelineGenerationORM(Base):
    __tablename__ = "pipeline_generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    project_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("projects.id"), nullable=True, index=True
    )

    uml: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=datetime.utcnow, nullable=False
    )

    user: Mapped["UserORM"] = relationship(back_populates="pipelines")
    project: Mapped[Optional["ProjectORM"]] = relationship(back_populates="pipelines")



