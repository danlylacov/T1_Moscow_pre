import json
from typing import List

from sqlalchemy.orm import Session

from app import models
from app.schemas import (
    User,
    UserCreate,
    Project,
    ProjectCreate,
    PipelineGeneration,
    PipelineGenerationCreate,
    ProjectAnalysis,
)


# ---------- Users ----------


def create_user(db: Session, data: UserCreate) -> User:
    user_orm = models.UserORM(username=data.username)
    db.add(user_orm)
    db.commit()
    db.refresh(user_orm)
    return User.model_validate(user_orm)


def list_users(db: Session) -> List[User]:
    users = db.query(models.UserORM).all()
    return [User.model_validate(u) for u in users]


# ---------- Projects ----------


def _analysis_to_json(analysis: ProjectAnalysis | None) -> str | None:
    if analysis is None:
        return None
    return analysis.model_dump_json()


def _analysis_from_json(data: str | None) -> ProjectAnalysis | None:
    if not data:
        return None
    # Используем pydantic для восстановления объекта
    return ProjectAnalysis.model_validate(json.loads(data))


def create_project(db: Session, data: ProjectCreate) -> Project:
    project_orm = models.ProjectORM(
        name=data.name,
        url=str(data.url),
        clone_token=data.clone_token,
        user_id=data.user_id,
        analysis_json=_analysis_to_json(data.analysis),
    )
    db.add(project_orm)
    db.commit()
    db.refresh(project_orm)

    return Project(
        id=project_orm.id,
        name=project_orm.name,
        url=project_orm.url,
        clone_token=project_orm.clone_token,
        user_id=project_orm.user_id,
        analysis=_analysis_from_json(project_orm.analysis_json),
    )


def list_projects(db: Session) -> List[Project]:
    projects = db.query(models.ProjectORM).all()
    result: List[Project] = []
    for p in projects:
        result.append(
            Project(
                id=p.id,
                name=p.name,
                url=p.url,
                clone_token=p.clone_token,
                user_id=p.user_id,
                analysis=_analysis_from_json(p.analysis_json),
            )
        )
    return result


def get_project(db: Session, project_id: int) -> Project | None:
    p = db.query(models.ProjectORM).filter(models.ProjectORM.id == project_id).first()
    if p is None:
        return None
    return Project(
        id=p.id,
        name=p.name,
        url=p.url,
        clone_token=p.clone_token,
        user_id=p.user_id,
        analysis=_analysis_from_json(p.analysis_json),
    )


# ---------- Pipeline generations ----------


def create_pipeline_generation(
    db: Session, data: PipelineGenerationCreate
) -> PipelineGeneration:
    pipeline_orm = models.PipelineGenerationORM(
        user_id=data.user_id,
        project_id=data.project_id,
        uml=data.uml,
    )
    db.add(pipeline_orm)
    db.commit()
    db.refresh(pipeline_orm)

    return PipelineGeneration(
        id=pipeline_orm.id,
        user_id=pipeline_orm.user_id,
        project_id=pipeline_orm.project_id,
        uml=pipeline_orm.uml,
        generated_at=pipeline_orm.generated_at,
    )


def list_pipeline_generations(db: Session) -> List[PipelineGeneration]:
    pipelines = db.query(models.PipelineGenerationORM).all()
    return [
        PipelineGeneration(
            id=p.id,
            user_id=p.user_id,
            project_id=p.project_id,
            uml=p.uml,
            generated_at=p.generated_at,
        )
        for p in pipelines
    ]


