from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("document", sa.String(length=20), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document"),
    )
    op.create_index(op.f("ix_tenants_document"), "tenants", ["document"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("administrador", "financeiro", "tecnico", "comercial", "leitura", name="userrole", native_enum=False),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "email", name="uq_user_tenant_email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)
    op.create_index(op.f("ix_users_tenant_id"), "users", ["tenant_id"], unique=False)

    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column(
            "person_type",
            sa.Enum("pf", "pj", name="pessoatipo", native_enum=False),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("document", sa.String(length=20), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("credit_score", sa.Integer(), nullable=True),
        sa.Column("credit_status", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_clients_document"), "clients", ["document"], unique=False)
    op.create_index(op.f("ix_clients_tenant_id"), "clients", ["tenant_id"], unique=False)

    op.create_table(
        "equipments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=True),
        sa.Column("serial_number", sa.String(length=80), nullable=False),
        sa.Column("brand", sa.String(length=80), nullable=False),
        sa.Column("model", sa.String(length=120), nullable=False),
        sa.Column("kind", sa.String(length=60), nullable=False),
        sa.Column(
            "status",
            sa.Enum("disponivel", "locado", "em_manutencao", "baixado", name="statusequipamento", native_enum=False),
            nullable=False,
        ),
        sa.Column("location", sa.String(length=180), nullable=True),
        sa.Column("last_counter_pb", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_counter_color", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_equipments_client_id"), "equipments", ["client_id"], unique=False)
    op.create_index(op.f("ix_equipments_serial_number"), "equipments", ["serial_number"], unique=False)
    op.create_index(op.f("ix_equipments_tenant_id"), "equipments", ["tenant_id"], unique=False)

    op.create_table(
        "plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column(
            "type",
            sa.Enum("por_pagina", "mensalidade", "franquia", name="tipoplano", native_enum=False),
            nullable=False,
        ),
        sa.Column("monthly_fee", sa.Numeric(12, 2), nullable=True),
        sa.Column("price_pb", sa.Numeric(12, 4), nullable=True),
        sa.Column("price_color", sa.Numeric(12, 4), nullable=True),
        sa.Column("franchise_pb", sa.Integer(), nullable=True),
        sa.Column("franchise_color", sa.Integer(), nullable=True),
        sa.Column("extra_pb", sa.Numeric(12, 4), nullable=True),
        sa.Column("extra_color", sa.Numeric(12, 4), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_plans_tenant_id"), "plans", ["tenant_id"], unique=False)

    op.create_table(
        "contracts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("number", sa.String(length=30), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("rascunho", "vigente", "suspenso", "encerrado", name="statuscontrato", native_enum=False),
            nullable=False,
        ),
        sa.Column("billing_day", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("monthly_value", sa.Numeric(12, 2), nullable=True),
        sa.Column("franchise_pb", sa.Integer(), nullable=True),
        sa.Column("franchise_color", sa.Integer(), nullable=True),
        sa.Column("price_excess_pb", sa.Numeric(12, 4), nullable=True),
        sa.Column("price_excess_color", sa.Numeric(12, 4), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.ForeignKeyConstraint(["plan_id"], ["plans.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "number", name="uq_contract_tenant_number"),
    )
    op.create_index(op.f("ix_contracts_client_id"), "contracts", ["client_id"], unique=False)
    op.create_index(op.f("ix_contracts_number"), "contracts", ["number"], unique=False)
    op.create_index(op.f("ix_contracts_plan_id"), "contracts", ["plan_id"], unique=False)
    op.create_index(op.f("ix_contracts_tenant_id"), "contracts", ["tenant_id"], unique=False)

    op.create_table(
        "contract_equipments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("contract_id", sa.Integer(), nullable=False),
        sa.Column("equipment_id", sa.Integer(), nullable=False),
        sa.Column("installed_at", sa.Date(), nullable=True),
        sa.Column("removed_at", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"]),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipments.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_contract_equipments_contract_id"), "contract_equipments", ["contract_id"], unique=False)
    op.create_index(op.f("ix_contract_equipments_equipment_id"), "contract_equipments", ["equipment_id"], unique=False)

    op.create_table(
        "readings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("contract_id", sa.Integer(), nullable=False),
        sa.Column("equipment_id", sa.Integer(), nullable=False),
        sa.Column("reference_date", sa.Date(), nullable=False),
        sa.Column(
            "source",
            sa.Enum("manual", "snmp", "csv", "portal", name="fonteleitura", native_enum=False),
            nullable=False,
        ),
        sa.Column("counter_pb_current", sa.Integer(), nullable=False),
        sa.Column("counter_pb_previous", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("counter_color_current", sa.Integer(), nullable=False),
        sa.Column("counter_color_previous", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("validated", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("photo_url", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"]),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipments.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_readings_contract_id"), "readings", ["contract_id"], unique=False)
    op.create_index(op.f("ix_readings_equipment_id"), "readings", ["equipment_id"], unique=False)
    op.create_index(op.f("ix_readings_reference_date"), "readings", ["reference_date"], unique=False)
    op.create_index(op.f("ix_readings_tenant_id"), "readings", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_readings_tenant_id"), table_name="readings")
    op.drop_index(op.f("ix_readings_reference_date"), table_name="readings")
    op.drop_index(op.f("ix_readings_equipment_id"), table_name="readings")
    op.drop_index(op.f("ix_readings_contract_id"), table_name="readings")
    op.drop_table("readings")

    op.drop_index(op.f("ix_contract_equipments_equipment_id"), table_name="contract_equipments")
    op.drop_index(op.f("ix_contract_equipments_contract_id"), table_name="contract_equipments")
    op.drop_table("contract_equipments")

    op.drop_index(op.f("ix_contracts_tenant_id"), table_name="contracts")
    op.drop_index(op.f("ix_contracts_plan_id"), table_name="contracts")
    op.drop_index(op.f("ix_contracts_number"), table_name="contracts")
    op.drop_index(op.f("ix_contracts_client_id"), table_name="contracts")
    op.drop_table("contracts")

    op.drop_index(op.f("ix_plans_tenant_id"), table_name="plans")
    op.drop_table("plans")

    op.drop_index(op.f("ix_equipments_tenant_id"), table_name="equipments")
    op.drop_index(op.f("ix_equipments_serial_number"), table_name="equipments")
    op.drop_index(op.f("ix_equipments_client_id"), table_name="equipments")
    op.drop_table("equipments")

    op.drop_index(op.f("ix_clients_tenant_id"), table_name="clients")
    op.drop_index(op.f("ix_clients_document"), table_name="clients")
    op.drop_table("clients")

    op.drop_index(op.f("ix_users_tenant_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    op.drop_index(op.f("ix_tenants_document"), table_name="tenants")
    op.drop_table("tenants")

