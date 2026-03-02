# Skills System

Extensible loader for agent skills — markdown-based instructions that teach an agent how to perform specific tasks.

## Constraints

Skills are **markdown-only**. A skill is a single `SKILL.md` file with YAML frontmatter and a markdown body. No scripts, referenced assets, sub-files, or executable code. The agent reads the body as plain text context.

## Architecture

```
SkillSource (ABC)
    ├── FileSkillSource   — reads skills/<name>/SKILL.md from a directory
    └── DBSkillSource     — extend this yourself (see below)

SkillsLoader([source1, source2, ...])
    ├── list_metadata()       — merged list (first source wins by name)
    ├── load_content(name)    — body from first source that has it
    ├── build_summary_xml()   — <available_skills> block for system prompt
    └── build_context(name)   — markdown block for prompt injection
```

## Extending with a database source

Subclass `SkillSource` anywhere in your codebase — no changes to this package needed:

```python
from ai.agent.skills import Skill, SkillSource, SkillsLoader, FileSkillSource

class DBSkillSource(SkillSource):
    def __init__(self, repo, user_id): ...

    def list_metadata(self) -> list[Skill]:
        return [Skill(name=r.name, description=r.description) for r in ...]

    def load_content(self, name: str) -> str | None:
        return repo.get_content_by_name(user_id, name)

# User skills shadow built-ins by name
loader = SkillsLoader([DBSkillSource(repo, user_id), FileSkillSource()])
```
