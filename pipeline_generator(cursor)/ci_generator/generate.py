"""
Agent 5: Generator Agent
Main coordinator that orchestrates all agents to generate CI/CD pipelines.
"""
import logging
from typing import Dict, Any, Tuple, Optional, List
import json

from .core.TemplateLibrary import TemplateLibrary
from .core.PipelineComposer import PipelineComposer
from .core.Validator import Validator
from .core.ExplainEngine import ExplainEngine
from .core.VariableAnalyzer import VariableAnalyzer
from .core.models import PipelineResult, ValidationResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PipelineGenerator:
    """
    Main Generator Agent that coordinates all other agents.
    
    This agent:
    1. Receives analysis and user_settings as JSON
    2. Requests templates from TemplateLibrary
    3. Composes pipeline via PipelineComposer
    4. Validates via Validator
    5. Generates explanation via ExplainEngine
    6. Returns YAML + explanation
    """
    
    def __init__(
        self, 
        templates_dir: Optional[str] = None,
        gitlab_url: Optional[str] = None,
        gitlab_token: Optional[str] = None
    ):
        """
        Initialize PipelineGenerator.
        
        Args:
            templates_dir: Path to templates directory
            gitlab_url: GitLab instance URL for lint API (optional)
            gitlab_token: GitLab token for API access (optional)
        """
        self.template_library = TemplateLibrary(templates_dir)
        self.pipeline_composer = PipelineComposer()
        self.validator = Validator(gitlab_url, gitlab_token)
        self.explain_engine = ExplainEngine()
        self.variable_analyzer = VariableAnalyzer()
        self.logger = logging.getLogger(__name__)
    
    def generate_pipeline(
        self, 
        analysis: Dict[str, Any], 
        user_settings: Dict[str, Any]
    ) -> Tuple[str, str, ValidationResult, List]:
        """
        Generate a complete CI/CD pipeline from analysis and user settings.
        
        Args:
            analysis: Repository analysis data
            user_settings: User configuration
            
        Returns:
            Tuple of (yaml_string, human_readable_explanation, validation_result, required_variables)
        """
        self.logger.info("Starting pipeline generation")
        self.logger.debug(f"Analysis: {json.dumps(analysis, indent=2)}")
        self.logger.debug(f"User settings: {json.dumps(user_settings, indent=2)}")
        
        try:
            # Step 1: Get templates from TemplateLibrary
            self.logger.info("Step 1: Loading templates")
            templates = self.template_library.get_templates_for(analysis)
            
            if not templates:
                self.logger.warning("No templates found, generating minimal pipeline")
                yaml_content = self._generate_minimal_pipeline(analysis, user_settings)
                explanation = "Minimal pipeline generated - no matching templates found."
                validation_result = self.validator.validate_pipeline(yaml_content)
                required_variables = self.variable_analyzer.analyze_required_variables(yaml_content)
                return yaml_content, explanation, validation_result, required_variables
            
            self.logger.info(f"Found {len(templates)} templates")
            
            # Filter templates by requested stages if user specified stages
            # Now any stage can be requested regardless of framework
            requested_stages = user_settings.get('stages', [])
            if requested_stages:
                # Map stage names to keywords and job names for filtering
                stage_keywords = {
                    'install': ['install', 'deps', 'dependencies', 'install_dependencies'],
                    'lint': ['lint', 'linter', 'flake8', 'eslint', 'pylint', 'black', 'isort'],
                    'test': ['test', 'pytest', 'jest', 'unittest', 'mocha', 'jasmine'],
                    'build': ['build', 'compile', 'docker build', 'build_docker', 'build_and_push', 'push_docker'],
                    'security': ['security', 'bandit', 'snyk', 'trivy', 'scan', 'security_scan'],
                    'deploy': ['deploy', 'kubectl', 'helm', 'terraform', 'migrations', 'run_migrations', 'deploy_docker']
                }
                
                # Filter templates that match requested stages
                filtered_templates = []
                for template in templates:
                    template_stage = template.stage
                    template_name_lower = (template.name or '').lower()
                    template_script_lower = ' '.join(template.script).lower()
                    template_content = f"{template_name_lower} {template_script_lower}"
                    
                    # Check if template matches any requested stage
                    matches = False
                    for stage in requested_stages:
                        # Direct stage match
                        if template_stage == stage:
                            matches = True
                            break
                        
                        # Check by keywords if stage not explicitly set
                        if stage in stage_keywords:
                            keywords = stage_keywords[stage]
                            # Check if template name or script contains keywords
                            if any(keyword in template_content for keyword in keywords):
                                matches = True
                                break
                            # Also check if template name matches stage
                            if stage in template_name_lower:
                                matches = True
                                break
                    
                    if matches:
                        filtered_templates.append(template)
                
                if filtered_templates:
                    templates = filtered_templates
                    self.logger.info(f"Filtered to {len(templates)} templates matching requested stages: {requested_stages}")
                else:
                    self.logger.warning(f"No templates found for requested stages: {requested_stages}. Using all available templates.")
            
            # Step 2: Apply parameters to templates
            self.logger.info("Step 2: Applying parameters to templates")
            parameterized_templates = []
            for template in templates:
                try:
                    param_template = self.template_library.apply_parameters(
                        template, analysis, user_settings
                    )
                    parameterized_templates.append(param_template)
                except Exception as e:
                    self.logger.error(f"Error applying parameters to template {template.name}: {e}")
                    continue
            
            # Step 3: Compose pipeline
            self.logger.info("Step 3: Composing pipeline")
            yaml_content = self.pipeline_composer.compose_pipeline(
                parameterized_templates, 
                user_settings
            )
            
            # Step 4: Validate pipeline
            self.logger.info("Step 4: Validating pipeline")
            validation_result = self.validator.validate_pipeline(yaml_content)
            
            if not validation_result.is_valid:
                self.logger.warning(f"Pipeline validation failed with {len(validation_result.errors)} errors")
            else:
                self.logger.info("Pipeline validation passed")
            
            # Step 5: Generate explanation
            self.logger.info("Step 5: Generating explanation")
            explanation = self.explain_engine.explain_pipeline(yaml_content)
            
            # Step 6: Analyze required variables
            self.logger.info("Step 6: Analyzing required variables")
            required_variables = self.variable_analyzer.analyze_required_variables(yaml_content)
            
            self.logger.info("Pipeline generation complete")
            
            return yaml_content, explanation, validation_result, required_variables
        
        except Exception as e:
            self.logger.error(f"Error generating pipeline: {e}", exc_info=True)
            # Return error result
            error_yaml = self._generate_error_pipeline(str(e))
            error_explanation = f"Error generating pipeline: {str(e)}"
            error_validation = ValidationResult(
                is_valid=False,
                errors=[f"Generation error: {str(e)}"]
            )
            return error_yaml, error_explanation, error_validation, []
    
    def _generate_minimal_pipeline(
        self, 
        analysis: Dict[str, Any], 
        user_settings: Dict[str, Any]
    ) -> str:
        """Generate a minimal pipeline when no templates are found."""
        stages = user_settings.get('stages', ['build', 'test', 'deploy'])
        platform = user_settings.get('platform', 'gitlab')
        
        if platform != 'gitlab':
            return self._generate_minimal_pipeline_gitlab(analysis, user_settings, stages)
        
        # Generate minimal GitLab CI pipeline
        pipeline = {
            'stages': stages,
            'variables': user_settings.get('variables', {})
        }
        
        # Add a basic build job
        language = analysis.get('languages', [''])[0] if analysis.get('languages') else 'python'
        package_manager = analysis.get('package_manager', 'pip')
        
        if language == 'python':
            image = 'python:3.11'
            script = [
                f'{package_manager} install -r requirements.txt' if package_manager == 'pip' else f'{package_manager} install',
                'echo "Build complete"'
            ]
        elif language in ['javascript', 'typescript']:
            image = 'node:18'
            pm = package_manager or 'npm'
            script = [
                f'{pm} install',
                f'{pm} run build'
            ]
        else:
            image = 'alpine:latest'
            script = ['echo "Build complete"']
        
        pipeline['build'] = {
            'stage': stages[0] if stages else 'build',
            'image': image,
            'script': script
        }
        
        # Add test job if test_runner is detected
        test_runner = analysis.get('test_runner')
        if test_runner and 'test' in stages:
            test_script = []
            if test_runner == 'pytest':
                test_script = ['pytest']
            elif test_runner == 'jest':
                test_script = ['npm test']
            elif test_runner == 'unittest':
                test_script = ['python -m unittest']
            
            if test_script:
                pipeline['test'] = {
                    'stage': 'test',
                    'image': image,
                    'script': test_script,
                    'needs': ['build']
                }
        
        import yaml
        return yaml.dump(pipeline, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    def _generate_minimal_pipeline_gitlab(
        self, 
        analysis: Dict[str, Any], 
        user_settings: Dict[str, Any],
        stages: list
    ) -> str:
        """Generate minimal GitLab CI pipeline."""
        return self._generate_minimal_pipeline(analysis, user_settings)
    
    def _generate_error_pipeline(self, error_message: str) -> str:
        """Generate an error pipeline."""
        import yaml
        pipeline = {
            'stages': ['error'],
            'error_job': {
                'stage': 'error',
                'script': [
                    f'echo "Pipeline generation failed: {error_message}"',
                    'exit 1'
                ]
            }
        }
        return yaml.dump(pipeline, default_flow_style=False, sort_keys=False, allow_unicode=True)


def generate_pipeline(
    analysis: Dict[str, Any], 
    user_settings: Dict[str, Any],
    templates_dir: Optional[str] = None,
    gitlab_url: Optional[str] = None,
    gitlab_token: Optional[str] = None
) -> Tuple[str, str, ValidationResult, List]:
    """
    Convenience function to generate a pipeline.
    
    Args:
        analysis: Repository analysis data
        user_settings: User configuration
        templates_dir: Path to templates directory
        gitlab_url: GitLab instance URL for lint API (optional)
        gitlab_token: GitLab token for API access (optional)
        
    Returns:
        Tuple of (yaml_string, explanation, validation_result, required_variables)
    """
    generator = PipelineGenerator(templates_dir, gitlab_url, gitlab_token)
    return generator.generate_pipeline(analysis, user_settings)


def generate_pipeline_from_json(
    analysis_json: str,
    user_settings_json: str,
    templates_dir: Optional[str] = None,
    gitlab_url: Optional[str] = None,
    gitlab_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate pipeline from JSON strings.
    
    Args:
        analysis_json: JSON string of analysis
        user_settings_json: JSON string of user settings
        templates_dir: Path to templates directory
        gitlab_url: GitLab instance URL for lint API (optional)
        gitlab_token: GitLab token for API access (optional)
        
    Returns:
        Dictionary with yaml, explanation, and validation results
    """
    try:
        analysis = json.loads(analysis_json)
        user_settings = json.loads(user_settings_json)
    except json.JSONDecodeError as e:
        return {
            'error': f'Invalid JSON: {str(e)}',
            'yaml': '',
            'explanation': '',
            'validation': {
                'is_valid': False,
                'errors': [f'JSON parsing error: {str(e)}']
            }
        }
    
    yaml_content, explanation, validation, required_variables = generate_pipeline(
        analysis, user_settings, templates_dir, gitlab_url, gitlab_token
    )
    
    # Extract stages from YAML
    try:
        import yaml
        pipeline_data = yaml.safe_load(yaml_content)
        stages = pipeline_data.get('stages', [])
    except:
        stages = []
    
    return {
        'yaml': yaml_content,
        'explanation': explanation,
        'validation': {
            'is_valid': validation.is_valid,
            'errors': validation.errors,
            'warnings': validation.warnings,
            'security_issues': validation.security_issues,
            'yaml_errors': validation.yaml_errors,
            'gitlab_lint_errors': validation.gitlab_lint_errors,
            'circular_dependencies': validation.circular_dependencies,
            'missing_dependencies': validation.missing_dependencies
        },
        'required_variables': [
            {
                'name': v.name,
                'description': v.description,
                'required': v.required,
                'default_value': v.default_value,
                'example': v.example,
                'job_usage': v.job_usage
            }
            for v in required_variables
        ],
        'jobs_count': len([k for k in (pipeline_data.keys() if isinstance(pipeline_data, dict) else []) 
                          if k not in ['stages', 'variables', 'workflow', 'cache', 'include', 'default']]),
        'stages': stages
    }

