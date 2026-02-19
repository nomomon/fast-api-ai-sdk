"""Prompt repository for data access."""

from pathlib import Path

import frontmatter


class PromptRepository:
    """Repository for prompt data access operations.

    Loads prompts from markdown files with YAML frontmatter in the
    ``prompts`` directory next to this module.
    """

    PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

    def _load_prompts(self) -> list[dict]:
        """Load all prompts from prompts/*.md (frontmatter + body as content)."""
        result: list[dict] = []
        if not self.PROMPTS_DIR.is_dir():
            return result
        for path in sorted(self.PROMPTS_DIR.glob("*.md")):
            try:
                post = frontmatter.load(path)
                meta = post.metadata
                prompt_id = meta.get("id")
                name = meta.get("name", path.stem)
                content = (post.content or "").strip()
                result.append(
                    {
                        "id": prompt_id,
                        "name": name,
                        "content": content or None,
                    }
                )
            except Exception:
                continue
        return result

    def get_all(self) -> list[dict]:
        """Get all prompts.

        Returns:
            List of prompt dictionaries
        """
        return self._load_prompts()

    def get_by_id(self, prompt_id: str) -> dict | None:
        """Get prompt by ID.

        Args:
            prompt_id: Prompt ID

        Returns:
            Prompt dictionary or None if not found
        """
        for prompt in self.get_all():
            if prompt["id"] == prompt_id:
                return prompt
        return None

    def get_content_by_id(self, prompt_id: str) -> str | None:
        """Get prompt content by ID.

        Args:
            prompt_id: Prompt ID

        Returns:
            Prompt content string or None if not found
        """
        prompt = self.get_by_id(prompt_id)
        return prompt.get("content") if prompt else None
