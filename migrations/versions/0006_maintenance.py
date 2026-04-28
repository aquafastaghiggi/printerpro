from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0006_maintenance"
down_revision = "0005_notifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "maintenance_tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("equipment_id", sa.Integer(), nullable=True),
        sa.Column("contract_id", sa.Integer(), nullable=True),
        sa.Column("client_id", sa.Integer(), nullable=True),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_key", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("scheduled_for", sa.Date(), nullable=True),
        sa.Column("technician_name", sa.String(length=120), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipments.id"]),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"]),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "source_key", name="uq_maintenance_tenant_source_key"),
    )
    op.create_index(op.f("ix_maintenance_tasks_client_id"), "maintenance_tasks", ["client_id"], unique=False)
    op.create_index(op.f("ix_maintenance_tasks_contract_id"), "maintenance_tasks", ["contract_id"], unique=False)
    op.create_index(op.f("ix_maintenance_tasks_due_date"), "maintenance_tasks", ["due_date"], unique=False)
    op.create_index(op.f("ix_maintenance_tasks_equipment_id"), "maintenance_tasks", ["equipment_id"], unique=False)
    op.create_index(op.f("ix_maintenance_tasks_source_key"), "maintenance_tasks", ["source_key"], unique=False)
    op.create_index(op.f("ix_maintenance_tasks_source_type"), "maintenance_tasks", ["source_type"], unique=False)
    op.create_index(op.f("ix_maintenance_tasks_status"), "maintenance_tasks", ["status"], unique=False)
    op.create_index(op.f("ix_maintenance_tasks_tenant_id"), "maintenance_tasks", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_maintenance_tasks_tenant_id"), table_name="maintenance_tasks")
    op.drop_index(op.f("ix_maintenance_tasks_status"), table_name="maintenance_tasks")
    op.drop_index(op.f("ix_maintenance_tasks_source_type"), table_name="maintenance_tasks")
    op.drop_index(op.f("ix_maintenance_tasks_source_key"), table_name="maintenance_tasks")
    op.drop_index(op.f("ix_maintenance_tasks_equipment_id"), table_name="maintenance_tasks")
    op.drop_index(op.f("ix_maintenance_tasks_due_date"), table_name="maintenance_tasks")
    op.drop_index(op.f("ix_maintenance_tasks_contract_id"), table_name="maintenance_tasks")
    op.drop_index(op.f("ix_maintenance_tasks_client_id"), table_name="maintenance_tasks")
    op.drop_table("maintenance_tasks")
