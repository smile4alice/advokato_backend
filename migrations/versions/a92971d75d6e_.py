"""empty message

Revision ID: a92971d75d6e
Revises: e032f2f9aca9
Create Date: 2023-12-02 20:41:01.240525

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a92971d75d6e"
down_revision = "e032f2f9aca9"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user_security",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("token", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("user_security")
    # ### end Alembic commands ###
