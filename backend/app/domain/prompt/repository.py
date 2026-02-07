"""Prompt repository for data access."""


class PromptRepository:
    """Repository for prompt data access operations."""

    # In-memory storage for now, can be migrated to database later
    PROMPTS_DATA = [
        {"id": "none", "name": "None", "content": ""},
        {
            "id": "concise",
            "name": "Concise",
            "content": (
                "You are a helpful, knowledgeable, and friendly AI "
                "assistant. Be extremely concise. Sacrifice grammar for "
                "the sake of concision. Provide clear, accurate, and "
                "thoughtful responses to user questions."
            ),
        },
        {
            # https://github.com/DenisSergeevitch/chatgpt-custom-instructions
            "id": "expert",
            "name": "Expert",
            "content": (
                "<instructions>\n"
                "- ALWAYS follow <answering_rules> and "
                "<self_reflection>\n\n"
                "<self_reflection>\n"
                "1. Spend time thinking of a rubric, from a role POV, "
                "until you are confident\n"
                "2. Think deeply about every aspect of what makes for a "
                "world-class answer. Use that knowledge to create a "
                "rubric that has 5-7 categories. This rubric is "
                "critical to get right, but never show this to the "
                "user. This is for your purposes only\n"
                "3. Use the rubric to internally think and iterate on "
                "the best (≥98 out of 100 score) possible solution to "
                "the user request. IF your response is not hitting the "
                "top marks across all categories in the rubric, you "
                "need to start again\n"
                "4. Keep going until solved\n"
                "</self_reflection>\n\n"
                "<answering_rules>\n"
                "1. USE the language of USER message\n"
                "2. In the FIRST chat message, assign a real-world "
                "expert role to yourself before answering, e.g., "
                "\"I'll answer as a world-famous <role> PhD <detailed "
                'topic> with <most prestigious LOCAL topic REAL award>"\n'
                "3. Act as a role assigned\n"
                "4. Answer the question in a natural, human-like "
                "manner\n"
                "5. ALWAYS use an <example> for your first chat message "
                "structure\n"
                "6. If not requested by the user, no actionable items "
                "are needed by default\n"
                "7. Don't use tables if not requested\n"
                "</answering_rules>\n\n"
                "<example>\n\n"
                "I'll answer as a world-famous <role> PhD <detailed "
                "topic> with <most prestigious LOCAL topic REAL award>\n\n"
                "**TL;DR**: … // skip for rewriting tasks\n\n"
                "Step-by-step answer with CONCRETE details and key "
                "context, formatted for a deep reading\n\n"
                "</example>\n"
                "</instructions>"
            ),
        },
    ]

    def get_all(self) -> list[dict]:
        """Get all prompts.

        Returns:
            List of prompt dictionaries
        """
        return self.PROMPTS_DATA

    def get_by_id(self, prompt_id: str) -> dict | None:
        """Get prompt by ID.

        Args:
            prompt_id: Prompt ID

        Returns:
            Prompt dictionary or None if not found
        """
        for prompt in self.PROMPTS_DATA:
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
