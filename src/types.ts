export type UserRole = "administrador" | "financeiro" | "tecnico" | "comercial" | "leitura";
export type PessoaTipo = "pf" | "pj";
export type StatusEquipamento = "disponivel" | "locado" | "em_manutencao" | "baixado";
export type TipoPlano = "por_pagina" | "mensalidade" | "franquia";
export type StatusContrato = "rascunho" | "vigente" | "suspenso" | "encerrado";
export type FonteLeitura = "manual" | "snmp" | "csv" | "portal";

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface BootstrapResponse extends TokenResponse {
  tenant_id: number;
  user_id: number;
}

export interface UserMe {
  id: number;
  tenant_id: number;
  name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
}

export interface Tenant {
  id: number;
  name: string;
  document: string | null;
  is_active: boolean;
}

export interface Client {
  id: number;
  tenant_id: number;
  person_type: PessoaTipo;
  name: string;
  document: string;
  email: string | null;
  phone: string | null;
  credit_score: number | null;
  credit_status: string | null;
}

export interface Equipment {
  id: number;
  tenant_id: number;
  client_id: number | null;
  serial_number: string;
  brand: string;
  model: string;
  kind: string;
  status: StatusEquipamento;
  location: string | null;
  last_counter_pb: number;
  last_counter_color: number;
}

export interface Plan {
  id: number;
  tenant_id: number;
  name: string;
  type: TipoPlano;
  monthly_fee: number | null;
  price_pb: number | null;
  price_color: number | null;
  franchise_pb: number | null;
  franchise_color: number | null;
  extra_pb: number | null;
  extra_color: number | null;
  is_active: boolean;
}

export interface Contract {
  id: number;
  tenant_id: number;
  client_id: number;
  plan_id: number;
  number: string;
  start_date: string;
  end_date: string | null;
  status: StatusContrato;
  billing_day: number;
  monthly_value: number | null;
  franchise_pb: number | null;
  franchise_color: number | null;
  price_excess_pb: number | null;
  price_excess_color: number | null;
  notes: string | null;
  equipments?: Array<{ equipment_id: number }>;
}

export interface Reading {
  id: number;
  tenant_id: number;
  contract_id: number;
  equipment_id: number;
  reference_date: string;
  source: FonteLeitura;
  counter_pb_current: number;
  counter_pb_previous: number;
  counter_color_current: number;
  counter_color_previous: number;
  validated: boolean;
  photo_url: string | null;
  notes: string | null;
}

export type StatusTitulo = "aberto" | "parcialmente_pago" | "pago" | "vencido" | "cancelado";
export type StatusBoleto = "gerado" | "enviado" | "registrado" | "pago" | "vencido" | "cancelado" | "rejeitado";
export type StatusRemessa = "criada" | "enviada" | "processada" | "falha";
export type StatusConciliacao = "pendente" | "casado" | "ignorado";
export type RegimeTributario = "simples_nacional" | "lucro_presumido" | "lucro_real" | "mei" | "outro";
export type TipoDocumentoFiscal = "nfe" | "nfse";
export type StatusDocumentoFiscal = "rascunho" | "autorizado" | "cancelado" | "rejeitado";
export type OrigemDocumentoFiscal = "manual" | "receivable" | "contract" | "batch";

export interface AccountsReceivable {
  id: number;
  tenant_id: number;
  contract_id: number | null;
  client_id: number | null;
  issue_date: string;
  due_date: string;
  competence: string;
  description: string;
  original_amount: number;
  paid_amount: number;
  interest_amount: number;
  penalty_amount: number;
  discount_amount: number;
  status: StatusTitulo;
  notes: string | null;
}

export interface AccountsPayable {
  id: number;
  tenant_id: number;
  contract_id: number | null;
  issue_date: string;
  due_date: string;
  description: string;
  category: string;
  supplier_name: string | null;
  original_amount: number;
  paid_amount: number;
  status: StatusTitulo;
  notes: string | null;
}

export interface Boleto {
  id: number;
  tenant_id: number;
  receivable_id: number | null;
  payable_id: number | null;
  bank_code: string;
  nosso_numero: string;
  barcode: string;
  pix_qr_code: string | null;
  due_date: string;
  amount: number;
  status: StatusBoleto;
  issued_at: string;
  sent_at: string | null;
  remittance_id: number | null;
  pdf_url: string | null;
  notes: string | null;
}

export interface Remittance {
  id: number;
  tenant_id: number;
  bank_code: string;
  file_type: string;
  file_name: string;
  file_url: string | null;
  generated_at: string;
  sent_at: string | null;
  status: StatusRemessa;
  total_titles: number;
  total_amount: number;
}

export interface BankReconciliationEntry {
  id: number;
  tenant_id: number;
  statement_date: string;
  description: string;
  reference: string | null;
  amount: number;
  source: string;
  status: StatusConciliacao;
  receivable_id: number | null;
  payable_id: number | null;
  matched_at: string | null;
  notes: string | null;
}

export interface FinanceSummary {
  receivable_open_total: number;
  receivable_overdue_total: number;
  payable_open_total: number;
  payable_overdue_total: number;
  boletos_open: number;
  boletos_paid: number;
  receivables: number;
  payables: number;
}

export interface AgingBucket {
  label: string;
  count: number;
  total: number;
}

export interface AgingReport {
  as_of: string;
  receivable_buckets: AgingBucket[];
  payable_buckets: AgingBucket[];
}

export interface SettlementRequest {
  paid_amount?: number | null;
  payment_date?: string | null;
  notes?: string | null;
}

export interface ReceivableCreate {
  contract_id?: number | null;
  client_id?: number | null;
  issue_date: string;
  due_date: string;
  competence: string;
  description: string;
  original_amount: number;
  notes?: string | null;
}

export interface PayableCreate {
  contract_id?: number | null;
  issue_date: string;
  due_date: string;
  description: string;
  category: string;
  supplier_name?: string | null;
  original_amount: number;
  notes?: string | null;
}

export interface BoletoCreate {
  receivable_id?: number | null;
  payable_id?: number | null;
  bank_code: string;
  due_date: string;
  amount: number;
}

export interface RemittanceCreate {
  bank_code: string;
  file_type: string;
  file_name: string;
  boleto_ids: number[];
}

export interface BankEntryCreate {
  statement_date: string;
  description: string;
  reference?: string | null;
  amount: number;
  source?: string;
  notes?: string | null;
}

export interface BankEntryImportRequest {
  entries: BankEntryCreate[];
  auto_match?: boolean;
}

export interface BillingGenerationRequest {
  competence: string;
  bank_code: string;
  issue_date: string;
  due_date: string;
  description_prefix?: string;
  generate_boleto?: boolean;
}

export interface BillingGenerationItem {
  contract_id: number;
  receivable_id: number;
  boleto_id: number | null;
  amount: number;
  description: string;
}

export interface BillingGenerationResponse {
  competence: string;
  total_amount: number;
  items: BillingGenerationItem[];
}

export interface PortalLoginRequest {
  tenant_key: string;
  client_document: string;
}

export interface PortalTokenResponse {
  access_token: string;
  token_type: string;
  client_id: number;
  tenant_id: number;
  client_name: string;
}

export interface PortalSummary {
  contracts: number;
  equipments: number;
  readings: number;
  boletos_open: number;
  tickets_open: number;
  last_reading_at: string | null;
}

export interface PortalReport {
  client_name: string;
  contracts: number;
  readings: number;
  tickets_open: number;
  boletos_open: number;
  total_due: number;
}

export interface PortalReadingCreate {
  contract_id: number;
  equipment_id: number;
  reference_date: string;
  counter_pb_current: number;
  counter_pb_previous?: number;
  counter_color_current: number;
  counter_color_previous?: number;
  notes?: string | null;
}

export interface PortalTicketCreate {
  subject: string;
  description: string;
  contract_id?: number | null;
  equipment_id?: number | null;
  priority?: "baixa" | "media" | "alta";
}

export interface PortalTicket {
  id: number;
  tenant_id: number;
  client_id: number;
  contract_id: number | null;
  equipment_id: number | null;
  subject: string;
  description: string;
  priority: "baixa" | "media" | "alta";
  status: "aberto" | "em_atendimento" | "resolvido" | "cancelado";
  last_response_at: string | null;
  resolved_at: string | null;
}

export interface FiscalConfig {
  id: number;
  tenant_id: number;
  company_name: string;
  cnpj: string | null;
  inscricao_estadual: string | null;
  inscricao_municipal: string | null;
  regime_tributario: RegimeTributario;
  serie_nfe: number;
  serie_nfse: number;
  nfe_enabled: boolean;
  nfse_enabled: boolean;
  iss_rate: number;
  notes: string | null;
}

export interface FiscalDocument {
  id: number;
  tenant_id: number;
  config_id: number;
  document_type: TipoDocumentoFiscal;
  origin: OrigemDocumentoFiscal;
  receivable_id: number | null;
  contract_id: number | null;
  client_id: number | null;
  number: number;
  series: number;
  access_key: string | null;
  status: StatusDocumentoFiscal;
  issue_date: string;
  competence: string;
  recipient_name: string;
  recipient_document: string | null;
  description: string;
  amount: number;
  tax_base: number | null;
  tax_rate: number | null;
  tax_amount: number | null;
  xml_url: string | null;
  pdf_url: string | null;
  authorization_protocol: string | null;
  authorized_at: string | null;
  cancelled_at: string | null;
  notes: string | null;
}

export interface FiscalSummary {
  total_documents: number;
  draft_documents: number;
  authorized_documents: number;
  cancelled_documents: number;
  total_amount: number;
}

export interface FiscalConfigUpsert {
  company_name: string;
  cnpj: string;
  inscricao_estadual: string;
  inscricao_municipal: string;
  regime_tributario: RegimeTributario;
  serie_nfe: number;
  serie_nfse: number;
  nfe_enabled: boolean;
  nfse_enabled: boolean;
  iss_rate: number;
  notes: string;
}

export interface FiscalDocumentIssueRequest {
  document_type: TipoDocumentoFiscal;
  origin?: OrigemDocumentoFiscal;
  receivable_id?: number | null;
  contract_id?: number | null;
  client_id?: number | null;
  series?: number | null;
  issue_date: string;
  competence: string;
  recipient_name?: string | null;
  recipient_document?: string | null;
  description?: string | null;
  amount?: number | null;
  tax_base?: number | null;
  tax_rate?: number | null;
  tax_amount?: number | null;
  authorize?: boolean;
  notes?: string | null;
}

export interface FiscalDocumentUpdateRequest {
  document_type?: TipoDocumentoFiscal;
  origin?: OrigemDocumentoFiscal;
  series?: number;
  issue_date?: string;
  competence?: string;
  recipient_name?: string;
  recipient_document?: string | null;
  description?: string;
  amount?: number;
  tax_base?: number | null;
  tax_rate?: number | null;
  tax_amount?: number | null;
  notes?: string | null;
}

export interface FiscalBatchIssueRequest {
  document_type?: TipoDocumentoFiscal;
  receivable_ids?: number[];
  authorize?: boolean;
  issue_date: string;
  competence: string;
  series?: number | null;
}

export interface LoginRequest {
  tenant_key: string;
  email: string;
  password: string;
}

export interface BootstrapRequest {
  tenant_name: string;
  tenant_document: string;
  admin_name: string;
  admin_email: string;
  admin_password: string;
}

export interface FinanceSummaryRequest {
  // reserved for future filters
}
