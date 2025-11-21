"""
Agent 3: Validator Agent
Validates CI/CD pipelines for syntax, security, and correctness.
"""
import re
import logging
from typing import List, Dict, Any, Set, Tuple
import yaml
import requests

from .models import ValidationResult

logger = logging.getLogger(__name__)


class Validator:
    """Validates GitLab CI pipelines."""
    
    # Dangerous command patterns
    DANGEROUS_PATTERNS = [
        (r'rm\s+-rf\s+[/]', 'CRITICAL', 'Dangerous rm -rf / command'),
        (r'rm\s+-rf\s+\$', 'HIGH', 'rm -rf with variable expansion'),
        (r'curl\s+.*\s+\|\s+bash', 'HIGH', 'Piping curl to bash without verification'),
        (r'wget\s+.*\s+\|\s+bash', 'HIGH', 'Piping wget to bash without verification'),
        (r'docker\s+run.*--privileged', 'HIGH', 'Docker run with privileged mode'),
        (r'chmod\s+777', 'MEDIUM', 'Overly permissive chmod'),
        (r'password\s*=\s*["\']', 'HIGH', 'Hardcoded password in script'),
        (r'api[_-]?key\s*=\s*["\']', 'HIGH', 'Hardcoded API key'),
        (r'secret\s*=\s*["\']', 'HIGH', 'Hardcoded secret'),
        (r'pip\s+install\s+.*http://', 'MEDIUM', 'pip install from insecure HTTP source'),
        (r'npm\s+install\s+.*http://', 'MEDIUM', 'npm install from insecure HTTP source'),
        (r'eval\s+\$\(', 'MEDIUM', 'Use of eval with command substitution'),
        (r'eval\s+[^$]', 'HIGH', 'Use of eval command'),
        (r'exec\s+\$', 'HIGH', 'Dynamic exec with variable'),
    ]
    
    def __init__(self, gitlab_url: str = None, gitlab_token: str = None):
        """
        Initialize Validator.
        
        Args:
            gitlab_url: GitLab instance URL for lint API (optional)
            gitlab_token: GitLab token for API access (optional)
        """
        self.gitlab_url = gitlab_url
        self.gitlab_token = gitlab_token
        self.logger = logging.getLogger(__name__)
    
    def validate_pipeline(self, yaml_str: str) -> ValidationResult:
        """
        Validate a pipeline YAML string.
        
        Args:
            yaml_str: Pipeline YAML content
            
        Returns:
            ValidationResult with errors and warnings
        """
        result = ValidationResult(is_valid=True)
        
        # YAML syntax validation
        yaml_errors = self._validate_yaml_syntax(yaml_str)
        result.yaml_errors = yaml_errors
        if yaml_errors:
            result.is_valid = False
        
        if not yaml_errors:
            # Parse YAML for further validation
            try:
                pipeline_data = yaml.safe_load(yaml_str)
                
                # Validate GitLab CI structure
                structure_errors = self._validate_gitlab_structure(pipeline_data)
                result.errors.extend(structure_errors)
                
                # Check for dangerous commands
                security_issues = self._check_dangerous_commands(yaml_str, pipeline_data)
                result.security_issues = security_issues
                
                # Check for circular dependencies
                circular_deps = self._check_circular_dependencies(pipeline_data)
                result.circular_dependencies = circular_deps
                
                # Check for missing dependencies
                missing_deps = self._check_missing_dependencies(pipeline_data)
                result.missing_dependencies = missing_deps
                
                # Check job name conflicts
                name_conflicts = self._check_job_name_conflicts(pipeline_data)
                result.warnings.extend(name_conflicts)
                
                # Check for common issues
                common_issues = self._check_common_issues(pipeline_data)
                result.warnings.extend(common_issues)
                
                if security_issues or circular_deps or missing_deps or structure_errors:
                    result.is_valid = False
                
            except Exception as e:
                result.errors.append(f"Failed to parse pipeline: {str(e)}")
                result.is_valid = False
        
        # GitLab Lint API validation (optional)
        if self.gitlab_url and self.gitlab_token and not result.yaml_errors:
            lint_errors = self._validate_gitlab_lint(yaml_str)
            result.gitlab_lint_errors = lint_errors
            if lint_errors:
                result.is_valid = False
        
        self.logger.info(f"Validation complete: valid={result.is_valid}, "
                        f"errors={len(result.errors)}, warnings={len(result.warnings)}")
        
        return result
    
    def _validate_yaml_syntax(self, yaml_str: str) -> List[str]:
        """Validate YAML syntax."""
        errors = []
        try:
            yaml.safe_load(yaml_str)
        except yaml.YAMLError as e:
            errors.append(f"YAML syntax error: {str(e)}")
        except Exception as e:
            errors.append(f"YAML parsing error: {str(e)}")
        
        return errors
    
    def _validate_gitlab_structure(self, pipeline_data: Dict[str, Any]) -> List[str]:
        """Validate GitLab CI structure."""
        errors = []
        
        if not isinstance(pipeline_data, dict):
            errors.append("Pipeline must be a dictionary")
            return errors
        
        # Check for valid job structure
        for job_name, job_config in pipeline_data.items():
            if job_name in ['stages', 'variables', 'cache', 'include', 'workflow', 'default']:
                continue
            
            if not isinstance(job_config, dict):
                errors.append(f"Job '{job_name}' must be a dictionary")
                continue
            
            # Check required fields
            if 'script' not in job_config and 'extends' not in job_config:
                errors.append(f"Job '{job_name}' must have 'script' or 'extends'")
            
            # Validate stage
            if 'stage' in job_config:
                stage = job_config['stage']
                if not isinstance(stage, str):
                    errors.append(f"Job '{job_name}' stage must be a string")
            
            # Validate script
            if 'script' in job_config:
                script = job_config['script']
                if not isinstance(script, (list, str)):
                    errors.append(f"Job '{job_name}' script must be a list or string")
            
            # Validate needs
            if 'needs' in job_config:
                needs = job_config['needs']
                if not isinstance(needs, list):
                    errors.append(f"Job '{job_name}' needs must be a list")
        
        # Validate stages
        if 'stages' in pipeline_data:
            stages = pipeline_data['stages']
            if not isinstance(stages, list):
                errors.append("'stages' must be a list")
        
        return errors
    
    def _check_dangerous_commands(
        self, 
        yaml_str: str, 
        pipeline_data: Dict[str, Any]
    ) -> List[str]:
        """Check for dangerous commands in pipeline."""
        issues = []
        lines = yaml_str.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_lower = line.lower()
            
            for pattern, severity, description in self.DANGEROUS_PATTERNS:
                if re.search(pattern, line_lower, re.IGNORECASE):
                    issues.append(f"Line {i}: [{severity}] {description}: {line.strip()}")
        
        # Check for hardcoded secrets in variables
        if 'variables' in pipeline_data:
            variables = pipeline_data['variables']
            if isinstance(variables, dict):
                for key, value in variables.items():
                    if isinstance(value, str) and any(
                        secret_word in key.lower() 
                        for secret_word in ['password', 'secret', 'key', 'token', 'credential']
                    ):
                        if len(value) > 8 and not value.startswith('$'):
                            issues.append(
                                f"Potential hardcoded secret in variable '{key}': "
                                f"consider using CI/CD variables"
                            )
        
        return issues
    
    def _check_circular_dependencies(self, pipeline_data: Dict[str, Any]) -> List[str]:
        """Check for circular dependencies between jobs."""
        circular_deps = []
        jobs = {name: config for name, config in pipeline_data.items() 
                if isinstance(config, dict) and 'needs' in config}
        
        def has_circular_dep(job_name: str, visited: Set[str], path: Set[str]) -> bool:
            if job_name in path:
                return True
            if job_name in visited:
                return False
            
            visited.add(job_name)
            path.add(job_name)
            
            job_config = jobs.get(job_name, {})
            needs = job_config.get('needs', [])
            
            for dep in needs:
                if isinstance(dep, dict):
                    dep_name = dep.get('job', '')
                elif isinstance(dep, str):
                    dep_name = dep
                else:
                    continue
                
                if dep_name in jobs and has_circular_dep(dep_name, visited, path.copy()):
                    return True
            
            path.remove(job_name)
            return False
        
        for job_name in jobs:
            if has_circular_dep(job_name, set(), set()):
                circular_deps.append(f"Circular dependency detected involving job '{job_name}'")
        
        return circular_deps
    
    def _check_missing_dependencies(self, pipeline_data: Dict[str, Any]) -> List[str]:
        """Check for references to non-existent jobs."""
        missing_deps = []
        job_names = set(name for name in pipeline_data.keys() 
                       if name not in ['stages', 'variables', 'cache', 'include', 'workflow', 'default'])
        
        for job_name, job_config in pipeline_data.items():
            if not isinstance(job_config, dict):
                continue
            
            needs = job_config.get('needs', [])
            if not needs:
                continue
            
            for dep in needs:
                if isinstance(dep, dict):
                    dep_name = dep.get('job', '')
                elif isinstance(dep, str):
                    dep_name = dep
                else:
                    continue
                
                if dep_name and dep_name not in job_names:
                    missing_deps.append(
                        f"Job '{job_name}' depends on '{dep_name}' which does not exist"
                    )
        
        return missing_deps
    
    def _check_job_name_conflicts(self, pipeline_data: Dict[str, Any]) -> List[str]:
        """Check for job name conflicts."""
        warnings = []
        job_names = []
        
        for name in pipeline_data.keys():
            if name not in ['stages', 'variables', 'cache', 'include', 'workflow', 'default']:
                if name in job_names:
                    warnings.append(f"Duplicate job name: '{name}'")
                job_names.append(name)
        
        return warnings
    
    def _check_common_issues(self, pipeline_data: Dict[str, Any]) -> List[str]:
        """Check for common pipeline issues."""
        warnings = []
        
        # Check if stages are defined but jobs don't use them
        if 'stages' in pipeline_data:
            defined_stages = set(pipeline_data['stages'])
            used_stages = set()
            
            for job_name, job_config in pipeline_data.items():
                if isinstance(job_config, dict) and 'stage' in job_config:
                    used_stages.add(job_config['stage'])
            
            unused_stages = defined_stages - used_stages
            if unused_stages:
                warnings.append(f"Defined stages not used: {', '.join(unused_stages)}")
        
        # Check for jobs without stages
        jobs_without_stage = []
        for job_name, job_config in pipeline_data.items():
            if isinstance(job_config, dict) and job_name not in ['variables', 'cache', 'include', 'workflow', 'default']:
                if 'stage' not in job_config:
                    jobs_without_stage.append(job_name)
        
        if jobs_without_stage:
            warnings.append(f"Jobs without stage defined: {', '.join(jobs_without_stage)}")
        
        # Check for empty scripts
        for job_name, job_config in pipeline_data.items():
            if isinstance(job_config, dict) and 'script' in job_config:
                script = job_config['script']
                if isinstance(script, list) and len(script) == 0:
                    warnings.append(f"Job '{job_name}' has empty script")
                elif isinstance(script, str) and not script.strip():
                    warnings.append(f"Job '{job_name}' has empty script")
        
        return warnings
    
    def _validate_gitlab_lint(self, yaml_str: str) -> List[str]:
        """
        Validate pipeline using GitLab Lint API.
        
        Args:
            yaml_str: Pipeline YAML content
            
        Returns:
            List of lint errors
        """
        if not self.gitlab_url or not self.gitlab_token:
            return []
        
        errors = []
        
        try:
            # GitLab Lint API endpoint
            lint_url = f"{self.gitlab_url.rstrip('/')}/api/v4/ci/lint"
            
            payload = {
                'content': yaml_str
            }
            
            headers = {
                'PRIVATE-TOKEN': self.gitlab_token,
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                lint_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if not data.get('valid', False):
                    status = data.get('status', 'unknown')
                    errors.append(f"GitLab Lint: {status}")
                    
                    if 'errors' in data:
                        for error in data['errors']:
                            errors.append(f"GitLab Lint: {error}")
                
                if 'warnings' in data:
                    for warning in data['warnings']:
                        errors.append(f"GitLab Lint Warning: {warning}")
            
            else:
                self.logger.warning(
                    f"GitLab Lint API returned status {response.status_code}: "
                    f"{response.text}"
                )
        
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Failed to call GitLab Lint API: {e}")
        except Exception as e:
            self.logger.warning(f"Error validating with GitLab Lint: {e}")
        
        return errors

