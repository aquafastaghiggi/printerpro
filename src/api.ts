import type {
  AgingReport,
  BankEntryImportRequest,
  BankReconciliationEntry,
  BootstrapRequest,
  BootstrapResponse,
  Client,
  Contract,
  AccountsPayable,
  AccountsReceivable,
  Boleto,
  BoletoCreate,
  Equipment,
  FinanceSummary,
  BillingGenerationRequest,
  BillingGenerationResponse,
  FiscalBatchIssueRequest,
  FiscalConfig,
  FiscalConfigUpsert,
  FiscalDocument,
  FiscalDocumentIssueRequest,
  FiscalDocumentUpdateRequest,
  FiscalSummary,
  DashboardOverview,
  MaintenanceSyncResponse,
  MaintenanceDispatchResponse,
  MaintenanceTask,
  MaintenanceTaskCreate,
  MaintenanceTaskUpdate,
  NotificationDispatchResponse,
  NotificationSyncResponse,
  OperationalNotification,
  PortalLoginRequest,
  PortalReadingCreate,
  PortalReport,
  PortalSummary,
  PortalTicket,
  PortalTicketCreate,
  PortalTokenResponse,
  LoginRequest,
  Plan,
  Reading,
  Remittance,
  RemittanceCreate,
  Tenant,
  TokenResponse,
  SettlementRequest,
  UserMe,
} from "./types";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000/api/v1";
const TOKEN_KEY = "printmanager.token";
const PORTAL_TOKEN_KEY = "printmanager.portal.token";

export function getStoredToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function storeToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export function getStoredPortalToken() {
  return localStorage.getItem(PORTAL_TOKEN_KEY);
}

export function storePortalToken(token: string) {
  localStorage.setItem(PORTAL_TOKEN_KEY, token);
}

export function clearPortalToken() {
  localStorage.removeItem(PORTAL_TOKEN_KEY);
}

async function request<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");

  if (options.body && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Erro HTTP ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export const api = {
  login(payload: LoginRequest) {
    return request<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  portalLogin(payload: PortalLoginRequest) {
    return request<PortalTokenResponse>("/portal/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  bootstrap(payload: BootstrapRequest) {
    return request<BootstrapResponse>("/auth/setup", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  me(token: string) {
    return request<UserMe>("/auth/me", {}, token);
  },
  listTenants(token: string) {
    return request<Tenant[]>("/tenants", {}, token);
  },
  createTenant(token: string, payload: { name: string; document: string | null }) {
    return request<Tenant>("/tenants", { method: "POST", body: JSON.stringify(payload) }, token);
  },
  updateTenant(token: string, id: number, payload: { name?: string; document?: string | null; is_active?: boolean }) {
    return request<Tenant>(`/tenants/${id}`, { method: "PUT", body: JSON.stringify(payload) }, token);
  },
  deleteTenant(token: string, id: number) {
    return request<{ detail: string }>(`/tenants/${id}`, { method: "DELETE" }, token);
  },
  listClients(token: string) {
    return request<Client[]>("/clientes", {}, token);
  },
  createClient(token: string, payload: Record<string, unknown>) {
    return request<Client>("/clientes", { method: "POST", body: JSON.stringify(payload) }, token);
  },
  updateClient(token: string, id: number, payload: Record<string, unknown>) {
    return request<Client>(`/clientes/${id}`, { method: "PUT", body: JSON.stringify(payload) }, token);
  },
  deleteClient(token: string, id: number) {
    return request<{ detail: string }>(`/clientes/${id}`, { method: "DELETE" }, token);
  },
  listEquipment(token: string) {
    return request<Equipment[]>("/equipamentos", {}, token);
  },
  createEquipment(token: string, payload: Record<string, unknown>) {
    return request<Equipment>("/equipamentos", { method: "POST", body: JSON.stringify(payload) }, token);
  },
  updateEquipment(token: string, id: number, payload: Record<string, unknown>) {
    return request<Equipment>(`/equipamentos/${id}`, { method: "PUT", body: JSON.stringify(payload) }, token);
  },
  deleteEquipment(token: string, id: number) {
    return request<{ detail: string }>(`/equipamentos/${id}`, { method: "DELETE" }, token);
  },
  listPlans(token: string) {
    return request<Plan[]>("/planos", {}, token);
  },
  createPlan(token: string, payload: Record<string, unknown>) {
    return request<Plan>("/planos", { method: "POST", body: JSON.stringify(payload) }, token);
  },
  updatePlan(token: string, id: number, payload: Record<string, unknown>) {
    return request<Plan>(`/planos/${id}`, { method: "PUT", body: JSON.stringify(payload) }, token);
  },
  deletePlan(token: string, id: number) {
    return request<{ detail: string }>(`/planos/${id}`, { method: "DELETE" }, token);
  },
  listContracts(token: string) {
    return request<Contract[]>("/contratos", {}, token);
  },
  createContract(token: string, payload: Record<string, unknown>) {
    return request<Contract>("/contratos", { method: "POST", body: JSON.stringify(payload) }, token);
  },
  updateContract(token: string, id: number, payload: Record<string, unknown>) {
    return request<Contract>(`/contratos/${id}`, { method: "PUT", body: JSON.stringify(payload) }, token);
  },
  duplicateContract(token: string, id: number) {
    return request<Contract>(`/contratos/${id}/duplicar`, { method: "POST" }, token);
  },
  closeContract(token: string, id: number) {
    return request<Contract>(`/contratos/${id}/encerrar`, { method: "POST" }, token);
  },
  deleteContract(token: string, id: number) {
    return request<{ detail: string }>(`/contratos/${id}`, { method: "DELETE" }, token);
  },
  listReadings(token: string) {
    return request<Reading[]>("/leituras", {}, token);
  },
  createReading(token: string, payload: Record<string, unknown>) {
    return request<Reading>("/leituras", { method: "POST", body: JSON.stringify(payload) }, token);
  },
  updateReading(token: string, id: number, payload: Record<string, unknown>) {
    return request<Reading>(`/leituras/${id}`, { method: "PUT", body: JSON.stringify(payload) }, token);
  },
  deleteReading(token: string, id: number) {
    return request<{ detail: string }>(`/leituras/${id}`, { method: "DELETE" }, token);
  },
  financeSummary(token: string) {
    return request<FinanceSummary>("/financeiro/dashboard", {}, token);
  },
  listReceivables(token: string) {
    return request<AccountsReceivable[]>("/financeiro/contas-receber", {}, token);
  },
  createReceivable(token: string, payload: Record<string, unknown>) {
    return request<AccountsReceivable>("/financeiro/contas-receber", { method: "POST", body: JSON.stringify(payload) }, token);
  },
  updateReceivable(token: string, id: number, payload: Record<string, unknown>) {
    return request<AccountsReceivable>(`/financeiro/contas-receber/${id}`, { method: "PUT", body: JSON.stringify(payload) }, token);
  },
  settleReceivable(token: string, id: number, payload: SettlementRequest) {
    return request<AccountsReceivable>(`/financeiro/contas-receber/${id}/baixa`, { method: "POST", body: JSON.stringify(payload) }, token);
  },
  deleteReceivable(token: string, id: number) {
    return request<{ detail: string }>(`/financeiro/contas-receber/${id}`, { method: "DELETE" }, token);
  },
  listPayables(token: string) {
    return request<AccountsPayable[]>("/financeiro/contas-pagar", {}, token);
  },
  createPayable(token: string, payload: Record<string, unknown>) {
    return request<AccountsPayable>("/financeiro/contas-pagar", { method: "POST", body: JSON.stringify(payload) }, token);
  },
  updatePayable(token: string, id: number, payload: Record<string, unknown>) {
    return request<AccountsPayable>(`/financeiro/contas-pagar/${id}`, { method: "PUT", body: JSON.stringify(payload) }, token);
  },
  settlePayable(token: string, id: number, payload: SettlementRequest) {
    return request<AccountsPayable>(`/financeiro/contas-pagar/${id}/baixa`, { method: "POST", body: JSON.stringify(payload) }, token);
  },
  deletePayable(token: string, id: number) {
    return request<{ detail: string }>(`/financeiro/contas-pagar/${id}`, { method: "DELETE" }, token);
  },
  listBoletos(token: string) {
    return request<Boleto[]>("/financeiro/boletos", {}, token);
  },
  createBoleto(token: string, payload: BoletoCreate) {
    return request<Boleto>("/financeiro/boletos", { method: "POST", body: JSON.stringify(payload) }, token);
  },
  sendBoleto(token: string, id: number) {
    return request<Boleto>(`/financeiro/boletos/${id}/enviar`, { method: "POST" }, token);
  },
  settleBoleto(token: string, id: number) {
    return request<Boleto>(`/financeiro/boletos/${id}/baixar`, { method: "POST" }, token);
  },
  deleteBoleto(token: string, id: number) {
    return request<{ detail: string }>(`/financeiro/boletos/${id}`, { method: "DELETE" }, token);
  },
  listRemittances(token: string) {
    return request<Remittance[]>("/financeiro/remessas", {}, token);
  },
  createRemittance(token: string, payload: RemittanceCreate) {
    return request<Remittance>("/financeiro/remessas", { method: "POST", body: JSON.stringify(payload) }, token);
  },
  importBankEntries(token: string, payload: BankEntryImportRequest) {
    return request<BankReconciliationEntry[]>("/financeiro/conciliacao/importar", { method: "POST", body: JSON.stringify(payload) }, token);
  },
  listReconciliation(token: string) {
    return request<BankReconciliationEntry[]>("/financeiro/conciliacao", {}, token);
  },
  agingReport(token: string) {
    return request<AgingReport>("/financeiro/inadimplencia/aging", {}, token);
  },
  generateBilling(token: string, payload: BillingGenerationRequest) {
    return request<BillingGenerationResponse>("/financeiro/faturamento/gerar", { method: "POST", body: JSON.stringify(payload) }, token);
  },
  getFiscalConfig(token: string) {
    return request<FiscalConfig>("/fiscal/configuracao", {}, token);
  },
  updateFiscalConfig(token: string, payload: FiscalConfigUpsert) {
    return request<FiscalConfig>("/fiscal/configuracao", { method: "PUT", body: JSON.stringify(payload) }, token);
  },
  fiscalSummary(token: string) {
    return request<FiscalSummary>("/fiscal/dashboard", {}, token);
  },
  dashboardOverview(token: string) {
    return request<DashboardOverview>("/dashboard/executivo", {}, token);
  },
  listMaintenanceTasks(token: string) {
    return request<MaintenanceTask[]>("/manutencao/fila", {}, token);
  },
  createMaintenanceTask(token: string, payload: MaintenanceTaskCreate) {
    return request<MaintenanceTask>("/manutencao/fila", { method: "POST", body: JSON.stringify(payload) }, token);
  },
  syncMaintenanceTasks(token: string) {
    return request<MaintenanceSyncResponse>("/manutencao/fila/sincronizar", { method: "POST" }, token);
  },
  updateMaintenanceTask(token: string, id: number, payload: MaintenanceTaskUpdate) {
    return request<MaintenanceTask>(`/manutencao/fila/${id}`, { method: "PATCH", body: JSON.stringify(payload) }, token);
  },
  startMaintenanceTask(token: string, id: number) {
    return request<MaintenanceTask>(`/manutencao/fila/${id}/iniciar`, { method: "POST" }, token);
  },
  completeMaintenanceTask(token: string, id: number) {
    return request<MaintenanceTask>(`/manutencao/fila/${id}/concluir`, { method: "POST" }, token);
  },
  dispatchMaintenanceTask(token: string, id: number) {
    return request<MaintenanceDispatchResponse>(`/manutencao/fila/${id}/enviar`, { method: "POST" }, token);
  },
  listNotifications(token: string) {
    return request<OperationalNotification[]>("/notificacoes", {}, token);
  },
  syncNotifications(token: string) {
    return request<NotificationSyncResponse>("/notificacoes/sincronizar", { method: "POST" }, token);
  },
  markNotificationRead(token: string, id: number) {
    return request<OperationalNotification>(`/notificacoes/${id}/lida`, { method: "POST" }, token);
  },
  dispatchNotifications(token: string) {
    return request<NotificationDispatchResponse>("/notificacoes/disparar", { method: "POST" }, token);
  },
  listFiscalDocuments(token: string) {
    return request<FiscalDocument[]>("/fiscal/documentos", {}, token);
  },
  createFiscalDocument(token: string, payload: FiscalDocumentIssueRequest) {
    return request<FiscalDocument>("/fiscal/documentos", { method: "POST", body: JSON.stringify(payload) }, token);
  },
  updateFiscalDocument(token: string, id: number, payload: FiscalDocumentUpdateRequest) {
    return request<FiscalDocument>(`/fiscal/documentos/${id}`, { method: "PUT", body: JSON.stringify(payload) }, token);
  },
  authorizeFiscalDocument(token: string, id: number) {
    return request<FiscalDocument>(`/fiscal/documentos/${id}/autorizar`, { method: "POST" }, token);
  },
  cancelFiscalDocument(token: string, id: number) {
    return request<FiscalDocument>(`/fiscal/documentos/${id}/cancelar`, { method: "POST" }, token);
  },
  deleteFiscalDocument(token: string, id: number) {
    return request<{ detail: string }>(`/fiscal/documentos/${id}`, { method: "DELETE" }, token);
  },
  batchIssueFiscalDocuments(token: string, payload: FiscalBatchIssueRequest) {
    return request<FiscalDocument[]>("/fiscal/documentos/gerar-recebiveis", { method: "POST", body: JSON.stringify(payload) }, token);
  },
  portalMe(token: string) {
    return request<Client>("/portal/me", {}, token);
  },
  portalSummary(token: string) {
    return request<PortalSummary>("/portal/dashboard", {}, token);
  },
  portalReport(token: string) {
    return request<PortalReport>("/portal/relatorio", {}, token);
  },
  portalContracts(token: string) {
    return request<Contract[]>("/portal/contratos", {}, token);
  },
  portalEquipments(token: string) {
    return request<Equipment[]>("/portal/equipamentos", {}, token);
  },
  portalReadings(token: string) {
    return request<Reading[]>("/portal/leituras", {}, token);
  },
  portalBoletos(token: string) {
    return request<Boleto[]>("/portal/boletos", {}, token);
  },
  portalCreateReading(token: string, payload: PortalReadingCreate) {
    return request<Reading>("/portal/leituras", { method: "POST", body: JSON.stringify(payload) }, token);
  },
  portalTickets(token: string) {
    return request<PortalTicket[]>("/portal/chamados", {}, token);
  },
  portalCreateTicket(token: string, payload: PortalTicketCreate) {
    return request<PortalTicket>("/portal/chamados", { method: "POST", body: JSON.stringify(payload) }, token);
  },
  portalDownloadBoleto(token: string, id: number) {
    return request<{ download_url: string | null; barcode: string | null }>(`/portal/boletos/${id}/download`, {}, token);
  },
};
