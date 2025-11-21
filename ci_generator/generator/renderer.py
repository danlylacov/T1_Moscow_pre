"""
renderer.py

Рендерит pipeline для GitLab и Jenkins.
Ищет шаблон стадии в директориях:
  templates_root/<platform>/stages/python/<stage>.<ext>
  templates_root/<platform>/stages/docker/<stage>.<ext>
  templates_root/<platform>/stages/kubernetes/<stage>.<ext>
  templates_root/<platform>/stages/shared/<stage>.<ext>

Если шаблона для стадии нет — стадия пропускается (маловероятно).
"""

import os
from jinja2 import Environment, FileSystemLoader
from typing import List, Dict

class PipelineRenderer:
    def __init__(self, templates_root: str = "pipelines"):
        self.templates_root = templates_root
        self.env = Environment(loader=FileSystemLoader(templates_root), trim_blocks=True, lstrip_blocks=True)

        # search order for stage templates
        # tests вынесены в отдельную директорию "tests"
        self.stage_dirs = ["tests", "python", "docker", "kubernetes", "shared"]

    def _find_stage_template(self, platform: str, stage: str, ext: str) -> str:
        """
        Возвращает относительный путь шаблона (от templates_root) или None.
        ext: 'gitlab.j2' or 'jenkins.j2' suffix.
        """
        base = os.path.join(platform, "stages")
        for d in self.stage_dirs:
            candidate = os.path.join(base, d, f"{stage}.{ext}")
            if os.path.exists(os.path.join(self.templates_root, candidate)):
                return candidate
        return None

    def render_gitlab(self, stages: List[str], ctx: Dict) -> str:
        parts = []
        # base header (stages list + variables)
        header_tpl = self.env.get_template("gitlab/base_header.j2")
        parts.append(header_tpl.render(stages=stages, ctx=ctx))

        # append each stage template content
        for s in stages:
            tpl_path = self._find_stage_template("gitlab", s, "gitlab.j2")
            if tpl_path:
                tpl = self.env.get_template(tpl_path)
                parts.append(tpl.render(ctx=ctx))
            else:
                # skip silently if no template (extensible)
                parts.append(f"# NOTE: no template for stage: {s}\n")

        return "\n".join(parts)

    def render_jenkins(self, stages: List[str], ctx: Dict) -> str:
        parts = []
        header_tpl = self.env.get_template("jenkins/base_header.j2")
        parts.append(header_tpl.render(ctx=ctx))

        # include each stage snippet
        for s in stages:
            tpl_path = self._find_stage_template("jenkins", s, "jenkins.j2")
            if tpl_path:
                tpl = self.env.get_template(tpl_path)
                parts.append(tpl.render(ctx=ctx))
            else:
                parts.append(f"// NOTE: no template for stage: {s}\n")

        # close pipeline (header already includes closing)
        return "\n".join(parts)
