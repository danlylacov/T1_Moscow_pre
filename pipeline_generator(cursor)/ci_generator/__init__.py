"""CI/CD Pipeline Generator - Self-Deploy."""
from .generate import generate_pipeline, generate_pipeline_from_json, PipelineGenerator

__version__ = "1.0.0"
__all__ = ["generate_pipeline", "generate_pipeline_from_json", "PipelineGenerator"]


