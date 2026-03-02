"""SkillsLoader: merges multiple SkillSource instances and formats output."""

from __future__ import annotations

from xml.sax.saxutils import escape

from ai.agent.skills.base import Skill, SkillSource


class SkillsLoader:
    """Merges multiple SkillSource instances with first-source-wins priority.

    Sources are checked in order; the first source that provides a skill
    for a given name wins. This means earlier sources shadow later ones,
    so pass higher-priority sources first (e.g. user DB before built-ins).

    Example::

        loader = SkillsLoader([user_source, FileSkillSource()])
        xml = loader.build_summary_xml()           # for system prompt
        content = loader.load_content("my-skill")  # for load_skill tool
        context = loader.build_context("my-skill") # for prompt injection

    Args:
        sources: Ordered list of SkillSource instances.
    """

    def __init__(self, sources: list[SkillSource]) -> None:
        self._sources = sources

    def list_metadata(self) -> list[Skill]:
        """Return merged skill metadata. First source wins on name conflicts."""
        by_name: dict[str, Skill] = {}
        # Iterate in reverse so earlier sources overwrite later ones
        for source in reversed(self._sources):
            for skill in source.list_metadata():
                by_name[skill.name] = skill
        return list(by_name.values())

    def load_content(self, name: str) -> str | None:
        """Return body content from the first source that has the skill."""
        for source in self._sources:
            content = source.load_content(name)
            if content is not None:
                return content
        return None

    def build_summary_xml(self) -> str:
        """Return an ``<available_skills>`` XML block for the system prompt.

        Lists all available skills with their names and descriptions.
        """
        skills = self.list_metadata()
        parts: list[str] = []
        for skill in skills:
            parts.append(
                "\t<skill>\n"
                f"\t\t<name>{escape(skill.name)}</name>\n"
                f"\t\t<description>{escape(skill.description)}</description>\n"
                "\t</skill>"
            )
        return "<available_skills>\n" + "\n".join(parts) + "\n</available_skills>"

    def build_context(self, name: str) -> str | None:
        """Return a formatted markdown block for injecting a skill into an agent prompt.

        Returns None if the skill is not found.
        """
        content = self.load_content(name)
        if content is None:
            return None
        return f"## Skill: {name}\n\n{content}"
