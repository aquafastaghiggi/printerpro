from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0002_financeiro"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accounts_receivable",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("contract_id", sa.Integer(), nullable=True),
        sa.Column("client_id", sa.Integer(), nullable=True),
        sa.Column("issue_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("competence", sa.String(length=7), nullable=False),
        sa.Column("description", sa.String(length=180), nullable=False),
        sa.Column("original_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("paid_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("interest_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("penalty_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("discount_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column(
            "status",
            sa.Enum("aberto", "parcialmente_pago", "pago", "vencido", "cancelado", name="statustitulo", native_enum=False),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_accounts_receivable_client_id"), "accounts_receivable", ["client_id"], unique=False)
    op.create_index(op.f("ix_accounts_receivable_competence"), "accounts_receivable", ["competence"], unique=False)
    op.create_index(op.f("ix_accounts_receivable_contract_id"), "accounts_receivable", ["contract_id"], unique=False)
    op.create_index(op.f("ix_accounts_receivable_due_date"), "accounts_receivable", ["due_date"], unique=False)
    op.create_index(op.f("ix_accounts_receivable_tenant_id"), "accounts_receivable", ["tenant_id"], unique=False)

    op.create_table(
        "accounts_payable",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("contract_id", sa.Integer(), nullable=True),
        sa.Column("issue_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("description", sa.String(length=180), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("supplier_name", sa.String(length=180), nullable=True),
        sa.Column("original_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("paid_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column(
            "status",
            sa.Enum("aberto", "parcialmente_pago", "pago", "vencido", "cancelado", name="statustitulo", native_enum=False),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_accounts_payable_contract_id"), "accounts_payable", ["contract_id"], unique=False)
    op.create_index(op.f("ix_accounts_payable_due_date"), "accounts_payable", ["due_date"], unique=False)
    op.create_index(op.f("ix_accounts_payable_tenant_id"), "accounts_payable", ["tenant_id"], unique=False)

    op.create_table(
        "remessas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("bank_code", sa.String(length=10), nullable=False),
        sa.Column("file_type", sa.String(length=20), nullable=False),
        sa.Column("file_name", sa.String(length=180), nullable=False),
        sa.Column("file_url", sa.String(length=255), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            sa.Enum("criada", "enviada", "processada", "falha", name="statusremessa", native_enum=False),
            nullable=False,
        ),
        sa.Column("total_titles", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_remessas_tenant_id"), "remessas", ["tenant_id"], unique=False)

    op.create_table(
        "boletos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("receivable_id", sa.Integer(), nullable=True),
        sa.Column("payable_id", sa.Integer(), nullable=True),
        sa.Column("bank_code", sa.String(length=10), nullable=False),
        sa.Column("nosso_numero", sa.String(length=40), nullable=True),
        sa.Column("barcode", sa.String(length=120), nullable=True),
        sa.Column("pix_qr_code", sa.Text(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "status",
            sa.Enum("gerado", "enviado", "registrado", "pago", "vencido", "cancelado", "rejeitado", name="statusboleto", native_enum=False),
            nullable=False,
        ),
        sa.Column("issued_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("remittance_id", sa.Integer(), nullable=True),
        sa.Column("pdf_url", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["payable_id"], ["accounts_payable.id"]),
        sa.ForeignKeyConstraint(["receivable_id"], ["accounts_receivable.id"]),
        sa.ForeignKeyConstraint(["remittance_id"], ["remessas.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_boletos_due_date"), "boletos", ["due_date"], unique=False)
    op.create_index(op.f("ix_boletos_nosso_numero"), "boletos", ["nosso_numero"], unique=False)
    op.create_index(op.f("ix_boletos_payable_id"), "boletos", ["payable_id"], unique=False)
    op.create_index(op.f("ix_boletos_receivable_id"), "boletos", ["receivable_id"], unique=False)
    op.create_index(op.f("ix_boletos_remittance_id"), "boletos", ["remittance_id"], unique=False)
    op.create_index(op.f("ix_boletos_tenant_id"), "boletos", ["tenant_id"], unique=False)

    op.create_table(
        "bank_reconciliation_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("statement_date", sa.Date(), nullable=False),
        sa.Column("description", sa.String(length=180), nullable=False),
        sa.Column("reference", sa.String(length=80), nullable=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("source", sa.String(length=40), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pendente", "casado", "ignorado", name="statusconciliacao", native_enum=False),
            nullable=False,
        ),
        sa.Column("receivable_id", sa.Integer(), nullable=True),
        sa.Column("payable_id", sa.Integer(), nullable=True),
        sa.Column("matched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["payable_id"], ["accounts_payable.id"]),
        sa.ForeignKeyConstraint(["receivable_id"], ["accounts_receivable.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_bank_reconciliation_entries_payable_id"), "bank_reconciliation_entries", ["payable_id"], unique=False)
    op.create_index(op.f("ix_bank_reconciliation_entries_receivable_id"), "bank_reconciliation_entries", ["receivable_id"], unique=False)
    op.create_index(op.f("ix_bank_reconciliation_entries_statement_date"), "bank_reconciliation_entries", ["statement_date"], unique=False)
    op.create_index(op.f("ix_bank_reconciliation_entries_tenant_id"), "bank_reconciliation_entries", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_bank_reconciliation_entries_tenant_id"), table_name="bank_reconciliation_entries")
    op.drop_index(op.f("ix_bank_reconciliation_entries_statement_date"), table_name="bank_reconciliation_entries")
    op.drop_index(op.f("ix_bank_reconciliation_entries_receivable_id"), table_name="bank_reconciliation_entries")
    op.drop_index(op.f("ix_bank_reconciliation_entries_payable_id"), table_name="bank_reconciliation_entries")
    op.drop_table("bank_reconciliation_entries")

    op.drop_index(op.f("ix_boletos_tenant_id"), table_name="boletos")
    op.drop_index(op.f("ix_boletos_remittance_id"), table_name="boletos")
    op.drop_index(op.f("ix_boletos_receivable_id"), table_name="boletos")
    op.drop_index(op.f("ix_boletos_payable_id"), table_name="boletos")
    op.drop_index(op.f("ix_boletos_nosso_numero"), table_name="boletos")
    op.drop_index(op.f("ix_boletos_due_date"), table_name="boletos")
    op.drop_table("boletos")

    op.drop_index(op.f("ix_remessas_tenant_id"), table_name="remessas")
    op.drop_table("remessas")

    op.drop_index(op.f("ix_accounts_payable_tenant_id"), table_name="accounts_payable")
    op.drop_index(op.f("ix_accounts_payable_due_date"), table_name="accounts_payable")
    op.drop_index(op.f("ix_accounts_payable_contract_id"), table_name="accounts_payable")
    op.drop_table("accounts_payable")

    op.drop_index(op.f("ix_accounts_receivable_tenant_id"), table_name="accounts_receivable")
    op.drop_index(op.f("ix_accounts_receivable_due_date"), table_name="accounts_receivable")
    op.drop_index(op.f("ix_accounts_receivable_contract_id"), table_name="accounts_receivable")
    op.drop_index(op.f("ix_accounts_receivable_competence"), table_name="accounts_receivable")
    op.drop_index(op.f("ix_accounts_receivable_client_id"), table_name="accounts_receivable")
    op.drop_table("accounts_receivable")
