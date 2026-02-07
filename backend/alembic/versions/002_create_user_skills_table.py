"""create user_skills table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2025-02-07

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a7"
down_revision: str | Sequence[str] | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user_skills",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("description", sa.String(), nullable=False, server_default=""),
        sa.Column("content", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_user_skills_id"), "user_skills", ["id"], unique=False)
    op.create_index(op.f("ix_user_skills_user_id"), "user_skills", ["user_id"], unique=False)
    op.create_unique_constraint(
        "uq_user_skills_user_id_name",
        "user_skills",
        ["user_id", "name"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_user_skills_user_id_name", "user_skills", type_="unique")
    op.drop_index(op.f("ix_user_skills_user_id"), table_name="user_skills")
    op.drop_index(op.f("ix_user_skills_id"), table_name="user_skills")
    op.drop_table("user_skills")
