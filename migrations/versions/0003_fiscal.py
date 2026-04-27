from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0003_fiscal"
down_revision = "0002_financeiro"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "fiscal_configs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("company_name", sa.String(length=180), nullable=False),
        sa.Column("cnpj", sa.String(length=20), nullable=True),
        sa.Column("inscricao_estadual", sa.String(length=30), nullable=True),
        sa.Column("inscricao_municipal", sa.String(length=30), nullable=True),
        sa.Column(
            "regime_tributario",
            sa.Enum("simples_nacional", "lucro_presumido", "lucro_real", "mei", "outro", name="regimetributario", native_enum=False),
            nullable=False,
        ),
        sa.Column("serie_nfe", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("serie_nfse", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("nfe_enabled", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("nfse_enabled", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("iss_rate", sa.Numeric(5, 2), nullable=False, server_default="2.00"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", name="uq_fiscal_configs_tenant"),
    )
    op.create_index(op.f("ix_fiscal_configs_tenant_id"), "fiscal_configs", ["tenant_id"], unique=False)

    op.create_table(
        "fiscal_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("config_id", sa.Integer(), nullable=False),
        sa.Column(
            "document_type",
            sa.Enum("nfe", "nfse", name="tipodocumentofiscal", native_enum=False),
            nullable=False,
        ),
        sa.Column(
            "origin",
            sa.Enum("manual", "receivable", "contract", "batch", name="origemdocumentofiscal", native_enum=False),
            nullable=False,
        ),
        sa.Column("receivable_id", sa.Integer(), nullable=True),
        sa.Column("contract_id", sa.Integer(), nullable=True),
        sa.Column("client_id", sa.Integer(), nullable=True),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("series", sa.Integer(), nullable=False),
        sa.Column("access_key", sa.String(length=80), nullable=True),
        sa.Column(
            "status",
            sa.Enum("rascunho", "autorizado", "cancelado", "rejeitado", name="statusdocumentofiscal", native_enum=False),
            nullable=False,
        ),
        sa.Column("issue_date", sa.Date(), nullable=False),
        sa.Column("competence", sa.String(length=7), nullable=False),
        sa.Column("recipient_name", sa.String(length=180), nullable=False),
        sa.Column("recipient_document", sa.String(length=20), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("tax_base", sa.Numeric(12, 2), nullable=True),
        sa.Column("tax_rate", sa.Numeric(5, 2), nullable=True),
        sa.Column("tax_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("xml_url", sa.String(length=255), nullable=True),
        sa.Column("pdf_url", sa.String(length=255), nullable=True),
        sa.Column("authorization_protocol", sa.String(length=80), nullable=True),
        sa.Column("authorized_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.ForeignKeyConstraint(["config_id"], ["fiscal_configs.id"]),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"]),
        sa.ForeignKeyConstraint(["receivable_id"], ["accounts_receivable.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "document_type", "series", "number", name="uq_fiscal_documents_number"),
    )
    op.create_index(op.f("ix_fiscal_documents_access_key"), "fiscal_documents", ["access_key"], unique=True)
    op.create_index(op.f("ix_fiscal_documents_client_id"), "fiscal_documents", ["client_id"], unique=False)
    op.create_index(op.f("ix_fiscal_documents_competence"), "fiscal_documents", ["competence"], unique=False)
    op.create_index(op.f("ix_fiscal_documents_config_id"), "fiscal_documents", ["config_id"], unique=False)
    op.create_index(op.f("ix_fiscal_documents_contract_id"), "fiscal_documents", ["contract_id"], unique=False)
    op.create_index(op.f("ix_fiscal_documents_document_type"), "fiscal_documents", ["document_type"], unique=False)
    op.create_index(op.f("ix_fiscal_documents_issue_date"), "fiscal_documents", ["issue_date"], unique=False)
    op.create_index(op.f("ix_fiscal_documents_receivable_id"), "fiscal_documents", ["receivable_id"], unique=False)
    op.create_index(op.f("ix_fiscal_documents_status"), "fiscal_documents", ["status"], unique=False)
    op.create_index(op.f("ix_fiscal_documents_tenant_id"), "fiscal_documents", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_fiscal_documents_tenant_id"), table_name="fiscal_documents")
    op.drop_index(op.f("ix_fiscal_documents_status"), table_name="fiscal_documents")
    op.drop_index(op.f("ix_fiscal_documents_receivable_id"), table_name="fiscal_documents")
    op.drop_index(op.f("ix_fiscal_documents_issue_date"), table_name="fiscal_documents")
    op.drop_index(op.f("ix_fiscal_documents_document_type"), table_name="fiscal_documents")
    op.drop_index(op.f("ix_fiscal_documents_contract_id"), table_name="fiscal_documents")
    op.drop_index(op.f("ix_fiscal_documents_config_id"), table_name="fiscal_documents")
    op.drop_index(op.f("ix_fiscal_documents_competence"), table_name="fiscal_documents")
    op.drop_index(op.f("ix_fiscal_documents_client_id"), table_name="fiscal_documents")
    op.drop_index(op.f("ix_fiscal_documents_access_key"), table_name="fiscal_documents")
    op.drop_table("fiscal_documents")

    op.drop_index(op.f("ix_fiscal_configs_tenant_id"), table_name="fiscal_configs")
    op.drop_table("fiscal_configs")
