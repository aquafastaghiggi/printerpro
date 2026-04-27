from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0004_portal"
down_revision = "0003_fiscal"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "portal_tickets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("contract_id", sa.Integer(), nullable=True),
        sa.Column("equipment_id", sa.Integer(), nullable=True),
        sa.Column("subject", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "priority",
            sa.Enum("baixa", "media", "alta", name="prioridadechamado", native_enum=False),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("aberto", "em_atendimento", "resolvido", "cancelado", name="statuschamado", native_enum=False),
            nullable=False,
        ),
        sa.Column("last_response_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"]),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipments.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_portal_tickets_client_id"), "portal_tickets", ["client_id"], unique=False)
    op.create_index(op.f("ix_portal_tickets_contract_id"), "portal_tickets", ["contract_id"], unique=False)
    op.create_index(op.f("ix_portal_tickets_equipment_id"), "portal_tickets", ["equipment_id"], unique=False)
    op.create_index(op.f("ix_portal_tickets_tenant_id"), "portal_tickets", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_portal_tickets_tenant_id"), table_name="portal_tickets")
    op.drop_index(op.f("ix_portal_tickets_equipment_id"), table_name="portal_tickets")
    op.drop_index(op.f("ix_portal_tickets_contract_id"), table_name="portal_tickets")
    op.drop_index(op.f("ix_portal_tickets_client_id"), table_name="portal_tickets")
    op.drop_table("portal_tickets")
