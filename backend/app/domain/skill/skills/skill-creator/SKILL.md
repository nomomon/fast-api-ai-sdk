---
name: skill-creator
description: Guide for creating and updating skills in this system. Use when the user wants to create a new skill or change an existing skill. Skills are markdown-only (SKILL.md with frontmatter and body); no scripts, references, assets, or packaging.
---

# Skill Creator

This skill describes how skills work in this system and how to create or update them.

## Two kinds of skills

- **Default skills**: Read-only markdown files under `skills/<skill-name>/SKILL.md` (e.g. this skill). They are shared and cannot be modified via tools.
- **User skills**: Stored per user in the database. The **update_skill** tool creates or updates only the *current* user's skill. Each user has their own set of custom skills; **load_skill** resolves the user's skill first, then falls back to the default skill by name.

## What is supported

- **One file per default skill**: Each default skill is a folder `skills/<skill-name>/` containing a single file `SKILL.md`.
- **SKILL.md format**: YAML frontmatter followed by Markdown body. Only `name` and `description` are used in the frontmatter; the body is the skill instructions.
- **Naming**: The frontmatter `name` must match the directory name (for defaults) or the skill name (for user skills). Names must be 1–64 characters, lowercase letters and numbers and hyphens only, no leading or trailing hyphen, no consecutive hyphens (e.g. `my-skill`, `data-analysis`).

## Tools

- **load_skill(skill_name)**: Loads the skill body. Resolves the current user's skill by that name first (from the database); if none, loads the default from `skills/<skill_name>/SKILL.md`. Use when the agent needs to activate a skill and read its instructions.
- **update_skill(skill_name, description, body)**: Creates or overwrites the *current user's* skill in the database (does not write files). Use when creating a new user skill or updating an existing one. `skill_name` must be valid per the naming rules above; invalid names or missing auth cause the tool to return false.

## SKILL.md structure (for content)

```yaml
---
name: skill-name
description: A short description of what the skill does and when to use it.
---

Markdown body: step-by-step instructions, examples, and guidance for the agent.
```

- **name**: Must match the folder name (defaults) or skill name (user). Used for discovery and for `load_skill` / `update_skill`.
- **description**: Shown in the list of available skills so the model knows when to use this skill. Include both what it does and when to use it.
- **Body**: Instructions loaded when the skill is activated. Write clearly and concisely; avoid unnecessary context.

## What is not supported

This system does **not** support:

- Scripts, references, or assets directories (no `scripts/`, `references/`, `assets/`).
- Packaging into .skill files or init/package scripts.
- Loading multiple files per skill; only the single SKILL.md body (or DB content) is read.

Keep skill content in the body. Do not reference other files inside the skill folder; they are not loaded by the agent.

## Creating or updating a user skill

1. Decide the skill name (must follow the naming rules; e.g. `pdf-help`, `code-review`).
2. Call **update_skill(skill_name, description, body)** with:
   - `skill_name`: The name (same as frontmatter `name`).
   - `description`: One or two sentences for what the skill does and when to use it.
   - `body`: The full Markdown instructions for the agent.
3. The skill is created or updated for the current user in the database. The agent can then use **load_skill(skill_name)** to read the body when the skill is relevant.

Keep the body focused and under a few hundred lines when possible. Put the most important "when to use" information in the description, since that is what the model sees before loading the skill.
