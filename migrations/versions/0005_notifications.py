from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0005_notifications"
down_revision = "0004_portal"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "operational_notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_key", sa.String(length=120), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("detail", sa.Text(), nullable=False),
        sa.Column("suggested_action", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "source_key", name="uq_notification_tenant_source_key"),
    )
    op.create_index(op.f("ix_operational_notifications_is_read"), "operational_notifications", ["is_read"], unique=False)
    op.create_index(op.f("ix_operational_notifications_severity"), "operational_notifications", ["severity"], unique=False)
    op.create_index(op.f("ix_operational_notifications_source_key"), "operational_notifications", ["source_key"], unique=False)
    op.create_index(op.f("ix_operational_notifications_source_type"), "operational_notifications", ["source_type"], unique=False)
    op.create_index(op.f("ix_operational_notifications_tenant_id"), "operational_notifications", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_operational_notifications_tenant_id"), table_name="operational_notifications")
    op.drop_index(op.f("ix_operational_notifications_source_type"), table_name="operational_notifications")
    op.drop_index(op.f("ix_operational_notifications_source_key"), table_name="operational_notifications")
    op.drop_index(op.f("ix_operational_notifications_severity"), table_name="operational_notifications")
    op.drop_index(op.f("ix_operational_notifications_is_read"), table_name="operational_notifications")
    op.drop_table("operational_notifications")
