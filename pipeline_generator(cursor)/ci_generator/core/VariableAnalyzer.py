"""
Variable Analyzer - extracts required variables from generated pipeline.
"""
import re
import logging
from typing import List, Dict, Any, Set
import yaml

from .models import RequiredVariable

logger = logging.getLogger(__name__)


class VariableAnalyzer:
    """Analyzes pipeline YAML to extract required variables."""
    
    # GitLab CI автоматические переменные (не требуют настройки)
    GITLAB_AUTO_VARS = {
        'CI_REGISTRY', 'CI_REGISTRY_IMAGE', 'CI_REGISTRY_USER', 'CI_REGISTRY_PASSWORD',
        'CI_PROJECT_PATH', 'CI_PROJECT_NAME', 'CI_PROJECT_URL',
        'CI_COMMIT_REF_NAME', 'CI_COMMIT_REF_SLUG', 'CI_COMMIT_SHA', 'CI_COMMIT_SHORT_SHA',
        'CI_COMMIT_TAG', 'CI_PIPELINE_ID', 'CI_PIPELINE_SOURCE', 'CI_JOB_NAME', 'CI_JOB_STAGE',
        'CI_SERVER_HOST', 'CI_SERVER_URL', 'CI_API_V4_URL'
    }
    
    # Описания переменных
    VARIABLE_DESCRIPTIONS = {
        'SSH_PRIVATE_KEY': {
            'description': 'Приватный SSH ключ для подключения к серверу деплоя',
            'required': True,
            'example': '-----BEGIN OPENSSH PRIVATE KEY-----\n...',
            'job_patterns': ['deploy_ssh', 'deploy_docker_ssh']
        },
        'DEPLOY_HOST': {
            'description': 'Хост сервера для SSH деплоя (IP или домен)',
            'required': True,
            'example': 'deploy.example.com или 192.168.1.100',
            'job_patterns': ['deploy_ssh', 'deploy_docker_ssh']
        },
        'DEPLOY_USER': {
            'description': 'Пользователь для SSH подключения',
            'required': False,
            'default_value': 'deploy',
            'example': 'deploy, root, ubuntu, ec2-user',
            'job_patterns': ['deploy_ssh', 'deploy_docker_ssh']
        },
        'KUBECONFIG': {
            'description': 'Kubernetes конфигурация в формате Base64',
            'required': True,
            'example': 'Base64 encoded kubeconfig file',
            'job_patterns': ['deploy_k8s', 'deploy_docker_k8s']
        },
        'CI_KUBECONFIG': {
            'description': 'Kubernetes конфигурация (альтернативное имя)',
            'required': True,
            'example': 'Base64 encoded kubeconfig file',
            'job_patterns': ['deploy_k8s', 'deploy_docker_k8s']
        },
        'CI_ENVIRONMENT_NAME': {
            'description': 'Имя окружения для деплоя',
            'required': False,
            'default_value': 'production',
            'example': 'production, staging, development',
            'job_patterns': ['deploy']
        },
        'CI_ENVIRONMENT_URL': {
            'description': 'URL окружения после деплоя',
            'required': False,
            'default_value': 'http://${CI_PROJECT_NAME}.example.com',
            'example': 'https://app.example.com',
            'job_patterns': ['deploy']
        },
        'CI_PROJECT_NAME': {
            'description': 'Имя проекта (используется для deployment name)',
            'required': False,
            'default_value': '${CI_PROJECT_NAME} (автоматически)',
            'example': 'myapp',
            'job_patterns': ['deploy']
        },
        'DOCKERFILE': {
            'description': 'Путь к Dockerfile',
            'required': False,
            'default_value': 'Dockerfile',
            'example': 'Dockerfile.prod, docker/Dockerfile',
            'job_patterns': ['build_docker', 'build_and_push']
        },
        'BUILD_ARGS': {
            'description': 'Аргументы для docker build',
            'required': False,
            'default_value': 'Не используется',
            'example': '--build-arg VERSION=1.0.0 --build-arg NODE_ENV=production',
            'job_patterns': ['build_docker', 'build_and_push']
        },
        'DOCKER_IMAGE': {
            'description': 'Имя Docker образа',
            'required': False,
            'default_value': '${CI_REGISTRY_IMAGE}:${CI_COMMIT_REF_SLUG}',
            'example': '${CI_REGISTRY_IMAGE}:${CI_COMMIT_SHORT_SHA}',
            'job_patterns': ['build_docker', 'push_docker', 'build_and_push']
        },
        'DOCKER_REGISTRY': {
            'description': 'Docker registry URL',
            'required': False,
            'default_value': '${CI_REGISTRY}',
            'example': 'docker.io, ghcr.io, registry.example.com',
            'job_patterns': ['build_docker', 'push_docker', 'build_and_push']
        },
        'COMPOSE_FILE': {
            'description': 'Путь к docker-compose файлу',
            'required': False,
            'default_value': 'docker-compose.yml',
            'example': 'docker-compose.prod.yml',
            'job_patterns': ['deploy_compose', 'deploy_docker_compose']
        },
        'PYTHON_VERSION': {
            'description': 'Версия Python для jobs',
            'required': False,
            'default_value': '3.11',
            'example': '3.11, 3.12, 3.10',
            'job_patterns': ['python']
        },
        'NODE_VERSION': {
            'description': 'Версия Node.js для jobs',
            'required': False,
            'default_value': '18',
            'example': '18, 20, 22',
            'job_patterns': ['node', 'javascript', 'typescript']
        },
        'TRIVY_EXIT_CODE': {
            'description': 'Exit code для Trivy security scan',
            'required': False,
            'default_value': '0 (не блокировать)',
            'example': '0 или 1',
            'job_patterns': ['security_scan', 'docker_security_scan']
        },
        'TRIVY_SEVERITY': {
            'description': 'Уровни серьезности для Trivy',
            'required': False,
            'default_value': 'HIGH,CRITICAL',
            'example': 'CRITICAL, HIGH,CRITICAL',
            'job_patterns': ['security_scan', 'docker_security_scan']
        },
        'TRIVY_NO_PROGRESS': {
            'description': 'Отключить прогресс-бар в Trivy',
            'required': False,
            'default_value': 'true',
            'example': 'true, false',
            'job_patterns': ['security_scan', 'docker_security_scan']
        },
        'DOCKER_HOST': {
            'description': 'Docker daemon host (автоматически настраивается для GitLab CI)',
            'required': False,
            'default_value': 'tcp://docker:2376',
            'example': 'tcp://docker:2376',
            'job_patterns': ['build_docker', 'push_docker', 'build_and_push', 'deploy_compose']
        },
        'DOCKER_TLS_CERTDIR': {
            'description': 'Директория с TLS сертификатами для Docker (автоматически настраивается)',
            'required': False,
            'default_value': '/certs',
            'example': '/certs',
            'job_patterns': ['build_docker', 'push_docker', 'build_and_push', 'deploy_compose']
        },
        'DOCKER_TAG': {
            'description': 'Тег для Docker образа',
            'required': False,
            'default_value': '${CI_COMMIT_REF_SLUG}',
            'example': '${CI_COMMIT_REF_SLUG}, latest, ${CI_COMMIT_SHORT_SHA}',
            'job_patterns': ['build_docker', 'push_docker', 'build_and_push']
        },
        'KUBECTL_VERSION': {
            'description': 'Версия kubectl для Kubernetes деплоя',
            'required': False,
            'default_value': 'latest',
            'example': 'latest, 1.28, 1.27',
            'job_patterns': ['deploy_k8s', 'deploy_docker_k8s']
        }
    }
    
    def analyze_required_variables(self, yaml_content: str) -> List[RequiredVariable]:
        """
        Analyze pipeline YAML and extract required variables.
        
        Args:
            yaml_content: Generated pipeline YAML
            
        Returns:
            List of RequiredVariable objects
        """
        try:
            pipeline_data = yaml.safe_load(yaml_content)
            if not isinstance(pipeline_data, dict):
                return []
            
            # Extract all variable references from YAML
            all_vars = self._extract_variables(yaml_content, pipeline_data)
            
            # Filter out GitLab auto variables
            required_vars = []
            seen_vars = set()
            
            for var_name in all_vars:
                if var_name in self.GITLAB_AUTO_VARS:
                    continue
                
                if var_name in seen_vars:
                    continue
                
                seen_vars.add(var_name)
                
                # Get variable info
                var_info = self.VARIABLE_DESCRIPTIONS.get(var_name, {})
                
                # Find jobs that use this variable
                jobs_using = self._find_jobs_using_variable(pipeline_data, var_name)
                
                required_var = RequiredVariable(
                    name=var_name,
                    description=var_info.get('description', f'Переменная {var_name}'),
                    required=var_info.get('required', False),
                    default_value=var_info.get('default_value'),
                    example=var_info.get('example'),
                    job_usage=jobs_using
                )
                
                required_vars.append(required_var)
            
            # Sort by required first, then by name
            required_vars.sort(key=lambda v: (not v.required, v.name))
            
            logger.info(f"Found {len(required_vars)} required variables")
            return required_vars
        
        except Exception as e:
            logger.error(f"Error analyzing variables: {e}")
            return []
    
    def _extract_variables(self, yaml_content: str, pipeline_data: Dict[str, Any]) -> Set[str]:
        """Extract all variable references from YAML."""
        variables = set()
        
        # Pattern for ${VAR} and ${VAR:-default}
        var_pattern = r'\$\{([A-Z_][A-Z0-9_]*)(?::-[^}]*)?\}'
        
        # Find all variable references
        matches = re.findall(var_pattern, yaml_content)
        variables.update(matches)
        
        # Also check variables section
        if 'variables' in pipeline_data:
            vars_section = pipeline_data['variables']
            if isinstance(vars_section, dict):
                variables.update(vars_section.keys())
        
        # Check job variables
        for job_name, job_config in pipeline_data.items():
            if isinstance(job_config, dict) and 'variables' in job_config:
                job_vars = job_config['variables']
                if isinstance(job_vars, dict):
                    variables.update(job_vars.keys())
        
        return variables
    
    def _find_jobs_using_variable(self, pipeline_data: Dict[str, Any], var_name: str) -> List[str]:
        """Find jobs that use a specific variable."""
        jobs = []
        
        for job_name, job_config in pipeline_data.items():
            if job_name in ['stages', 'variables', 'workflow', 'cache', 'include', 'default']:
                continue
            
            if not isinstance(job_config, dict):
                continue
            
            # Check if variable is used in this job
            job_yaml = yaml.dump({job_name: job_config}, default_flow_style=False)
            
            # Check various patterns
            var_name_escaped = re.escape(var_name)
            # Build pattern for ${VAR} or ${VAR:-default} - need to escape braces properly
            pattern1 = r'\$\{' + var_name_escaped + r'(?::-[^}]*)?\}'
            patterns = [
                pattern1,                                        # ${VAR} or ${VAR:-default}
                r'\$' + var_name_escaped + r'\b',               # $VAR
                '"' + var_name + '"',                           # "VAR"
                "'" + var_name + "'",                           # 'VAR'
            ]
            
            for pattern in patterns:
                if re.search(pattern, job_yaml, re.IGNORECASE):
                    jobs.append(job_name)
                    break
        
        return jobs

