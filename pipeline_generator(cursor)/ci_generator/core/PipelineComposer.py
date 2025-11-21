"""
Agent 2: PipelineComposer Agent
Composes CI/CD pipeline from templates and user settings.
"""
import logging
from typing import List, Dict, Any, Set
import yaml

from .models import Template, Job, PipelineConfig

logger = logging.getLogger(__name__)


class PipelineComposer:
    """Composes GitLab CI pipelines from job templates."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def compose_pipeline(
        self, 
        templates: List[Template], 
        user_settings: Dict[str, Any]
    ) -> str:
        """
        Compose a complete pipeline from templates.
        
        Args:
            templates: List of job templates
            user_settings: User configuration
            
        Returns:
            YAML string of the complete pipeline
        """
        self.logger.info(f"Composing pipeline from {len(templates)} templates")
        
        # Convert templates to jobs
        jobs = self.merge_jobs(templates, user_settings)
        
        # Assign stages
        stages = user_settings.get('stages', [])
        if not stages:
            # Auto-detect stages from jobs
            stages = self._detect_stages(jobs)
        
        self.assign_stages(jobs, stages)
        
        # Resolve dependencies
        self.resolve_dependencies(jobs)
        
        # Build pipeline config
        pipeline_config = PipelineConfig(
            stages=stages,
            jobs=jobs,
            variables=user_settings.get('variables', {}),
            cache=user_settings.get('cache_config'),
            workflow=self._build_workflow(user_settings)
        )
        
        # Convert to YAML
        yaml_str = self._to_yaml(pipeline_config, user_settings)
        
        # Inject triggers
        yaml_str = self.inject_triggers(yaml_str, user_settings)
        
        self.logger.info(f"Pipeline composed with {len(jobs)} jobs across {len(stages)} stages")
        return yaml_str
    
    def merge_jobs(
        self, 
        templates: List[Template], 
        user_settings: Dict[str, Any]
    ) -> List[Job]:
        """
        Merge templates into jobs, handling conflicts.
        
        Args:
            templates: List of templates
            user_settings: User configuration
            
        Returns:
            List of unique jobs
        """
        jobs = []
        seen_names: Set[str] = set()
        name_counter: Dict[str, int] = {}
        # Track jobs by name and stage to avoid true duplicates
        # Prefer framework-specific templates over generic ones
        job_by_name_stage: Dict[tuple, Job] = {}
        
        # Sort templates to prefer framework-specific over generic
        # Also prefer combined jobs (build_and_push) over separate ones
        sorted_templates = sorted(templates, key=lambda t: (
            0 if t.framework else 1,  # Framework-specific first
            1 if 'and' in (t.name or '').lower() else 0,  # Combined jobs first (build_and_push)
            t.name or ''
        ))
        
        requested_stages = user_settings.get('stages', []) or []
        
        for template in sorted_templates:
            # Generate unique job name
            base_name = template.name or f"job_{len(jobs)}"
            
            # Determine stage
            stage = template.stage
            if not stage and user_settings.get('stages'):
                # Assign to first appropriate stage
                stage = self._suggest_stage(template, user_settings.get('stages', []))
            stage = stage or 'build'
            
            # If пользователь явно НЕ запросил stage `build`,
            # то build‑джобы (в том числе Docker build/push) нужно выкинуть,
            # даже если они были подобраны по analysis (docker=true).
            if stage == 'build' and requested_stages and 'build' not in requested_stages:
                self.logger.info(
                    f"Skipping build job '{base_name}' because 'build' stage "
                    f"is not present in requested stages: {requested_stages}"
                )
                continue
            
            # Check if we already have a job with this name and stage
            # Also check for Docker job conflicts (build_docker vs build_and_push_docker)
            key = (base_name, stage)
            if key in job_by_name_stage:
                # Skip if we already have this job (prefer first one, which is framework-specific)
                self.logger.debug(f"Skipping duplicate job: {base_name} in stage {stage}")
                continue
            
            # Special handling for Docker jobs: prefer combined jobs
            if stage == 'build' and 'docker' in base_name.lower():
                # If we already have build_and_push_docker, skip separate build_docker and push_docker
                existing_job_names = [j.name for j in jobs]
                if 'build_and_push_docker' in existing_job_names:
                    if base_name in ['build_docker', 'push_docker']:
                        self.logger.debug(f"Skipping {base_name} - build_and_push_docker already exists")
                        continue
                # If we're adding build_and_push_docker, remove separate jobs if they exist
                if 'build_and_push' in base_name.lower():
                    jobs = [j for j in jobs if j.name not in ['build_docker', 'push_docker']]
                    job_by_name_stage = {k: v for k, v in job_by_name_stage.items() if v.name not in ['build_docker', 'push_docker']}
            
            job_name = self._make_unique_name(base_name, seen_names, name_counter)
            seen_names.add(job_name)
            
            # Build job
            job = Job(
                name=job_name,
                stage=stage,
                script=template.script,
                image=template.image or user_settings.get('images', {}).get('default', 'python:3.11'),
                services=template.services,
                variables=template.variables,
                dependencies=template.dependencies,
                needs=template.dependencies.copy(),
                tags=template.tags,
                cache=template.cache,
                artifacts=template.artifacts,
                only=template.only,
                except_branches=template.except_branches,
                when=template.when,
                allow_failure=template.allow_failure,
                timeout=template.timeout,
                retry=template.retry,
                before_script=template.before_script,
                after_script=template.after_script
            )
            
            jobs.append(job)
            job_by_name_stage[key] = job
        
        return jobs
    
    def _make_unique_name(
        self, 
        base_name: str, 
        seen_names: Set[str], 
        name_counter: Dict[str, int]
    ) -> str:
        """Generate a unique job name."""
        if base_name not in seen_names:
            name_counter[base_name] = 0
            return base_name
        
        # Increment counter
        name_counter[base_name] = name_counter.get(base_name, 0) + 1
        new_name = f"{base_name}_{name_counter[base_name]}"
        
        # Recursively ensure uniqueness
        if new_name in seen_names:
            return self._make_unique_name(base_name, seen_names, name_counter)
        
        return new_name
    
    def _suggest_stage(self, template: Template, stages: List[str]) -> str:
        """Suggest appropriate stage for a template based on its name and content."""
        name_lower = template.name.lower() if template.name else ''
        script_lower = ' '.join(template.script).lower()
        content = f"{name_lower} {script_lower}"
        
        # Stage detection logic
        stage_mapping = {
            'lint': ['lint', 'linter', 'flake8', 'eslint', 'pylint'],
            'test': ['test', 'pytest', 'jest', 'unittest', 'spec'],
            'build': ['build', 'compile', 'docker build', 'npm run build'],
            'security': ['security', 'bandit', 'snyk', 'trivy', 'scan'],
            'deploy': ['deploy', 'kubectl', 'helm', 'terraform apply'],
            'install': ['install', 'deps', 'dependencies', 'pip install', 'npm install'],
        }
        
        # Find best matching stage
        for stage in stages:
            if stage.lower() in stage_mapping:
                keywords = stage_mapping[stage.lower()]
                if any(keyword in content for keyword in keywords):
                    return stage
        
        # Default to first stage or 'build'
        return stages[0] if stages else 'build'
    
    def assign_stages(self, jobs: List[Job], stages: List[str]) -> None:
        """
        Assign stages to jobs based on user settings.
        
        Args:
            jobs: List of jobs
            stages: List of stage names
        """
        if not stages:
            return
        
        # Group jobs by suggested stage
        stage_groups: Dict[str, List[Job]] = {stage: [] for stage in stages}
        unassigned = []
        
        for job in jobs:
            if job.stage and job.stage in stages:
                stage_groups[job.stage].append(job)
            else:
                unassigned.append(job)
        
        # Assign unassigned jobs
        for job in unassigned:
            suggested = self._suggest_stage_from_job(job, stages)
            job.stage = suggested
            stage_groups[suggested].append(job)
        
        self.logger.debug(f"Stage assignment: {[(stage, len(jobs)) for stage, jobs in stage_groups.items()]}")
    
    def _suggest_stage_from_job(self, job: Job, stages: List[str]) -> str:
        """Suggest stage for a job based on its name and script."""
        name_lower = job.name.lower()
        script_lower = ' '.join(job.script).lower()
        content = f"{name_lower} {script_lower}"
        
        stage_mapping = {
            'lint': ['lint', 'linter', 'flake8', 'eslint'],
            'test': ['test', 'pytest', 'jest', 'unittest'],
            'build': ['build', 'compile', 'docker'],
            'security': ['security', 'bandit', 'snyk', 'trivy'],
            'deploy': ['deploy', 'kubectl', 'helm'],
        }
        
        for stage in stages:
            if stage.lower() in stage_mapping:
                keywords = stage_mapping[stage.lower()]
                if any(keyword in content for keyword in keywords):
                    return stage
        
        return stages[0] if stages else 'build'
    
    def resolve_dependencies(self, jobs: List[Job]) -> None:
        """
        Resolve job dependencies and prevent circular references.
        Also auto-detect common dependencies (e.g., test depends on install).
        
        Args:
            jobs: List of jobs to process
        """
        job_names = {job.name for job in jobs}
        job_by_name = {job.name: job for job in jobs}
        
        # Common dependency patterns
        install_jobs = [j.name for j in jobs if 'install' in j.name.lower() and j.stage == 'install']
        build_jobs = [j.name for j in jobs if 'build' in j.name.lower() and j.stage == 'build']
        
        for job in jobs:
            # Filter out invalid dependencies
            valid_needs = [dep for dep in job.needs if dep in job_names]
            job.needs = valid_needs
            
            # Auto-detect common dependencies
            job_name_lower = job.name.lower()
            job_stage = job.stage
            
            # Jobs in later stages typically depend on install
            if job_stage in ['lint', 'test', 'build', 'security', 'deploy'] and install_jobs:
                # Add install dependency if not already present
                for install_job in install_jobs:
                    if install_job not in job.needs:
                        job.needs.append(install_job)
            
            # Build jobs might depend on test
            if job_stage == 'build' and 'test' in job_name_lower:
                test_jobs = [j.name for j in jobs if 'test' in j.name.lower() and j.stage == 'test']
                for test_job in test_jobs:
                    if test_job not in job.needs:
                        job.needs.append(test_job)
            
            # Deploy might depend on build
            if job_stage == 'deploy' and build_jobs:
                for build_job in build_jobs:
                    if build_job not in job.needs:
                        job.needs.append(build_job)
            
            # Remove duplicates
            job.needs = list(dict.fromkeys(job.needs))  # Preserve order, remove duplicates
            
            # Check for circular dependencies
            if self._has_circular_dependency(job, jobs, set()):
                self.logger.warning(f"Circular dependency detected for job {job.name}, clearing needs")
                job.needs = []
    
    def _has_circular_dependency(
        self, 
        job: Job, 
        all_jobs: List[Job], 
        visited: Set[str]
    ) -> bool:
        """Check if job has circular dependencies."""
        if job.name in visited:
            return True
        
        visited.add(job.name)
        
        for dep_name in job.needs:
            dep_job = next((j for j in all_jobs if j.name == dep_name), None)
            if dep_job and self._has_circular_dependency(dep_job, all_jobs, visited.copy()):
                return True
        
        return False
    
    def _detect_stages(self, jobs: List[Job]) -> List[str]:
        """Auto-detect stages from jobs."""
        stages = set()
        for job in jobs:
            if job.stage:
                stages.add(job.stage)
        
        # Default stages if none found
        if not stages:
            return ['build', 'test', 'deploy']
        
        # Order stages logically
        stage_order = ['install', 'lint', 'test', 'build', 'security', 'deploy']
        ordered = [s for s in stage_order if s in stages]
        remaining = sorted(stages - set(ordered))
        
        return ordered + remaining
    
    def _build_workflow(self, user_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Build workflow rules from user settings."""
        triggers = user_settings.get('triggers', {})
        rules = []
        
        # Push triggers
        if triggers.get('on_push'):
            branches = triggers['on_push']
            if isinstance(branches, list):
                for branch in branches:
                    rules.append({
                        'if': f'$CI_COMMIT_BRANCH == "{branch}"'
                    })
            elif isinstance(branches, bool) and branches:
                rules.append({'if': '$CI_PIPELINE_SOURCE == "push"'})
        
        # Merge request triggers
        if triggers.get('on_merge_request'):
            rules.append({'if': '$CI_PIPELINE_SOURCE == "merge_request_event"'})
        
        # Tag triggers
        if triggers.get('on_tags'):
            tag_pattern = triggers['on_tags']
            rules.append({'if': f'$CI_COMMIT_TAG =~ /{tag_pattern}/'})
        
        # Schedule triggers
        if triggers.get('schedule'):
            rules.append({'if': '$CI_PIPELINE_SOURCE == "schedule"'})
        
        # Manual triggers
        if triggers.get('manual'):
            rules.append({'if': '$CI_PIPELINE_SOURCE == "web"'})
        
        return {'rules': rules} if rules else None
    
    def inject_triggers(self, yaml_str: str, user_settings: Dict[str, Any]) -> str:
        """
        Inject trigger rules into pipeline YAML.
        
        Args:
            yaml_str: Pipeline YAML
            user_settings: User configuration
            
        Returns:
            YAML with triggers injected
        """
        try:
            data = yaml.safe_load(yaml_str)
            if not isinstance(data, dict):
                return yaml_str
            
            workflow = self._build_workflow(user_settings)
            if workflow:
                data['workflow'] = workflow
            
            # Also add only/except to individual jobs if specified
            triggers = user_settings.get('triggers', {})
            
            if 'workflow' in data and data['workflow'].get('rules'):
                return yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
            
            return yaml_str
        
        except Exception as e:
            self.logger.error(f"Error injecting triggers: {e}")
            return yaml_str
    
    def _to_yaml(self, config: PipelineConfig, user_settings: Dict[str, Any]) -> str:
        """Convert PipelineConfig to YAML string."""
        pipeline_dict = {}
        
        # Add stages
        if config.stages:
            pipeline_dict['stages'] = config.stages
        
        # Add variables
        if config.variables:
            pipeline_dict['variables'] = config.variables
        
        # Add cache
        if config.cache:
            pipeline_dict['cache'] = config.cache
        
        # Add workflow
        if config.workflow:
            pipeline_dict['workflow'] = config.workflow
        
        # Add default section
        if config.default:
            pipeline_dict['default'] = config.default
        
        # Add jobs
        for job in config.jobs:
            job_dict = self._job_to_dict(job, user_settings)
            pipeline_dict[job.name] = job_dict
        
        return yaml.dump(pipeline_dict, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    def _job_to_dict(self, job: Job, user_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Job to dictionary."""
        job_dict = {
            'stage': job.stage,
            'script': job.script
        }
        
        # Add optional fields
        if job.image:
            job_dict['image'] = job.image
        
        if job.services:
            job_dict['services'] = job.services
        
        if job.variables:
            job_dict['variables'] = job.variables
        
        if job.needs:
            job_dict['needs'] = job.needs
        
        if job.tags:
            job_dict['tags'] = job.tags
        
        if job.cache:
            job_dict['cache'] = job.cache
        
        if job.artifacts:
            job_dict['artifacts'] = job.artifacts
        
        if job.before_script:
            job_dict['before_script'] = job.before_script
        
        if job.after_script:
            job_dict['after_script'] = job.after_script
        
        if job.only:
            job_dict['only'] = job.only
        
        if job.except_branches:
            job_dict['except'] = job.except_branches
        
        if job.when:
            job_dict['when'] = job.when
        
        if job.allow_failure:
            job_dict['allow_failure'] = job.allow_failure
        
        if job.timeout:
            job_dict['timeout'] = job.timeout
        
        if job.retry:
            job_dict['retry'] = job.retry
        
        # Add rules if workflow rules are used
        if user_settings.get('triggers', {}).get('on_push') or user_settings.get('triggers', {}).get('on_merge_request'):
            rules = []
            triggers = user_settings.get('triggers', {})
            
            if triggers.get('on_push'):
                branches = triggers['on_push']
                if isinstance(branches, list):
                    for branch in branches:
                        rules.append({'if': f'$CI_COMMIT_BRANCH == "{branch}"'})
                elif isinstance(branches, bool) and branches:
                    rules.append({'if': '$CI_PIPELINE_SOURCE == "push"'})
            
            if triggers.get('on_merge_request'):
                rules.append({'if': '$CI_PIPELINE_SOURCE == "merge_request_event"'})
            
            if rules:
                job_dict['rules'] = rules
        
        return job_dict

