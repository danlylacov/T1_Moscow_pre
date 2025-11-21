"""
Data models for CI/CD pipeline generator.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from enum import Enum


class Platform(str, Enum):
    """Supported CI/CD platforms."""
    GITLAB = "gitlab"
    JENKINS = "jenkins"
    GITHUB = "github"


class JobStatus(str, Enum):
    """Job execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Template:
    """Represents a CI/CD job template."""
    name: str
    content: str
    language: Optional[str] = None
    framework: Optional[str] = None
    stage: Optional[str] = None
    variables: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    image: Optional[str] = None
    services: List[str] = field(default_factory=list)
    cache: Optional[Dict[str, Any]] = None
    artifacts: Optional[Dict[str, Any]] = None
    only: Optional[List[str]] = None
    except_branches: Optional[List[str]] = None
    when: Optional[str] = None
    allow_failure: bool = False
    timeout: Optional[str] = None
    retry: Optional[Dict[str, int]] = None
    script: List[str] = field(default_factory=list)
    before_script: List[str] = field(default_factory=list)
    after_script: List[str] = field(default_factory=list)


@dataclass
class Job:
    """Represents a CI/CD job in the pipeline."""
    name: str
    stage: str
    script: List[str]
    image: Optional[str] = None
    services: List[str] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    needs: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    cache: Optional[Dict[str, Any]] = None
    artifacts: Optional[Dict[str, Any]] = None
    only: Optional[List[str]] = None
    except_branches: Optional[List[str]] = None
    when: Optional[str] = None
    allow_failure: bool = False
    timeout: Optional[str] = None
    retry: Optional[Dict[str, int]] = None
    before_script: List[str] = field(default_factory=list)
    after_script: List[str] = field(default_factory=list)
    rules: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Result of pipeline validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    security_issues: List[str] = field(default_factory=list)
    yaml_errors: List[str] = field(default_factory=list)
    gitlab_lint_errors: List[str] = field(default_factory=list)
    circular_dependencies: List[str] = field(default_factory=list)
    missing_dependencies: List[str] = field(default_factory=list)


@dataclass
class PipelineConfig:
    """Complete pipeline configuration."""
    stages: List[str]
    jobs: List[Job]
    variables: Dict[str, Any] = field(default_factory=dict)
    cache: Optional[Dict[str, Any]] = None
    include: List[str] = field(default_factory=list)
    workflow: Optional[Dict[str, Any]] = None
    default: Optional[Dict[str, Any]] = None


@dataclass
class Analysis:
    """Repository analysis data."""
    languages: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    frontend_frameworks: List[str] = field(default_factory=list)
    backend_frameworks: List[str] = field(default_factory=list)
    package_manager: Optional[str] = None
    test_runner: Optional[str] = None
    docker: bool = False
    kubernetes: bool = False
    terraform: bool = False
    databases: List[str] = field(default_factory=list)
    entry_points: List[Dict[str, Any]] = field(default_factory=list)
    main_entry: Optional[Dict[str, Any]] = None


@dataclass
class UserSettings:
    """User configuration for pipeline generation."""
    platform: str = "gitlab"
    triggers: Dict[str, Any] = field(default_factory=dict)
    stages: List[str] = field(default_factory=list)
    docker_registry: Optional[str] = None
    docker_image: Optional[str] = None
    secrets: Dict[str, str] = field(default_factory=dict)
    cache_config: Optional[Dict[str, Any]] = None
    parallel_jobs: bool = False
    coverage_reports: bool = False
    custom_stages: List[Dict[str, Any]] = field(default_factory=list)
    executor: str = "docker"
    images: Dict[str, str] = field(default_factory=dict)


@dataclass
class RequiredVariable:
    """Information about a required CI/CD variable."""
    name: str
    description: str
    required: bool = True
    default_value: Optional[str] = None
    example: Optional[str] = None
    job_usage: List[str] = field(default_factory=list)  # Jobs that use this variable


@dataclass
class PipelineResult:
    """Final pipeline generation result."""
    yaml_content: str
    explanation: str
    validation_result: ValidationResult
    jobs_count: int
    stages: List[str]
    warnings: List[str] = field(default_factory=list)
    required_variables: List[RequiredVariable] = field(default_factory=list)

