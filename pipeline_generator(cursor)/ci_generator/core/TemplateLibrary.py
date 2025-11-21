"""
Agent 1: TemplateLibrary Agent
Loads and manages CI/CD job templates from filesystem.
"""
import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml

from .models import Template, Analysis

logger = logging.getLogger(__name__)


class TemplateLibrary:
    """Manages CI/CD job templates with placeholder substitution."""
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize TemplateLibrary.
        
        Args:
            templates_dir: Path to templates directory. Defaults to ./templates
        """
        if templates_dir is None:
            # Get the directory where this file is located
            base_dir = Path(__file__).parent.parent
            self.templates_dir = base_dir / "templates"
        else:
            self.templates_dir = Path(templates_dir)
        
        self._template_cache: Dict[str, Template] = {}
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load all templates from the filesystem."""
        if not self.templates_dir.exists():
            logger.warning(f"Templates directory not found: {self.templates_dir}")
            return
        
        logger.info(f"Loading templates from {self.templates_dir}")
        
        # Walk through all YAML files in templates directory
        for yaml_file in self.templates_dir.rglob("*.yml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse YAML to extract job information
                try:
                    yaml_data = yaml.safe_load(content)
                except yaml.YAMLError as e:
                    logger.error(f"Failed to parse YAML in {yaml_file}: {e}")
                    continue
                
                if not yaml_data or not isinstance(yaml_data, dict):
                    continue
                
                # Extract language and framework from path
                parts = yaml_file.relative_to(self.templates_dir).parts
                language = parts[0] if len(parts) > 0 else None
                framework = parts[1] if len(parts) > 1 else None
                
                # Process each job in the template file
                for job_name, job_config in yaml_data.items():
                    if job_name in ['stages', 'variables', 'cache', 'include', 'workflow', 'default']:
                        continue
                    
                    if isinstance(job_config, dict):
                        template = self._parse_job_to_template(
                            job_name, job_config, content, language, framework
                        )
                        # Create cache key: language/framework/job_name or language/job_name
                        if framework:
                            cache_key = f"{language}/{framework}/{job_name}"
                        elif language:
                            cache_key = f"{language}/{job_name}"
                        else:
                            cache_key = job_name
                        self._template_cache[cache_key] = template
                        # Also store by filename for easier lookup
                        file_key = f"{yaml_file.relative_to(self.templates_dir)}/{job_name}"
                        self._template_cache[file_key] = template
                        # Store by language only for language-only templates
                        if language and not framework:
                            lang_only_key = f"{language}/{job_name}"
                            if lang_only_key not in self._template_cache:
                                self._template_cache[lang_only_key] = template
                        logger.debug(f"Loaded template: {cache_key}")
            
            except Exception as e:
                logger.error(f"Error loading template from {yaml_file}: {e}")
        
        logger.info(f"Loaded {len(self._template_cache)} templates")
    
    def _parse_job_to_template(
        self, 
        job_name: str, 
        job_config: Dict[str, Any], 
        raw_content: str,
        language: Optional[str],
        framework: Optional[str]
    ) -> Template:
        """Parse a job configuration into a Template object."""
        # Extract script
        script = job_config.get('script', [])
        if isinstance(script, str):
            script = [script]
        elif not isinstance(script, list):
            script = []
        
        # Extract other fields
        stage = job_config.get('stage')
        image = job_config.get('image')
        services = job_config.get('services', [])
        if isinstance(services, str):
            services = [services]
        
        variables = job_config.get('variables', {})
        if not isinstance(variables, dict):
            variables = {}
        
        dependencies = job_config.get('dependencies', [])
        if isinstance(dependencies, str):
            dependencies = [dependencies]
        
        tags = job_config.get('tags', [])
        if isinstance(tags, str):
            tags = [tags]
        
        before_script = job_config.get('before_script', [])
        if isinstance(before_script, str):
            before_script = [before_script]
        
        after_script = job_config.get('after_script', [])
        if isinstance(after_script, str):
            after_script = [after_script]
        
        return Template(
            name=job_name,
            content=raw_content,
            language=language,
            framework=framework,
            stage=stage,
            variables=variables,
            dependencies=dependencies,
            tags=tags,
            image=image,
            services=services,
            cache=job_config.get('cache'),
            artifacts=job_config.get('artifacts'),
            only=job_config.get('only'),
            except_branches=job_config.get('except'),
            when=job_config.get('when'),
            allow_failure=job_config.get('allow_failure', False),
            timeout=job_config.get('timeout'),
            retry=job_config.get('retry'),
            script=script,
            before_script=before_script,
            after_script=after_script
        )
    
    def get_templates_for(self, analysis: Dict[str, Any]) -> List[Template]:
        """
        Get relevant templates based on analysis.
        New structure:
        - Lint: by language (python/lint.yml, node/lint.yml)
        - Test: by test_runner (python/test_pytest.yml, node/test_jest.yml)
        - Install/Build: by framework or language
        - Any stage can be added regardless of framework
        
        Args:
            analysis: Repository analysis data
            
        Returns:
            List of matching templates
        """
        templates = []
        seen_templates = set()  # Track by (language, framework, job_name) to avoid duplicates
        languages = analysis.get('languages', [])
        frameworks = analysis.get('frameworks', []) + analysis.get('backend_frameworks', [])
        frontend_frameworks = analysis.get('frontend_frameworks', [])
        package_manager = analysis.get('package_manager')
        test_runner = analysis.get('test_runner')
        docker = analysis.get('docker', False)
        kubernetes = analysis.get('kubernetes', False)
        terraform = analysis.get('terraform', False)
        
        # Normalize language names
        lang_map = {
            'javascript': 'node',
            'typescript': 'node',
            'python': 'python',
            'java': 'java',
            'go': 'go',
            'rust': 'rust',
            'php': 'php',
            'ruby': 'ruby',
            'csharp': 'dotnet',
            'cpp': 'cpp',
            'c': 'c'
        }
        
        # Map test runners to template names
        test_runner_map = {
            'pytest': 'test_pytest',
            'jest': 'test_jest',
            'mocha': 'test_mocha',
            'unittest': 'test_unittest',
            'jasmine': 'test_jest',  # fallback to jest
            'go test': 'test',
            'go': 'test'
        }
        
        for lang in languages:
            normalized_lang = lang_map.get(lang.lower(), lang.lower())
            
            # 1. LINT: Always by language (python/lint.yml, node/lint.yml)
            for key, template in self._template_cache.items():
                parts = key.split('/')
                # Match: language/lint.yml or language/lint or file-based keys like "python/lint.yml/lint"
                is_lint_match = (
                    (len(parts) == 2 and parts[0] == normalized_lang and 'lint' in parts[1].lower()) or
                    (len(parts) == 3 and parts[0] == normalized_lang and 'lint' in parts[1].lower() and template.name == 'lint') or
                    (template.language == normalized_lang and template.name == 'lint' and not template.framework)
                )
                if is_lint_match:
                    template_id = (template.language, template.framework, template.name)
                    if template_id not in seen_templates:
                        templates.append(template)
                        seen_templates.add(template_id)
                        logger.debug(f"Matched lint template by language: {key}")
            
            # 2. TEST: By test_runner (python/test_pytest.yml, node/test_jest.yml)
            if test_runner:
                test_runner_lower = test_runner.lower()
                test_template_name = test_runner_map.get(test_runner_lower, 'test')
                
                # Look for test_runner specific templates
                for key, template in self._template_cache.items():
                    parts = key.split('/')
                    # Match: language/test_runner.yml or language/test_runner
                    # Or file-based keys like "python/test_pytest.yml/test"
                    is_test_match = (
                        (len(parts) == 2 and parts[0] == normalized_lang and 
                         (test_template_name in parts[1].lower() or test_runner_lower in parts[1].lower())) or
                        (len(parts) == 3 and parts[0] == normalized_lang and 
                         (test_template_name in parts[1].lower() or test_runner_lower in parts[1].lower()) and
                         template.name == 'test') or
                        (template.language == normalized_lang and template.name == 'test' and
                         (test_template_name in str(template.framework or '').lower() or
                          test_runner_lower in str(template.framework or '').lower()))
                    )
                    if is_test_match:
                        template_id = (template.language, template.framework, template.name)
                        if template_id not in seen_templates:
                            templates.append(template)
                            seen_templates.add(template_id)
                            logger.debug(f"Matched test template by test_runner: {key}")
                
                # Fallback: generic test template for language
                if not any(t.name == 'test' for t in templates):
                    for key, template in self._template_cache.items():
                        parts = key.split('/')
                        is_generic_test = (
                            (len(parts) == 2 and parts[0] == normalized_lang and 'test' in parts[1].lower() and template.name == 'test') or
                            (len(parts) == 3 and parts[0] == normalized_lang and 'test' in parts[1].lower() and template.name == 'test') or
                            (template.language == normalized_lang and template.name == 'test' and not template.framework)
                        )
                        if is_generic_test:
                            template_id = (template.language, template.framework, template.name)
                            if template_id not in seen_templates:
                                templates.append(template)
                                seen_templates.add(template_id)
                                logger.debug(f"Matched generic test template: {key}")
            
            # 3. INSTALL/BUILD: By framework first, then by language
            primary_framework = None
            if frameworks:
                primary_framework = frameworks[0].lower().replace('-', '_').replace('.', '_')
            elif frontend_frameworks:
                primary_framework = frontend_frameworks[0].lower().replace('-', '_').replace('.', '_')
            
            if primary_framework:
                # Look for framework-specific install/build templates
                for key, template in self._template_cache.items():
                    parts = key.split('/')
                    # Match: language/framework/job_name (install, build, etc.)
                    if (len(parts) >= 3 and parts[0] == normalized_lang and 
                        parts[1] == primary_framework and
                        template.name not in ['lint', 'test']):  # Exclude lint/test, they're handled above
                        template_id = (template.language, template.framework, template.name)
                        if template_id not in seen_templates:
                            templates.append(template)
                            seen_templates.add(template_id)
                            logger.debug(f"Matched framework-specific template: {key}")
            
            # Language-only install/build templates (fallback)
            for key, template in self._template_cache.items():
                parts = key.split('/')
                # Match: language/job_name (install, build, etc.) but not lint/test
                if (len(parts) == 2 and parts[0] == normalized_lang and 
                    template.name not in ['lint', 'test'] and
                    template.framework is None):
                    template_id = (template.language, template.framework, template.name)
                    if template_id not in seen_templates:
                        templates.append(template)
                        seen_templates.add(template_id)
                        logger.debug(f"Matched language-only template: {key}")
        
        # Add Docker-specific templates
        if docker:
            for key, template in self._template_cache.items():
                # Match docker templates: docker/*.yml
                parts = key.split('/')
                is_docker_template = (
                    (len(parts) >= 2 and parts[0] == 'docker') or
                    'docker' in key.lower() or
                    (template.language == 'docker')
                )
                if is_docker_template:
                    template_id = (template.language, template.framework, template.name)
                    if template_id not in seen_templates:
                        templates.append(template)
                        seen_templates.add(template_id)
                        logger.debug(f"Matched Docker template: {key}")
        
        # Add Kubernetes templates
        if kubernetes:
            for key, template in self._template_cache.items():
                if 'kubernetes' in key.lower() or 'k8s' in key.lower() or (template.language == 'kubernetes'):
                    template_id = (template.language, template.framework, template.name)
                    if template_id not in seen_templates:
                        templates.append(template)
                        seen_templates.add(template_id)
        
        # Add Terraform templates
        if terraform:
            for key, template in self._template_cache.items():
                if 'terraform' in key.lower() or (template.language == 'terraform'):
                    template_id = (template.language, template.framework, template.name)
                    if template_id not in seen_templates:
                        templates.append(template)
                        seen_templates.add(template_id)
        
        # If no specific templates found, try generic ones
        if not templates:
            logger.warning("No specific templates found, trying generic templates")
            for key, template in self._template_cache.items():
                if 'generic' in key or 'base' in key:
                    template_id = (template.language, template.framework, template.name)
                    if template_id not in seen_templates:
                        templates.append(template)
                        seen_templates.add(template_id)
        
        logger.info(f"Found {len(templates)} unique templates for analysis")
        return templates
    
    def apply_parameters(
        self, 
        template: Template, 
        analysis: Dict[str, Any], 
        user_settings: Dict[str, Any]
    ) -> Template:
        """
        Apply parameters to template, replacing placeholders.
        
        Args:
            template: Template to apply parameters to
            analysis: Repository analysis
            user_settings: User configuration
            
        Returns:
            Template with parameters applied
        """
        # Create parameter mapping
        params = {
            'LANGUAGE': analysis.get('languages', [''])[0] if analysis.get('languages') else '',
            'PACKAGE_MANAGER': analysis.get('package_manager', ''),
            'TEST_RUNNER': analysis.get('test_runner', ''),
            'PYTHON_VERSION': '3.11',
            'NODE_VERSION': '18',
            'DOCKER_IMAGE': user_settings.get('docker_image', '${CI_REGISTRY_IMAGE}:${CI_COMMIT_REF_SLUG}'),
            'DOCKER_REGISTRY': user_settings.get('docker_registry', '${CI_REGISTRY}'),
        }
        
        # Add framework-specific parameters
        frameworks = analysis.get('frameworks', []) + analysis.get('backend_frameworks', [])
        if frameworks:
            params['FRAMEWORK'] = frameworks[0]
        
        # Replace placeholders in script
        new_script = []
        for line in template.script:
            new_line = self._replace_placeholders(line, params)
            new_script.append(new_line)
        
        # Replace in before_script and after_script
        new_before_script = [self._replace_placeholders(line, params) for line in template.before_script]
        new_after_script = [self._replace_placeholders(line, params) for line in template.after_script]
        
        # Replace in image
        new_image = template.image
        if new_image:
            new_image = self._replace_placeholders(new_image, params)
        
        # Create new template with applied parameters
        return Template(
            name=template.name,
            content=template.content,
            language=template.language,
            framework=template.framework,
            stage=template.stage,
            variables=template.variables,
            dependencies=template.dependencies,
            tags=template.tags,
            image=new_image,
            services=template.services,
            cache=template.cache,
            artifacts=template.artifacts,
            only=template.only,
            except_branches=template.except_branches,
            when=template.when,
            allow_failure=template.allow_failure,
            timeout=template.timeout,
            retry=template.retry,
            script=new_script,
            before_script=new_before_script,
            after_script=new_after_script
        )
    
    def _replace_placeholders(self, text: str, params: Dict[str, str]) -> str:
        """Replace ${VAR} placeholders in text."""
        if not isinstance(text, str):
            return text
        
        result = text
        for key, value in params.items():
            # Replace ${VAR} and ${VAR:default}
            pattern = r'\$\{' + re.escape(key) + r'(?::[^}]*)?\}'
            result = re.sub(pattern, str(value), result)
        
        return result
    
    def get_template_by_name(self, name: str) -> Optional[Template]:
        """Get a specific template by name."""
        for template in self._template_cache.values():
            if template.name == name:
                return template
        return None
    
    def list_templates(self) -> List[str]:
        """List all available template keys."""
        return list(self._template_cache.keys())

