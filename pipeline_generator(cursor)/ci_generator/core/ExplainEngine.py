"""
Agent 4: ExplainEngine Agent
Generates human-readable explanations of CI/CD pipelines.
"""
import logging
from typing import Dict, Any, List
import yaml

logger = logging.getLogger(__name__)


class ExplainEngine:
    """Generates human-readable explanations of CI/CD pipelines."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def explain_pipeline(self, yaml_str: str) -> str:
        """
        Generate human-readable explanation of the pipeline.
        
        Args:
            yaml_str: Pipeline YAML content
            
        Returns:
            Human-readable explanation
        """
        try:
            pipeline_data = yaml.safe_load(yaml_str)
            if not isinstance(pipeline_data, dict):
                return "Invalid pipeline: not a dictionary"
            
            explanation_parts = []
            
            # Header
            explanation_parts.append("# Pipeline Explanation\n")
            
            # Overview
            overview = self._explain_overview(pipeline_data)
            if overview:
                explanation_parts.append(overview)
            
            # Stages
            stages_explanation = self._explain_stages(pipeline_data)
            if stages_explanation:
                explanation_parts.append(stages_explanation)
            
            # Jobs by stage
            jobs_explanation = self._explain_jobs(pipeline_data)
            if jobs_explanation:
                explanation_parts.append(jobs_explanation)
            
            # Dependencies
            deps_explanation = self._explain_dependencies(pipeline_data)
            if deps_explanation:
                explanation_parts.append(deps_explanation)
            
            # Triggers
            triggers_explanation = self._explain_triggers(pipeline_data)
            if triggers_explanation:
                explanation_parts.append(triggers_explanation)
            
            # Variables and configuration
            config_explanation = self._explain_configuration(pipeline_data)
            if config_explanation:
                explanation_parts.append(config_explanation)
            
            # Security and optimizations
            optimizations = self._explain_optimizations(pipeline_data)
            if optimizations:
                explanation_parts.append(optimizations)
            
            return "\n".join(explanation_parts)
        
        except Exception as e:
            self.logger.error(f"Error explaining pipeline: {e}")
            return f"Error generating explanation: {str(e)}"
    
    def _explain_overview(self, pipeline_data: Dict[str, Any]) -> str:
        """Explain pipeline overview."""
        parts = ["## Overview\n"]
        
        # Count jobs
        jobs = [name for name in pipeline_data.keys() 
                if name not in ['stages', 'variables', 'cache', 'include', 'workflow', 'default']]
        job_count = len(jobs)
        
        parts.append(f"This pipeline contains **{job_count} jobs** organized into stages.\n")
        
        # Stages
        if 'stages' in pipeline_data:
            stages = pipeline_data['stages']
            parts.append(f"Pipeline stages: {', '.join(stages)}\n")
        
        return "\n".join(parts)
    
    def _explain_stages(self, pipeline_data: Dict[str, Any]) -> str:
        """Explain pipeline stages."""
        if 'stages' not in pipeline_data:
            return ""
        
        parts = ["## Pipeline Stages\n"]
        stages = pipeline_data['stages']
        
        # Group jobs by stage
        stage_jobs: Dict[str, List[str]] = {}
        for job_name, job_config in pipeline_data.items():
            if isinstance(job_config, dict) and job_name not in ['variables', 'cache', 'include', 'workflow', 'default']:
                stage = job_config.get('stage', 'unknown')
                if stage not in stage_jobs:
                    stage_jobs[stage] = []
                stage_jobs[stage].append(job_name)
        
        for stage in stages:
            jobs = stage_jobs.get(stage, [])
            parts.append(f"### {stage.capitalize()} Stage")
            parts.append(f"- **Purpose**: {self._explain_stage_purpose(stage)}")
            parts.append(f"- **Jobs**: {len(jobs)}")
            if jobs:
                parts.append(f"- **Job names**: {', '.join(jobs)}")
            parts.append("")
        
        return "\n".join(parts)
    
    def _explain_stage_purpose(self, stage: str) -> str:
        """Explain the purpose of a stage."""
        purposes = {
            'install': 'Install and restore project dependencies',
            'lint': 'Run static code analysis and linting',
            'test': 'Execute test suites and generate coverage reports',
            'build': 'Compile and build the application',
            'security': 'Run security scans and vulnerability checks',
            'deploy': 'Deploy the application to target environments',
            'publish': 'Publish artifacts and Docker images',
            'cleanup': 'Clean up temporary files and resources'
        }
        return purposes.get(stage.lower(), f'Execute {stage} tasks')
    
    def _explain_jobs(self, pipeline_data: Dict[str, Any]) -> str:
        """Explain individual jobs."""
        parts = ["## Jobs Details\n"]
        
        jobs = [(name, config) for name, config in pipeline_data.items() 
                if isinstance(config, dict) and name not in ['variables', 'cache', 'include', 'workflow', 'default']]
        
        # Sort by stage
        jobs_by_stage: Dict[str, List[tuple]] = {}
        for job_name, job_config in jobs:
            stage = job_config.get('stage', 'unknown')
            if stage not in jobs_by_stage:
                jobs_by_stage[stage] = []
            jobs_by_stage[stage].append((job_name, job_config))
        
        for stage in sorted(jobs_by_stage.keys()):
            parts.append(f"### {stage.capitalize()} Stage Jobs\n")
            
            for job_name, job_config in jobs_by_stage[stage]:
                parts.append(f"#### {job_name}")
                
                # Explain what the job does
                script = job_config.get('script', [])
                if isinstance(script, str):
                    script = [script]
                
                job_explanation = self._explain_job_script(job_name, script)
                if job_explanation:
                    parts.append(job_explanation)
                
                # Image
                if 'image' in job_config:
                    parts.append(f"- **Docker image**: `{job_config['image']}`")
                
                # Services
                if 'services' in job_config:
                    services = job_config['services']
                    if isinstance(services, list):
                        parts.append(f"- **Services**: {', '.join(services)}")
                
                # Artifacts
                if 'artifacts' in job_config:
                    artifacts = job_config['artifacts']
                    if isinstance(artifacts, dict):
                        paths = artifacts.get('paths', [])
                        if paths:
                            parts.append(f"- **Artifacts**: {', '.join(paths)}")
                
                # Cache
                if 'cache' in job_config:
                    cache = job_config['cache']
                    if isinstance(cache, dict):
                        key = cache.get('key', '')
                        paths = cache.get('paths', [])
                        if key or paths:
                            parts.append(f"- **Cache**: key=`{key}`, paths={', '.join(paths) if paths else 'N/A'}")
                
                # Dependencies
                if 'needs' in job_config:
                    needs = job_config['needs']
                    if needs:
                        parts.append(f"- **Depends on**: {', '.join(str(n) for n in needs)}")
                
                # Allow failure
                if job_config.get('allow_failure', False):
                    parts.append("- **Allow failure**: Yes (job can fail without blocking pipeline)")
                
                # Timeout
                if 'timeout' in job_config:
                    parts.append(f"- **Timeout**: {job_config['timeout']}")
                
                parts.append("")
        
        return "\n".join(parts)
    
    def _explain_job_script(self, job_name: str, script: List[str]) -> str:
        """Explain what a job script does."""
        if not script:
            return ""
        
        script_text = ' '.join(script).lower()
        explanations = []
        
        # Detect common patterns
        if 'pip install' in script_text or 'npm install' in script_text or 'yarn install' in script_text:
            explanations.append("This job installs project dependencies")
        
        if 'pytest' in script_text or 'jest' in script_text or 'test' in script_text:
            explanations.append("This job runs the test suite")
        
        if 'flake8' in script_text or 'pylint' in script_text or 'eslint' in script_text:
            explanations.append("This job performs static code analysis and linting")
        
        if 'docker build' in script_text:
            explanations.append("This job builds a Docker image")
        
        if 'docker push' in script_text:
            explanations.append("This job publishes the Docker image to a registry")
        
        if 'kubectl' in script_text or 'helm' in script_text:
            explanations.append("This job deploys to Kubernetes")
        
        if 'terraform' in script_text:
            explanations.append("This job manages infrastructure with Terraform")
        
        if 'bandit' in script_text or 'snyk' in script_text or 'trivy' in script_text:
            explanations.append("This job performs security scanning")
        
        if not explanations:
            # Generic explanation based on job name
            name_lower = job_name.lower()
            if 'lint' in name_lower:
                explanations.append("This job runs linting and code quality checks")
            elif 'test' in name_lower:
                explanations.append("This job executes tests")
            elif 'build' in name_lower:
                explanations.append("This job builds the application")
            elif 'deploy' in name_lower:
                explanations.append("This job deploys the application")
            elif 'security' in name_lower or 'scan' in name_lower:
                explanations.append("This job performs security scanning")
            else:
                explanations.append(f"This job executes: {'; '.join(script[:3])}")
        
        return "- **Purpose**: " + "; ".join(explanations)
    
    def _explain_dependencies(self, pipeline_data: Dict[str, Any]) -> str:
        """Explain job dependencies."""
        parts = ["## Job Dependencies\n"]
        
        jobs_with_deps = []
        for job_name, job_config in pipeline_data.items():
            if isinstance(job_config, dict) and 'needs' in job_config:
                needs = job_config['needs']
                if needs:
                    jobs_with_deps.append((job_name, needs))
        
        if not jobs_with_deps:
            parts.append("No explicit job dependencies defined. Jobs will run in stage order.\n")
            return "\n".join(parts)
        
        parts.append("The following jobs have explicit dependencies:\n")
        
        for job_name, needs in jobs_with_deps:
            needs_str = ', '.join(str(n) for n in needs)
            parts.append(f"- **{job_name}** depends on: {needs_str}")
        
        parts.append("\nJobs with dependencies can run in parallel with their dependencies, "
                    "potentially speeding up pipeline execution.\n")
        
        return "\n".join(parts)
    
    def _explain_triggers(self, pipeline_data: Dict[str, Any]) -> str:
        """Explain pipeline triggers."""
        parts = ["## Pipeline Triggers\n"]
        
        workflow = pipeline_data.get('workflow', {})
        rules = workflow.get('rules', [])
        
        if not rules:
            # Check individual job rules
            job_rules = []
            for job_name, job_config in pipeline_data.items():
                if isinstance(job_config, dict) and 'rules' in job_config:
                    job_rules.extend(job_config['rules'])
                elif isinstance(job_config, dict) and 'only' in job_config:
                    only = job_config['only']
                    if isinstance(only, list):
                        job_rules.append(f"Runs on branches: {', '.join(only)}")
            
            if job_rules:
                parts.append("Pipeline triggers based on job-level rules:")
                for rule in set(job_rules):
                    parts.append(f"- {rule}")
            else:
                parts.append("Pipeline runs on all branches and merge requests by default.")
        else:
            parts.append("Pipeline triggers:")
            for rule in rules:
                if 'if' in rule:
                    condition = rule['if']
                    parts.append(f"- Runs when: `{condition}`")
        
        parts.append("")
        return "\n".join(parts)
    
    def _explain_configuration(self, pipeline_data: Dict[str, Any]) -> str:
        """Explain pipeline configuration."""
        parts = ["## Configuration\n"]
        
        # Variables
        if 'variables' in pipeline_data:
            variables = pipeline_data['variables']
            if isinstance(variables, dict) and variables:
                parts.append("### Environment Variables")
                for key, value in list(variables.items())[:10]:  # Limit to first 10
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:50] + "..."
                    parts.append(f"- `{key}`: `{value}`")
                if len(variables) > 10:
                    parts.append(f"- ... and {len(variables) - 10} more variables")
                parts.append("")
        
        # Cache
        if 'cache' in pipeline_data:
            cache = pipeline_data['cache']
            if isinstance(cache, dict):
                parts.append("### Cache Configuration")
                key = cache.get('key', 'default')
                paths = cache.get('paths', [])
                parts.append(f"- Cache key: `{key}`")
                if paths:
                    parts.append(f"- Cached paths: {', '.join(paths)}")
                parts.append("")
        
        # Default
        if 'default' in pipeline_data:
            default = pipeline_data['default']
            if isinstance(default, dict):
                parts.append("### Default Job Configuration")
                if 'image' in default:
                    parts.append(f"- Default image: `{default['image']}`")
                if 'before_script' in default:
                    parts.append(f"- Default before_script: {len(default['before_script'])} commands")
                parts.append("")
        
        if len(parts) == 1:  # Only header
            return ""
        
        return "\n".join(parts)
    
    def _explain_optimizations(self, pipeline_data: Dict[str, Any]) -> str:
        """Explain optimizations and security considerations."""
        parts = ["## Optimizations & Security\n"]
        
        optimizations = []
        security_notes = []
        
        # Check for cache usage
        has_cache = False
        for job_name, job_config in pipeline_data.items():
            if isinstance(job_config, dict) and 'cache' in job_config:
                has_cache = True
                break
        
        if has_cache:
            optimizations.append("✅ **Cache enabled**: Dependencies are cached to speed up builds")
        else:
            optimizations.append("⚠️ **No cache**: Consider enabling cache for dependencies to speed up builds")
        
        # Check for parallel execution (needs)
        has_parallel = False
        for job_name, job_config in pipeline_data.items():
            if isinstance(job_config, dict) and 'needs' in job_config:
                needs = job_config.get('needs', [])
                if needs:
                    has_parallel = True
                    break
        
        if has_parallel:
            optimizations.append("✅ **Parallel execution**: Jobs use 'needs' for parallel execution")
        else:
            optimizations.append("💡 **Consider parallelization**: Use 'needs' to run independent jobs in parallel")
        
        # Check for artifacts
        has_artifacts = False
        for job_name, job_config in pipeline_data.items():
            if isinstance(job_config, dict) and 'artifacts' in job_config:
                has_artifacts = True
                break
        
        if has_artifacts:
            optimizations.append("✅ **Artifacts**: Build artifacts are preserved between jobs")
        
        # Security notes
        security_notes.append("🔒 **Security**: Review scripts for hardcoded secrets and use CI/CD variables")
        security_notes.append("🔒 **Security**: Ensure Docker images are from trusted sources")
        
        if optimizations:
            parts.extend(optimizations)
            parts.append("")
        
        if security_notes:
            parts.extend(security_notes)
            parts.append("")
        
        if len(parts) == 1:  # Only header
            return ""
        
        return "\n".join(parts)

