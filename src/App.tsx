import { type FormEvent, type ReactNode, useEffect, useMemo, useState } from "react";
import { api, clearPortalToken, clearToken, getStoredPortalToken, getStoredToken, storePortalToken, storeToken } from "./api";
import PortalWorkspace from "./PortalWorkspace";
import type {
  AgingReport,
  AccountsPayable,
  AccountsReceivable,
  BankReconciliationEntry,
  BootstrapRequest,
  Client,
  Contract,
  Equipment,
  FonteLeitura,
  FinanceSummary,
  FiscalBatchIssueRequest,
  FiscalConfig,
  FiscalConfigUpsert,
  FiscalDocument,
  FiscalDocumentIssueRequest,
  FiscalSummary,
  OrigemDocumentoFiscal,
  Plan,
  Reading,
  Remittance,
  Tenant,
  UserMe,
  Boleto,
  RegimeTributario,
  StatusDocumentoFiscal,
  TipoDocumentoFiscal,
} from "./types";

type AuthView = "login" | "setup" | "portal";

const emptyBootstrap: BootstrapRequest = {
  tenant_name: "Empresa Modelo",
  tenant_document: "00000000000000",
  admin_name: "Usuario Modelo",
  admin_email: "demo@printerpro.com",
  admin_password: "123456",
};

const emptyLogin = {
  tenant_key: "Empresa Modelo",
  email: "demo@printerpro.com",
  password: "123456",
};

const emptyPortalLogin = {
  tenant_key: "00000000000000",
  client_document: "",
};

const emptyClient = {
  person_type: "pj",
  name: "",
  document: "",
  email: "",
  phone: "",
  credit_score: "",
  credit_status: "",
};

const emptyPlan = {
  name: "",
  type: "franquia",
  monthly_fee: "",
  price_pb: "",
  price_color: "",
  franchise_pb: "",
  franchise_color: "",
  extra_pb: "",
  extra_color: "",
};

const emptyEquipment = {
  client_id: "",
  serial_number: "",
  brand: "",
  model: "",
  kind: "multifuncional",
  status: "disponivel",
  location: "",
};

const emptyContract = {
  client_id: "",
  plan_id: "",
  number: "",
  start_date: new Date().toISOString().slice(0, 10),
  end_date: "",
  status: "rascunho",
  billing_day: "10",
  monthly_value: "",
  franchise_pb: "",
  franchise_color: "",
  price_excess_pb: "",
  price_excess_color: "",
  notes: "",
  equipment_ids: [] as number[],
};

const emptyReading = {
  contract_id: "",
  equipment_id: "",
  reference_date: new Date().toISOString().slice(0, 10),
  source: "manual",
  counter_pb_current: "",
  counter_pb_previous: "0",
  counter_color_current: "",
  counter_color_previous: "0",
  validated: false,
  photo_url: "",
  notes: "",
};

const emptyReceivable = {
  contract_id: "",
  client_id: "",
  issue_date: new Date().toISOString().slice(0, 10),
  due_date: new Date().toISOString().slice(0, 10),
  competence: new Date().toISOString().slice(0, 7),
  description: "",
  original_amount: "",
  notes: "",
};

const emptyPayable = {
  contract_id: "",
  issue_date: new Date().toISOString().slice(0, 10),
  due_date: new Date().toISOString().slice(0, 10),
  description: "",
  category: "operacional",
  supplier_name: "",
  original_amount: "",
  notes: "",
};

const emptyBoleto = {
  receivable_id: "",
  payable_id: "",
  bank_code: "001",
  due_date: new Date().toISOString().slice(0, 10),
  amount: "",
};

const emptyRemittance = {
  bank_code: "001",
  file_type: "cnab240",
  file_name: `remessa-${new Date().toISOString().slice(0, 10)}.txt`,
  boleto_ids: [] as number[],
};

const emptyBankEntry = {
  statement_date: new Date().toISOString().slice(0, 10),
  description: "",
  reference: "",
  amount: "",
  source: "extrato",
  notes: "",
};

const emptyBilling = {
  competence: new Date().toISOString().slice(0, 7),
  bank_code: "001",
  issue_date: new Date().toISOString().slice(0, 10),
  due_date: new Date().toISOString().slice(0, 10),
  description_prefix: "Faturamento",
  generate_boleto: true,
};

const emptyFiscalConfig = {
  company_name: "Empresa Modelo",
  cnpj: "00000000000191",
  inscricao_estadual: "",
  inscricao_municipal: "",
  regime_tributario: "simples_nacional" as RegimeTributario,
  serie_nfe: "1",
  serie_nfse: "1",
  nfe_enabled: true,
  nfse_enabled: true,
  iss_rate: "2.00",
  notes: "",
};

const emptyFiscalDocument = {
  document_type: "nfse" as TipoDocumentoFiscal,
  origin: "manual" as OrigemDocumentoFiscal,
  receivable_id: "",
  contract_id: "",
  client_id: "",
  series: "",
  issue_date: new Date().toISOString().slice(0, 10),
  competence: new Date().toISOString().slice(0, 7),
  recipient_name: "",
  recipient_document: "",
  description: "",
  amount: "",
  tax_base: "",
  tax_rate: "",
  tax_amount: "",
  authorize: true,
  notes: "",
};

function currency(value: number | null | undefined) {
  if (value === null || value === undefined) return "-";
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(value);
}

function parseNumber(value: string) {
  return value === "" ? null : Number(value);
}

function App() {
  const [token, setToken] = useState<string | null>(() => getStoredToken());
  const [portalToken, setPortalToken] = useState<string | null>(() => getStoredPortalToken());
  const [me, setMe] = useState<UserMe | null>(null);
  const [authView, setAuthView] = useState<AuthView>("login");
  const [message, setMessage] = useState<string>("");
  const [busy, setBusy] = useState(false);

  const [bootstrap, setBootstrap] = useState(emptyBootstrap);
  const [login, setLogin] = useState(emptyLogin);
  const [portalLogin, setPortalLogin] = useState(emptyPortalLogin);
  const [clients, setClients] = useState<Client[]>([]);
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [readings, setReadings] = useState<Reading[]>([]);
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [financeSummary, setFinanceSummary] = useState<FinanceSummary | null>(null);
  const [receivables, setReceivables] = useState<AccountsReceivable[]>([]);
  const [payables, setPayables] = useState<AccountsPayable[]>([]);
  const [boletos, setBoletos] = useState<Boleto[]>([]);
  const [remittances, setRemittances] = useState<Remittance[]>([]);
  const [reconciliationEntries, setReconciliationEntries] = useState<BankReconciliationEntry[]>([]);
  const [agingReport, setAgingReport] = useState<AgingReport | null>(null);
  const [fiscalSummary, setFiscalSummary] = useState<FiscalSummary | null>(null);
  const [fiscalConfig, setFiscalConfig] = useState<FiscalConfig | null>(null);
  const [fiscalDocuments, setFiscalDocuments] = useState<FiscalDocument[]>([]);

  const [clientForm, setClientForm] = useState(emptyClient);
  const [planForm, setPlanForm] = useState(emptyPlan);
  const [equipmentForm, setEquipmentForm] = useState(emptyEquipment);
  const [contractForm, setContractForm] = useState(emptyContract);
  const [readingForm, setReadingForm] = useState(emptyReading);
  const [receivableForm, setReceivableForm] = useState(emptyReceivable);
  const [payableForm, setPayableForm] = useState(emptyPayable);
  const [boletoForm, setBoletoForm] = useState(emptyBoleto);
  const [remittanceForm, setRemittanceForm] = useState(emptyRemittance);
  const [bankEntryForm, setBankEntryForm] = useState(emptyBankEntry);
  const [billingForm, setBillingForm] = useState(emptyBilling);
  const [fiscalConfigForm, setFiscalConfigForm] = useState(emptyFiscalConfig);
  const [fiscalDocumentForm, setFiscalDocumentForm] = useState(emptyFiscalDocument);
  const [fiscalBatchReceivables, setFiscalBatchReceivables] = useState<string[]>([]);
  const [editingFiscalDocumentId, setEditingFiscalDocumentId] = useState<number | null>(null);
  const [tenantForm, setTenantForm] = useState({ name: "", document: "" });

  const [contractEquipmentSelection, setContractEquipmentSelection] = useState<string[]>([]);
  const [remittanceSelection, setRemittanceSelection] = useState<string[]>([]);
  const [editingTenantId, setEditingTenantId] = useState<number | null>(null);
  const [editingClientId, setEditingClientId] = useState<number | null>(null);
  const [editingPlanId, setEditingPlanId] = useState<number | null>(null);
  const [editingEquipmentId, setEditingEquipmentId] = useState<number | null>(null);
  const [editingContractId, setEditingContractId] = useState<number | null>(null);
  const [editingReadingId, setEditingReadingId] = useState<number | null>(null);
  const [editingReceivableId, setEditingReceivableId] = useState<number | null>(null);
  const [editingPayableId, setEditingPayableId] = useState<number | null>(null);

  const isAdmin = me?.role === "administrador";

  const dashboardCards = useMemo(
    () => [
      { label: "Clientes", value: clients.length },
      { label: "Equipamentos", value: equipment.length },
      { label: "Planos", value: plans.length },
      { label: "Contratos", value: contracts.length },
      { label: "Leituras", value: readings.length },
    ],
    [clients.length, equipment.length, plans.length, contracts.length, readings.length],
  );

  useEffect(() => {
    if (!token) return;
    loadSession(token).catch(() => logout());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  async function loadSession(currentToken: string) {
    const currentUser = await api.me(currentToken);
    setMe(currentUser);
    await refreshData(currentToken, currentUser.role === "administrador");
  }

  async function refreshData(currentToken = token, includeTenants = isAdmin) {
    if (!currentToken) return;
    const [clientsData, equipmentData, plansData, contractsData, readingsData] = await Promise.all([
      api.listClients(currentToken),
      api.listEquipment(currentToken),
      api.listPlans(currentToken),
      api.listContracts(currentToken),
      api.listReadings(currentToken),
    ]);
    setClients(clientsData);
    setEquipment(equipmentData);
    setPlans(plansData);
    setContracts(contractsData);
    setReadings(readingsData);
    if (includeTenants) {
      const tenantsData = await api.listTenants(currentToken);
      setTenants(tenantsData);
    }
    await refreshFinance(currentToken);
    await refreshFiscal(currentToken);
  }

  async function refreshFinance(currentToken = token) {
    if (!currentToken) return;
    const [summary, receivablesData, payablesData, boletosData, remittancesData, reconciliationData, agingData] = await Promise.all([
      api.financeSummary(currentToken),
      api.listReceivables(currentToken),
      api.listPayables(currentToken),
      api.listBoletos(currentToken),
      api.listRemittances(currentToken),
      api.listReconciliation(currentToken),
      api.agingReport(currentToken),
    ]);
    setFinanceSummary(summary);
    setReceivables(receivablesData);
    setPayables(payablesData);
    setBoletos(boletosData);
    setRemittances(remittancesData);
    setReconciliationEntries(reconciliationData);
    setAgingReport(agingData);
  }

  async function refreshFiscal(currentToken = token) {
    if (!currentToken) return;
    const [summary, config, documents] = await Promise.all([
      api.fiscalSummary(currentToken),
      api.getFiscalConfig(currentToken),
      api.listFiscalDocuments(currentToken),
    ]);
    setFiscalSummary(summary);
    setFiscalConfig(config);
    setFiscalDocuments(documents);
    setFiscalConfigForm({
      company_name: config.company_name,
      cnpj: config.cnpj || "",
      inscricao_estadual: config.inscricao_estadual || "",
      inscricao_municipal: config.inscricao_municipal || "",
      regime_tributario: config.regime_tributario,
      serie_nfe: String(config.serie_nfe),
      serie_nfse: String(config.serie_nfse),
      nfe_enabled: config.nfe_enabled,
      nfse_enabled: config.nfse_enabled,
      iss_rate: String(config.iss_rate),
      notes: config.notes || "",
    });
  }

  function logout() {
    clearToken();
    setToken(null);
    setMe(null);
    setClients([]);
    setEquipment([]);
    setPlans([]);
    setContracts([]);
    setReadings([]);
    setTenants([]);
    setFinanceSummary(null);
    setReceivables([]);
    setPayables([]);
    setBoletos([]);
    setRemittances([]);
    setReconciliationEntries([]);
    setAgingReport(null);
    setFiscalSummary(null);
    setFiscalConfig(null);
    setFiscalDocuments([]);
    setEditingTenantId(null);
    setEditingClientId(null);
    setEditingPlanId(null);
    setEditingEquipmentId(null);
    setEditingContractId(null);
    setEditingReadingId(null);
    setEditingReceivableId(null);
    setEditingPayableId(null);
    setEditingFiscalDocumentId(null);
    setFiscalConfigForm(emptyFiscalConfig);
    setFiscalDocumentForm(emptyFiscalDocument);
    setFiscalBatchReceivables([]);
    setTenantForm({ name: "", document: "" });
    setMessage("Sessao encerrada.");
  }

  function logoutPortal() {
    clearPortalToken();
    setPortalToken(null);
    setPortalLogin(emptyPortalLogin);
    setMessage("Sessao do portal encerrada.");
  }

  async function handleBootstrap(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      const response = await api.bootstrap(bootstrap);
      storeToken(response.access_token);
      setToken(response.access_token);
      await loadSession(response.access_token);
      setMessage("Sistema inicializado com sucesso.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao inicializar o sistema");
    } finally {
      setBusy(false);
    }
  }

  async function handleLogin(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      const response = await api.login(login);
      storeToken(response.access_token);
      setToken(response.access_token);
      await loadSession(response.access_token);
      setMessage("Login realizado com sucesso.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha no login");
    } finally {
      setBusy(false);
    }
  }

  async function handlePortalLogin(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      const response = await api.portalLogin(portalLogin);
      storePortalToken(response.access_token);
      setPortalToken(response.access_token);
      setMessage(`Portal liberado para ${response.client_name}.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha no acesso ao portal");
    } finally {
      setBusy(false);
    }
  }

  async function createTenant(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    setBusy(true);
    try {
      const wasEditing = editingTenantId !== null;
      const payload = {
        name: tenantForm.name,
        document: tenantForm.document || null,
      };
      if (editingTenantId) {
        await api.updateTenant(token, editingTenantId, payload);
      } else {
        await api.createTenant(token, payload);
      }
      await refreshData(token, true);
      resetTenantEditor();
      setMessage(wasEditing ? "Tenant atualizado." : "Tenant criado.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao salvar tenant");
    } finally {
      setBusy(false);
    }
  }

  async function createClient(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    setBusy(true);
    try {
      const payload = {
        ...clientForm,
        email: clientForm.email || null,
        phone: clientForm.phone || null,
        credit_score: clientForm.credit_score ? Number(clientForm.credit_score) : null,
        credit_status: clientForm.credit_status || null,
      };
      if (editingClientId) {
        await api.updateClient(token, editingClientId, payload);
      } else {
        await api.createClient(token, payload);
      }
      setClientForm(emptyClient);
      setEditingClientId(null);
      await refreshData(token);
      setMessage(editingClientId ? "Cliente atualizado." : "Cliente criado.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao salvar cliente");
    } finally {
      setBusy(false);
    }
  }

  async function createPlan(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    setBusy(true);
    try {
      const payload = {
        ...planForm,
        monthly_fee: planForm.monthly_fee ? Number(planForm.monthly_fee) : null,
        price_pb: planForm.price_pb ? Number(planForm.price_pb) : null,
        price_color: planForm.price_color ? Number(planForm.price_color) : null,
        franchise_pb: planForm.franchise_pb ? Number(planForm.franchise_pb) : null,
        franchise_color: planForm.franchise_color ? Number(planForm.franchise_color) : null,
        extra_pb: planForm.extra_pb ? Number(planForm.extra_pb) : null,
        extra_color: planForm.extra_color ? Number(planForm.extra_color) : null,
      };
      if (editingPlanId) {
        await api.updatePlan(token, editingPlanId, payload);
      } else {
        await api.createPlan(token, payload);
      }
      setPlanForm(emptyPlan);
      setEditingPlanId(null);
      await refreshData(token);
      setMessage(editingPlanId ? "Plano atualizado." : "Plano criado.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao salvar plano");
    } finally {
      setBusy(false);
    }
  }

  async function createEquipment(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    setBusy(true);
    try {
      const payload = {
        ...equipmentForm,
        client_id: equipmentForm.client_id ? Number(equipmentForm.client_id) : null,
      };
      if (editingEquipmentId) {
        await api.updateEquipment(token, editingEquipmentId, payload);
      } else {
        await api.createEquipment(token, payload);
      }
      setEquipmentForm(emptyEquipment);
      setEditingEquipmentId(null);
      await refreshData(token);
      setMessage(editingEquipmentId ? "Equipamento atualizado." : "Equipamento criado.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao salvar equipamento");
    } finally {
      setBusy(false);
    }
  }

  async function createContract(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    setBusy(true);
    try {
      const payload = {
        ...contractForm,
        client_id: Number(contractForm.client_id),
        plan_id: Number(contractForm.plan_id),
        billing_day: Number(contractForm.billing_day),
        monthly_value: contractForm.monthly_value ? Number(contractForm.monthly_value) : null,
        franchise_pb: contractForm.franchise_pb ? Number(contractForm.franchise_pb) : null,
        franchise_color: contractForm.franchise_color ? Number(contractForm.franchise_color) : null,
        price_excess_pb: contractForm.price_excess_pb ? Number(contractForm.price_excess_pb) : null,
        price_excess_color: contractForm.price_excess_color ? Number(contractForm.price_excess_color) : null,
        end_date: contractForm.end_date || null,
        equipment_ids: contractEquipmentSelection.map(Number),
      };
      if (editingContractId) {
        await api.updateContract(token, editingContractId, payload);
      } else {
        await api.createContract(token, payload);
      }
      setContractForm({ ...emptyContract, start_date: new Date().toISOString().slice(0, 10) });
      setContractEquipmentSelection([]);
      setEditingContractId(null);
      await refreshData(token);
      setMessage(editingContractId ? "Contrato atualizado." : "Contrato criado.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao salvar contrato");
    } finally {
      setBusy(false);
    }
  }

  async function createReading(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    setBusy(true);
    try {
      const payload = {
        ...readingForm,
        contract_id: Number(readingForm.contract_id),
        equipment_id: Number(readingForm.equipment_id),
        counter_pb_current: Number(readingForm.counter_pb_current),
        counter_pb_previous: Number(readingForm.counter_pb_previous),
        counter_color_current: Number(readingForm.counter_color_current),
        counter_color_previous: Number(readingForm.counter_color_previous),
        validated: Boolean(readingForm.validated),
        photo_url: readingForm.photo_url || null,
        notes: readingForm.notes || null,
      };
      if (editingReadingId) {
        await api.updateReading(token, editingReadingId, payload);
      } else {
        await api.createReading(token, payload);
      }
      setReadingForm(emptyReading);
      setEditingReadingId(null);
      await refreshData(token);
      setMessage(editingReadingId ? "Leitura atualizada." : "Leitura registrada.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao salvar leitura");
    } finally {
      setBusy(false);
    }
  }

  async function createReceivable(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    setBusy(true);
    try {
      const payload = {
        ...receivableForm,
        client_id: parseNumber(receivableForm.client_id) ?? undefined,
        contract_id: parseNumber(receivableForm.contract_id) ?? undefined,
        original_amount: Number(receivableForm.original_amount),
        notes: receivableForm.notes || null,
      };
      if (editingReceivableId) {
        await api.updateReceivable(token, editingReceivableId, payload);
      } else {
        await api.createReceivable(token, payload);
      }
      setReceivableForm(emptyReceivable);
      setEditingReceivableId(null);
      await refreshData(token);
      setMessage(editingReceivableId ? "Conta a receber atualizada." : "Conta a receber criada.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao salvar conta a receber");
    } finally {
      setBusy(false);
    }
  }

  async function settleReceivable(receivableId: number) {
    if (!token) return;
    setBusy(true);
    try {
      await api.settleReceivable(token, receivableId, { paid_amount: undefined, notes: "Baixa manual" });
      await refreshData(token);
      setMessage("Conta a receber baixada.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha na baixa");
    } finally {
      setBusy(false);
    }
  }

  async function createPayable(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    setBusy(true);
    try {
      const payload = {
        ...payableForm,
        contract_id: parseNumber(payableForm.contract_id) ?? undefined,
        original_amount: Number(payableForm.original_amount),
        supplier_name: payableForm.supplier_name || null,
        notes: payableForm.notes || null,
      };
      if (editingPayableId) {
        await api.updatePayable(token, editingPayableId, payload);
      } else {
        await api.createPayable(token, payload);
      }
      setPayableForm(emptyPayable);
      setEditingPayableId(null);
      await refreshData(token);
      setMessage(editingPayableId ? "Conta a pagar atualizada." : "Conta a pagar criada.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao salvar conta a pagar");
    } finally {
      setBusy(false);
    }
  }

  async function settlePayable(payableId: number) {
    if (!token) return;
    setBusy(true);
    try {
      await api.settlePayable(token, payableId, { paid_amount: undefined, notes: "Baixa manual" });
      await refreshData(token);
      setMessage("Conta a pagar baixada.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha na baixa");
    } finally {
      setBusy(false);
    }
  }

  async function createBoleto(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    setBusy(true);
    try {
      await api.createBoleto(token, {
        receivable_id: parseNumber(boletoForm.receivable_id) ?? undefined,
        payable_id: parseNumber(boletoForm.payable_id) ?? undefined,
        bank_code: boletoForm.bank_code,
        due_date: boletoForm.due_date,
        amount: Number(boletoForm.amount),
      });
      setBoletoForm(emptyBoleto);
      await refreshData(token);
      setMessage("Boleto criado.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao criar boleto");
    } finally {
      setBusy(false);
    }
  }

  async function sendBoleto(boletoId: number) {
    if (!token) return;
    setBusy(true);
    try {
      await api.sendBoleto(token, boletoId);
      await refreshData(token);
      setMessage("Boleto enviado.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao enviar boleto");
    } finally {
      setBusy(false);
    }
  }

  async function settleBoleto(boletoId: number) {
    if (!token) return;
    setBusy(true);
    try {
      await api.settleBoleto(token, boletoId);
      await refreshData(token);
      setMessage("Boleto baixado.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha na baixa do boleto");
    } finally {
      setBusy(false);
    }
  }

  async function duplicateContract(contractId: number) {
    if (!token) return;
    setBusy(true);
    try {
      await api.duplicateContract(token, contractId);
      await refreshData(token);
      setMessage("Contrato duplicado.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao duplicar contrato");
    } finally {
      setBusy(false);
    }
  }

  async function closeContract(contractId: number) {
    if (!token) return;
    setBusy(true);
    try {
      await api.closeContract(token, contractId);
      await refreshData(token);
      setMessage("Contrato encerrado.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao encerrar contrato");
    } finally {
      setBusy(false);
    }
  }

  async function toggleEquipmentStatus(item: Equipment) {
    if (!token) return;
    setBusy(true);
    try {
      const nextStatus = item.status === "baixado" ? "disponivel" : "baixado";
      await api.updateEquipment(token, item.id, { status: nextStatus, client_id: item.client_id });
      await refreshData(token);
      setMessage(nextStatus === "baixado" ? "Equipamento desativado." : "Equipamento ativado.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao alterar status do equipamento");
    } finally {
      setBusy(false);
    }
  }

  async function createRemittance(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    setBusy(true);
    try {
      await api.createRemittance(token, {
        bank_code: remittanceForm.bank_code,
        file_type: remittanceForm.file_type,
        file_name: remittanceForm.file_name,
        boleto_ids: remittanceSelection.map(Number),
      });
      setRemittanceForm(emptyRemittance);
      setRemittanceSelection([]);
      await refreshData(token);
      setMessage("Remessa criada.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao criar remessa");
    } finally {
      setBusy(false);
    }
  }

  async function importBankEntries(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    setBusy(true);
    try {
      await api.importBankEntries(token, {
        auto_match: true,
        entries: [
          {
            statement_date: bankEntryForm.statement_date,
            description: bankEntryForm.description,
            reference: bankEntryForm.reference || null,
            amount: Number(bankEntryForm.amount),
            source: bankEntryForm.source,
            notes: bankEntryForm.notes || null,
          },
        ],
      });
      setBankEntryForm(emptyBankEntry);
      await refreshData(token);
      setMessage("Conciliação importada.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha na importação da conciliação");
    } finally {
      setBusy(false);
    }
  }

  async function generateBilling(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    setBusy(true);
    try {
      await api.generateBilling(token, {
        competence: billingForm.competence,
        bank_code: billingForm.bank_code,
        issue_date: billingForm.issue_date,
        due_date: billingForm.due_date,
        description_prefix: billingForm.description_prefix,
        generate_boleto: billingForm.generate_boleto,
      });
      await refreshData(token);
      setMessage("Faturamento financeiro gerado.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao gerar faturamento");
    } finally {
      setBusy(false);
    }
  }

  async function saveFiscalConfig(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    setBusy(true);
    try {
      await api.updateFiscalConfig(token, {
        company_name: fiscalConfigForm.company_name,
        cnpj: fiscalConfigForm.cnpj,
        inscricao_estadual: fiscalConfigForm.inscricao_estadual,
        inscricao_municipal: fiscalConfigForm.inscricao_municipal,
        regime_tributario: fiscalConfigForm.regime_tributario,
        serie_nfe: Number(fiscalConfigForm.serie_nfe),
        serie_nfse: Number(fiscalConfigForm.serie_nfse),
        nfe_enabled: fiscalConfigForm.nfe_enabled,
        nfse_enabled: fiscalConfigForm.nfse_enabled,
        iss_rate: Number(fiscalConfigForm.iss_rate),
        notes: fiscalConfigForm.notes,
      });
      await refreshFiscal(token);
      setMessage("Configuração fiscal salva.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao salvar configuração fiscal");
    } finally {
      setBusy(false);
    }
  }

  async function saveFiscalDocument(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    setBusy(true);
    try {
      const payload = {
        document_type: fiscalDocumentForm.document_type,
        origin: fiscalDocumentForm.origin,
        receivable_id: parseNumber(fiscalDocumentForm.receivable_id) ?? undefined,
        contract_id: parseNumber(fiscalDocumentForm.contract_id) ?? undefined,
        client_id: parseNumber(fiscalDocumentForm.client_id) ?? undefined,
        series: parseNumber(fiscalDocumentForm.series) ?? undefined,
        issue_date: fiscalDocumentForm.issue_date,
        competence: fiscalDocumentForm.competence,
        recipient_name: fiscalDocumentForm.recipient_name || null,
        recipient_document: fiscalDocumentForm.recipient_document || null,
        description: fiscalDocumentForm.description || null,
        amount: parseNumber(fiscalDocumentForm.amount),
        tax_base: parseNumber(fiscalDocumentForm.tax_base),
        tax_rate: parseNumber(fiscalDocumentForm.tax_rate),
        tax_amount: parseNumber(fiscalDocumentForm.tax_amount),
        authorize: fiscalDocumentForm.authorize,
        notes: fiscalDocumentForm.notes || null,
      };
      if (editingFiscalDocumentId) {
        await api.updateFiscalDocument(token, editingFiscalDocumentId, payload);
      } else {
        await api.createFiscalDocument(token, payload);
      }
      setFiscalDocumentForm(emptyFiscalDocument);
      setEditingFiscalDocumentId(null);
      await refreshFiscal(token);
      setMessage(editingFiscalDocumentId ? "Documento fiscal atualizado." : "Documento fiscal emitido.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao salvar documento fiscal");
    } finally {
      setBusy(false);
    }
  }

  async function batchIssueFiscalDocuments(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    setBusy(true);
    try {
      const payload = {
        document_type: fiscalDocumentForm.document_type,
        receivable_ids: fiscalBatchReceivables.map(Number),
        authorize: fiscalDocumentForm.authorize,
        issue_date: fiscalDocumentForm.issue_date,
        competence: fiscalDocumentForm.competence,
        series: parseNumber(fiscalDocumentForm.series) ?? undefined,
      };
      await api.batchIssueFiscalDocuments(token, payload);
      setFiscalBatchReceivables([]);
      await refreshFiscal(token);
      setMessage("Documentos fiscais gerados em lote.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao gerar documentos fiscais em lote");
    } finally {
      setBusy(false);
    }
  }

  async function authorizeFiscalDocument(id: number) {
    if (!token) return;
    setBusy(true);
    try {
      await api.authorizeFiscalDocument(token, id);
      await refreshFiscal(token);
      setMessage("Documento fiscal autorizado.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao autorizar documento fiscal");
    } finally {
      setBusy(false);
    }
  }

  async function cancelFiscalDocument(id: number) {
    if (!token) return;
    setBusy(true);
    try {
      await api.cancelFiscalDocument(token, id);
      await refreshFiscal(token);
      setMessage("Documento fiscal cancelado.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao cancelar documento fiscal");
    } finally {
      setBusy(false);
    }
  }

  async function removeFiscalDocument(id: number) {
    if (!token) return;
    setBusy(true);
    try {
      await api.deleteFiscalDocument(token, id);
      if (editingFiscalDocumentId === id) {
        setEditingFiscalDocumentId(null);
        setFiscalDocumentForm(emptyFiscalDocument);
      }
      await refreshFiscal(token);
      setMessage("Documento fiscal removido.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao remover documento fiscal");
    } finally {
      setBusy(false);
    }
  }

  async function removeItem(
    kind: "tenant" | "client" | "equipment" | "plan" | "contract" | "reading" | "receivable" | "payable" | "boleto",
    id: number,
  ) {
    if (!token) return;
    setBusy(true);
    try {
      if (kind === "tenant") await api.deleteTenant(token, id);
      if (kind === "client") await api.deleteClient(token, id);
      if (kind === "equipment") await api.deleteEquipment(token, id);
      if (kind === "plan") await api.deletePlan(token, id);
      if (kind === "contract") await api.deleteContract(token, id);
      if (kind === "reading") await api.deleteReading(token, id);
      if (kind === "receivable") await api.deleteReceivable(token, id);
      if (kind === "payable") await api.deletePayable(token, id);
      if (kind === "boleto") await api.deleteBoleto(token, id);
      if (kind === "client" && editingClientId === id) resetClientEditor();
      if (kind === "equipment" && editingEquipmentId === id) resetEquipmentEditor();
      if (kind === "plan" && editingPlanId === id) resetPlanEditor();
      if (kind === "contract" && editingContractId === id) resetContractEditor();
      if (kind === "reading" && editingReadingId === id) resetReadingEditor();
      if (kind === "receivable" && editingReceivableId === id) resetReceivableEditor();
      if (kind === "payable" && editingPayableId === id) resetPayableEditor();
      if (kind === "tenant" && editingTenantId === id) resetTenantEditor();
      await refreshData(token, isAdmin);
      setMessage(`${kind} removido.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao remover item");
    } finally {
      setBusy(false);
    }
  }

  function editClient(client: Client) {
    setClientForm({
      person_type: client.person_type,
      name: client.name,
      document: client.document,
      email: client.email || "",
      phone: client.phone || "",
      credit_score: client.credit_score?.toString() ?? "",
      credit_status: client.credit_status || "",
    });
    setEditingClientId(client.id);
  }

  function editPlan(plan: Plan) {
    setPlanForm({
      name: plan.name,
      type: plan.type,
      monthly_fee: plan.monthly_fee?.toString() ?? "",
      price_pb: plan.price_pb?.toString() ?? "",
      price_color: plan.price_color?.toString() ?? "",
      franchise_pb: plan.franchise_pb?.toString() ?? "",
      franchise_color: plan.franchise_color?.toString() ?? "",
      extra_pb: plan.extra_pb?.toString() ?? "",
      extra_color: plan.extra_color?.toString() ?? "",
    });
    setEditingPlanId(plan.id);
  }

  function editEquipment(item: Equipment) {
    setEquipmentForm({
      client_id: item.client_id ? String(item.client_id) : "",
      serial_number: item.serial_number,
      brand: item.brand,
      model: item.model,
      kind: item.kind,
      status: item.status,
      location: item.location || "",
    });
    setEditingEquipmentId(item.id);
  }

  function editContract(contract: Contract) {
    setContractForm({
      client_id: String(contract.client_id),
      plan_id: String(contract.plan_id),
      number: contract.number,
      start_date: contract.start_date,
      end_date: contract.end_date || "",
      status: contract.status,
      billing_day: String(contract.billing_day),
      monthly_value: contract.monthly_value?.toString() ?? "",
      franchise_pb: contract.franchise_pb?.toString() ?? "",
      franchise_color: contract.franchise_color?.toString() ?? "",
      price_excess_pb: contract.price_excess_pb?.toString() ?? "",
      price_excess_color: contract.price_excess_color?.toString() ?? "",
      notes: contract.notes || "",
      equipment_ids: (contract.equipments ?? []).map((item) => item.equipment_id),
    });
    setContractEquipmentSelection((contract.equipments ?? []).map((item) => String(item.equipment_id)));
    setEditingContractId(contract.id);
  }

  function editReading(reading: Reading) {
    setReadingForm({
      contract_id: String(reading.contract_id),
      equipment_id: String(reading.equipment_id),
      reference_date: reading.reference_date,
      source: reading.source,
      counter_pb_current: String(reading.counter_pb_current),
      counter_pb_previous: String(reading.counter_pb_previous),
      counter_color_current: String(reading.counter_color_current),
      counter_color_previous: String(reading.counter_color_previous),
      validated: reading.validated,
      photo_url: reading.photo_url || "",
      notes: reading.notes || "",
    });
    setEditingReadingId(reading.id);
  }

  function editReceivable(item: AccountsReceivable) {
    setReceivableForm({
      contract_id: item.contract_id ? String(item.contract_id) : "",
      client_id: item.client_id ? String(item.client_id) : "",
      issue_date: item.issue_date,
      due_date: item.due_date,
      competence: item.competence,
      description: item.description,
      original_amount: String(item.original_amount),
      notes: item.notes || "",
    });
    setEditingReceivableId(item.id);
  }

  function editPayable(item: AccountsPayable) {
    setPayableForm({
      contract_id: item.contract_id ? String(item.contract_id) : "",
      issue_date: item.issue_date,
      due_date: item.due_date,
      description: item.description,
      category: item.category,
      supplier_name: item.supplier_name || "",
      original_amount: String(item.original_amount),
      notes: item.notes || "",
    });
    setEditingPayableId(item.id);
  }

  function editFiscalDocument(document: FiscalDocument) {
    setFiscalDocumentForm({
      document_type: document.document_type,
      origin: document.origin,
      receivable_id: document.receivable_id ? String(document.receivable_id) : "",
      contract_id: document.contract_id ? String(document.contract_id) : "",
      client_id: document.client_id ? String(document.client_id) : "",
      series: String(document.series),
      issue_date: document.issue_date,
      competence: document.competence,
      recipient_name: document.recipient_name,
      recipient_document: document.recipient_document || "",
      description: document.description,
      amount: String(document.amount),
      tax_base: document.tax_base ? String(document.tax_base) : "",
      tax_rate: document.tax_rate ? String(document.tax_rate) : "",
      tax_amount: document.tax_amount ? String(document.tax_amount) : "",
      authorize: document.status === "autorizado",
      notes: document.notes || "",
    });
    setEditingFiscalDocumentId(document.id);
  }

  function resetClientEditor() {
    setClientForm(emptyClient);
    setEditingClientId(null);
  }

  function resetPlanEditor() {
    setPlanForm(emptyPlan);
    setEditingPlanId(null);
  }

  function resetEquipmentEditor() {
    setEquipmentForm(emptyEquipment);
    setEditingEquipmentId(null);
  }

  function resetContractEditor() {
    setContractForm({ ...emptyContract, start_date: new Date().toISOString().slice(0, 10) });
    setContractEquipmentSelection([]);
    setEditingContractId(null);
  }

  function resetReadingEditor() {
    setReadingForm(emptyReading);
    setEditingReadingId(null);
  }

  function resetReceivableEditor() {
    setReceivableForm(emptyReceivable);
    setEditingReceivableId(null);
  }

  function resetPayableEditor() {
    setPayableForm(emptyPayable);
    setEditingPayableId(null);
  }

  function resetFiscalDocumentEditor() {
    setFiscalDocumentForm(emptyFiscalDocument);
    setEditingFiscalDocumentId(null);
  }

  function editTenant(tenant: Tenant) {
    setTenantForm({
      name: tenant.name,
      document: tenant.document || "",
    });
    setEditingTenantId(tenant.id);
  }

  function resetTenantEditor() {
    setTenantForm({ name: "", document: "" });
    setEditingTenantId(null);
  }

  if (token && !me) {
    return (
      <div className="loading-shell">
        <div className="loading-card">
          <div className="brand-mark">PM</div>
          <h1>Carregando sessão</h1>
          <p>Estamos validando seu acesso e preparando o painel.</p>
        </div>
      </div>
    );
  }

  if (portalToken && !token) {
    return <PortalWorkspace token={portalToken} onLogout={logoutPortal} />;
  }

  if (!token || !me) {
    return (
      <div className="auth-shell">
        <section className="hero-panel">
          <div className="hero-badge">PrintManager Pro</div>
          <h1>Controle a operação de locação de impressoras com um fluxo único e claro.</h1>
          <p>
            Cadastre tenants, clientes, equipamentos, contratos e leituras em um sistema preparado para multi-tenant,
            faturamento e evolução fiscal.
          </p>
          <div className="hero-points">
            <span>Login com tenant</span>
            <span>Fluxo de bootstrap inicial</span>
            <span>MVP operacional</span>
            <span>Portal do cliente</span>
          </div>
        </section>

        <section className="auth-panel">
          <div className="auth-tabs">
            <button type="button" className={authView === "login" ? "active" : ""} onClick={() => setAuthView("login")}>
              Entrar
            </button>
            <button type="button" className={authView === "setup" ? "active" : ""} onClick={() => setAuthView("setup")}>
              Primeiro acesso
            </button>
            <button type="button" className={authView === "portal" ? "active" : ""} onClick={() => setAuthView("portal")}>
              Portal
            </button>
          </div>

          {authView === "login" ? (
            <form className="panel-form" onSubmit={handleLogin}>
              <h2>Entrar no sistema</h2>
              <Field label="Tenant (nome ou documento)">
                <input value={login.tenant_key} onChange={(e) => setLogin({ ...login, tenant_key: e.target.value })} />
              </Field>
              <Field label="E-mail">
                <input value={login.email} onChange={(e) => setLogin({ ...login, email: e.target.value })} />
              </Field>
              <Field label="Senha">
                <input
                  type="password"
                  value={login.password}
                  onChange={(e) => setLogin({ ...login, password: e.target.value })}
                />
              </Field>
              <button className="primary" type="submit" disabled={busy}>
                {busy ? "Entrando..." : "Acessar"}
              </button>
            </form>
          ) : authView === "setup" ? (
            <form className="panel-form" onSubmit={handleBootstrap}>
              <h2>Inicializar sistema</h2>
              <Field label="Nome do tenant">
                <input
                  value={bootstrap.tenant_name}
                  onChange={(e) => setBootstrap({ ...bootstrap, tenant_name: e.target.value })}
                />
              </Field>
              <Field label="Documento do tenant">
                <input
                  value={bootstrap.tenant_document}
                  onChange={(e) => setBootstrap({ ...bootstrap, tenant_document: e.target.value })}
                />
              </Field>
              <Field label="Nome do admin">
                <input
                  value={bootstrap.admin_name}
                  onChange={(e) => setBootstrap({ ...bootstrap, admin_name: e.target.value })}
                />
              </Field>
              <Field label="E-mail do admin">
                <input
                  value={bootstrap.admin_email}
                  onChange={(e) => setBootstrap({ ...bootstrap, admin_email: e.target.value })}
                />
              </Field>
              <Field label="Senha do admin">
                <input
                  type="password"
                  value={bootstrap.admin_password}
                  onChange={(e) => setBootstrap({ ...bootstrap, admin_password: e.target.value })}
                />
              </Field>
              <button className="primary" type="submit" disabled={busy}>
                {busy ? "Criando..." : "Criar ambiente"}
              </button>
            </form>
          ) : (
            <form className="panel-form" onSubmit={handlePortalLogin}>
              <h2>Entrar no portal</h2>
              <Field label="Tenant (nome ou documento)">
                <input
                  value={portalLogin.tenant_key}
                  onChange={(e) => setPortalLogin({ ...portalLogin, tenant_key: e.target.value })}
                />
              </Field>
              <Field label="Documento do cliente">
                <input
                  value={portalLogin.client_document}
                  onChange={(e) => setPortalLogin({ ...portalLogin, client_document: e.target.value })}
                />
              </Field>
              <button className="primary" type="submit" disabled={busy}>
                {busy ? "Entrando..." : "Acessar portal"}
              </button>
            </form>
          )}

          {message ? <div className="notice">{message}</div> : null}
        </section>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <div className="brand-mark">PM</div>
          <h1>PrintManager Pro</h1>
          <p>Operação, cobrança e leitura em um único painel.</p>
        </div>

        <div className="sidebar-block">
          <span className="sidebar-label">Usuário</span>
          <strong>{me.name}</strong>
          <small>{me.email}</small>
        </div>

        <div className="sidebar-block">
          <span className="sidebar-label">Tenant</span>
          <strong>ID {me.tenant_id}</strong>
          <small>{me.role}</small>
        </div>

        <button className="ghost" onClick={logout}>
          Sair
        </button>
      </aside>

      <main className="workspace">
        <header className="workspace-header">
          <div>
            <span className="eyebrow">MVP Fase 1</span>
            <h2>Fluxo operacional pronto para uso.</h2>
            <p>Cadastre tenant, cliente, equipamento, plano, contrato e leitura. O restante do sistema evolui em cima disso.</p>
          </div>
          <div className="header-message">{busy ? "Processando..." : message || "Tudo pronto para operar."}</div>
        </header>

        <section className="metric-grid">
          {dashboardCards.map((card) => (
            <article key={card.label} className="metric-card">
              <span>{card.label}</span>
              <strong>{card.value}</strong>
            </article>
          ))}
        </section>

        <section className="content-grid">
          {isAdmin ? (
            <Panel title="Tenants" description="Acesso administrativo para novos tenants e manutenção de base">
              <form className="inline-form" onSubmit={createTenant}>
                <input placeholder="Nome do tenant" value={tenantForm.name} onChange={(e) => setTenantForm({ ...tenantForm, name: e.target.value })} />
                <input placeholder="Documento" value={tenantForm.document} onChange={(e) => setTenantForm({ ...tenantForm, document: e.target.value })} />
                <button className="secondary" type="submit">
                  {editingTenantId ? "Atualizar" : "Criar"}
                </button>
                {editingTenantId ? (
                  <button type="button" className="secondary" onClick={resetTenantEditor}>
                    Cancelar edição
                  </button>
                ) : null}
              </form>
              <DataList
                items={tenants}
                searchableText={(tenant) => `${tenant.name} ${tenant.document || ""}`}
                searchPlaceholder="Pesquisar tenant"
                renderItem={(tenant) => (
                  <>
                    <div>
                      <strong>{tenant.name}</strong>
                      <small>{tenant.document || "sem documento"}</small>
                    </div>
                    <div className="inline-actions">
                      <button type="button" className="secondary" onClick={() => editTenant(tenant)}>
                        Editar
                      </button>
                      <button type="button" onClick={() => removeItem("tenant", tenant.id)}>
                        Excluir
                      </button>
                    </div>
                  </>
                )}
              />
            </Panel>
          ) : null}

          <Panel title="Clientes" description="Cadastro base para contratos e faturamento">
            <form className="panel-form compact" onSubmit={createClient}>
              <Row>
                <Select
                  label="Tipo"
                  value={clientForm.person_type}
                  onChange={(value) => setClientForm({ ...clientForm, person_type: value })}
                  options={[
                    { value: "pj", label: "PJ" },
                    { value: "pf", label: "PF" },
                  ]}
                />
                <Field label="Nome">
                  <input value={clientForm.name} onChange={(e) => setClientForm({ ...clientForm, name: e.target.value })} />
                </Field>
              </Row>
              <Row>
                <Field label="Documento">
                  <input
                    value={clientForm.document}
                    onChange={(e) => setClientForm({ ...clientForm, document: e.target.value })}
                  />
                </Field>
                <Field label="E-mail">
                  <input value={clientForm.email} onChange={(e) => setClientForm({ ...clientForm, email: e.target.value })} />
                </Field>
              </Row>
              <Row>
                <Field label="Telefone">
                  <input value={clientForm.phone} onChange={(e) => setClientForm({ ...clientForm, phone: e.target.value })} />
                </Field>
                <Field label="Score">
                  <input
                    type="number"
                    value={clientForm.credit_score}
                    onChange={(e) => setClientForm({ ...clientForm, credit_score: e.target.value })}
                  />
                </Field>
              </Row>
              <Field label="Status de crédito">
                <input
                  value={clientForm.credit_status}
                  onChange={(e) => setClientForm({ ...clientForm, credit_status: e.target.value })}
                />
              </Field>
              <div className="inline-actions">
                <button className="primary" type="submit">
                  {editingClientId ? "Atualizar cliente" : "Salvar cliente"}
                </button>
                {editingClientId ? (
                  <button type="button" className="secondary" onClick={resetClientEditor}>
                    Cancelar edição
                  </button>
                ) : null}
              </div>
            </form>
            <DataList
              items={clients}
              searchableText={(client) => `${client.name} ${client.document} ${client.email || ""} ${client.phone || ""}`}
              searchPlaceholder="Pesquisar cliente"
              renderItem={(client) => (
                <>
                  <div>
                    <strong>{client.name}</strong>
                    <small>
                      {client.document} | {client.person_type.toUpperCase()} | {client.credit_status || "sem status"}
                    </small>
                  </div>
                  <div className="inline-actions">
                    <button type="button" className="secondary" onClick={() => editClient(client)}>
                      Editar
                    </button>
                    <button type="button" onClick={() => removeItem("client", client.id)}>
                      Excluir
                    </button>
                  </div>
                </>
              )}
            />
          </Panel>

          <Panel title="Planos" description="Definição dos modelos de cobrança">
            <form className="panel-form compact" onSubmit={createPlan}>
              <Row>
                <Field label="Nome">
                  <input value={planForm.name} onChange={(e) => setPlanForm({ ...planForm, name: e.target.value })} />
                </Field>
                <Select
                  label="Tipo"
                  value={planForm.type}
                  onChange={(value) => setPlanForm({ ...planForm, type: value })}
                  options={[
                    { value: "franquia", label: "Franquia" },
                    { value: "por_pagina", label: "Por página" },
                    { value: "mensalidade", label: "Mensalidade" },
                  ]}
                />
              </Row>
              <Row>
                <Field label="Mensalidade">
                  <input
                    type="number"
                    step="0.01"
                    value={planForm.monthly_fee}
                    onChange={(e) => setPlanForm({ ...planForm, monthly_fee: e.target.value })}
                  />
                </Field>
                <Field label="Preço P&B">
                  <input
                    type="number"
                    step="0.0001"
                    value={planForm.price_pb}
                    onChange={(e) => setPlanForm({ ...planForm, price_pb: e.target.value })}
                  />
                </Field>
              </Row>
              <Row>
                <Field label="Preço Color">
                  <input
                    type="number"
                    step="0.0001"
                    value={planForm.price_color}
                    onChange={(e) => setPlanForm({ ...planForm, price_color: e.target.value })}
                  />
                </Field>
                <Field label="Franquia P&B">
                  <input
                    type="number"
                    value={planForm.franchise_pb}
                    onChange={(e) => setPlanForm({ ...planForm, franchise_pb: e.target.value })}
                  />
                </Field>
              </Row>
              <Row>
                <Field label="Franquia Color">
                  <input
                    type="number"
                    value={planForm.franchise_color}
                    onChange={(e) => setPlanForm({ ...planForm, franchise_color: e.target.value })}
                  />
                </Field>
                <Field label="Excedente P&B">
                  <input
                    type="number"
                    step="0.0001"
                    value={planForm.extra_pb}
                    onChange={(e) => setPlanForm({ ...planForm, extra_pb: e.target.value })}
                  />
                </Field>
              </Row>
              <Field label="Excedente Color">
                <input
                  type="number"
                  step="0.0001"
                  value={planForm.extra_color}
                  onChange={(e) => setPlanForm({ ...planForm, extra_color: e.target.value })}
                />
              </Field>
              <div className="inline-actions">
                <button className="primary" type="submit">
                  {editingPlanId ? "Atualizar plano" : "Salvar plano"}
                </button>
                {editingPlanId ? (
                  <button type="button" className="secondary" onClick={resetPlanEditor}>
                    Cancelar edição
                  </button>
                ) : null}
              </div>
            </form>
            <DataList
              items={plans}
              searchableText={(plan) => `${plan.name} ${plan.type}`}
              searchPlaceholder="Pesquisar plano"
              filterOptions={[
                { value: "active", label: "Ativos" },
                { value: "inactive", label: "Inativos" },
              ]}
              filterPredicate={(plan, filterValue) => (filterValue === "active" ? plan.is_active : !plan.is_active)}
              renderItem={(plan) => (
                <>
                  <div>
                    <strong>{plan.name}</strong>
                    <small>
                      {plan.type} | {currency(plan.monthly_fee)}
                    </small>
                  </div>
                  <div className="inline-actions">
                    <button type="button" className="secondary" onClick={() => editPlan(plan)}>
                      Editar
                    </button>
                    <button type="button" onClick={() => removeItem("plan", plan.id)}>
                      Excluir
                    </button>
                  </div>
                </>
              )}
            />
          </Panel>

          <Panel title="Equipamentos" description="Controle de impressoras e vínculos com cliente">
            <form className="panel-form compact" onSubmit={createEquipment}>
              <Row>
                <Select
                  label="Cliente"
                  value={equipmentForm.client_id}
                  onChange={(value) => setEquipmentForm({ ...equipmentForm, client_id: value })}
                  options={[
                    { value: "", label: "Sem vínculo" },
                    ...clients.map((client) => ({ value: String(client.id), label: `${client.name} (#${client.id})` })),
                  ]}
                />
                <Field label="Serial">
                  <input
                    value={equipmentForm.serial_number}
                    onChange={(e) => setEquipmentForm({ ...equipmentForm, serial_number: e.target.value })}
                  />
                </Field>
              </Row>
              <Row>
                <Field label="Marca">
                  <input value={equipmentForm.brand} onChange={(e) => setEquipmentForm({ ...equipmentForm, brand: e.target.value })} />
                </Field>
                <Field label="Modelo">
                  <input value={equipmentForm.model} onChange={(e) => setEquipmentForm({ ...equipmentForm, model: e.target.value })} />
                </Field>
              </Row>
              <Row>
                <Field label="Tipo">
                  <input value={equipmentForm.kind} onChange={(e) => setEquipmentForm({ ...equipmentForm, kind: e.target.value })} />
                </Field>
                <Select
                  label="Status"
                  value={equipmentForm.status}
                  onChange={(value) => setEquipmentForm({ ...equipmentForm, status: value })}
                  options={[
                    { value: "disponivel", label: "Disponível" },
                    { value: "locado", label: "Locado" },
                    { value: "em_manutencao", label: "Manutenção" },
                    { value: "baixado", label: "Baixado" },
                  ]}
                />
              </Row>
              <Field label="Local">
                <input value={equipmentForm.location} onChange={(e) => setEquipmentForm({ ...equipmentForm, location: e.target.value })} />
              </Field>
              <div className="inline-actions">
                <button className="primary" type="submit">
                  {editingEquipmentId ? "Atualizar equipamento" : "Salvar equipamento"}
                </button>
                {editingEquipmentId ? (
                  <button type="button" className="secondary" onClick={resetEquipmentEditor}>
                    Cancelar edição
                  </button>
                ) : null}
              </div>
            </form>
            <DataList
              items={equipment}
              searchableText={(item) => `${item.brand} ${item.model} ${item.serial_number} ${item.kind}`}
              searchPlaceholder="Pesquisar equipamento"
              filterOptions={[
                { value: "disponivel", label: "Disponíveis" },
                { value: "locado", label: "Locados" },
                { value: "em_manutencao", label: "Em manutenção" },
                { value: "baixado", label: "Baixados" },
              ]}
              filterPredicate={(item, filterValue) => item.status === filterValue}
              renderItem={(item) => (
                <>
                  <div>
                    <strong>{item.brand} {item.model}</strong>
                    <small>
                      {item.serial_number} | {item.status}
                    </small>
                  </div>
                  <div className="inline-actions">
                    <button type="button" className="secondary" onClick={() => editEquipment(item)}>
                      Editar
                    </button>
                    <button type="button" className="secondary" onClick={() => toggleEquipmentStatus(item)}>
                      {item.status === "baixado" ? "Ativar" : "Desativar"}
                    </button>
                    <button type="button" onClick={() => removeItem("equipment", item.id)}>
                      Excluir
                    </button>
                  </div>
                </>
              )}
            />
          </Panel>

          <Panel title="Contratos" description="Vincula cliente, plano e equipamentos">
            <form className="panel-form compact" onSubmit={createContract}>
              <Row>
                <Select
                  label="Cliente"
                  value={contractForm.client_id}
                  onChange={(value) => setContractForm({ ...contractForm, client_id: value })}
                  options={clients.map((client) => ({ value: String(client.id), label: `${client.name} (#${client.id})` }))}
                />
                <Select
                  label="Plano"
                  value={contractForm.plan_id}
                  onChange={(value) => setContractForm({ ...contractForm, plan_id: value })}
                  options={plans.map((plan) => ({ value: String(plan.id), label: `${plan.name} (#${plan.id})` }))}
                />
              </Row>
              <Row>
                <Field label="Número">
                  <input value={contractForm.number} onChange={(e) => setContractForm({ ...contractForm, number: e.target.value })} />
                </Field>
                <Field label="Início">
                  <input type="date" value={contractForm.start_date} onChange={(e) => setContractForm({ ...contractForm, start_date: e.target.value })} />
                </Field>
              </Row>
              <Row>
                <Field label="Fim">
                  <input type="date" value={contractForm.end_date} onChange={(e) => setContractForm({ ...contractForm, end_date: e.target.value })} />
                </Field>
                <Select
                  label="Status"
                  value={contractForm.status}
                  onChange={(value) => setContractForm({ ...contractForm, status: value })}
                  options={[
                    { value: "rascunho", label: "Rascunho" },
                    { value: "vigente", label: "Vigente" },
                    { value: "suspenso", label: "Suspenso" },
                    { value: "encerrado", label: "Encerrado" },
                  ]}
                />
              </Row>
              <Row>
                <Field label="Dia de vencimento">
                  <input
                    type="number"
                    value={contractForm.billing_day}
                    onChange={(e) => setContractForm({ ...contractForm, billing_day: e.target.value })}
                  />
                </Field>
                <Field label="Valor mensal">
                  <input
                    type="number"
                    step="0.01"
                    value={contractForm.monthly_value}
                    onChange={(e) => setContractForm({ ...contractForm, monthly_value: e.target.value })}
                  />
                </Field>
              </Row>
              <Row>
                <Field label="Franquia P&B">
                  <input
                    type="number"
                    value={contractForm.franchise_pb}
                    onChange={(e) => setContractForm({ ...contractForm, franchise_pb: e.target.value })}
                  />
                </Field>
                <Field label="Franquia Color">
                  <input
                    type="number"
                    value={contractForm.franchise_color}
                    onChange={(e) => setContractForm({ ...contractForm, franchise_color: e.target.value })}
                  />
                </Field>
              </Row>
              <Row>
                <Field label="Excedente P&B">
                  <input
                    type="number"
                    step="0.0001"
                    value={contractForm.price_excess_pb}
                    onChange={(e) => setContractForm({ ...contractForm, price_excess_pb: e.target.value })}
                  />
                </Field>
                <Field label="Excedente Color">
                  <input
                    type="number"
                    step="0.0001"
                    value={contractForm.price_excess_color}
                    onChange={(e) => setContractForm({ ...contractForm, price_excess_color: e.target.value })}
                  />
                </Field>
              </Row>
              <Field label="Observações">
                <textarea value={contractForm.notes} onChange={(e) => setContractForm({ ...contractForm, notes: e.target.value })} />
              </Field>
              <div className="choice-list">
                {equipment.map((item) => (
                  <label key={item.id} className="choice-item">
                    <input
                      type="checkbox"
                      checked={contractEquipmentSelection.includes(String(item.id))}
                      onChange={(e) => {
                        const id = String(item.id);
                        setContractEquipmentSelection((current) =>
                          e.target.checked ? [...current, id] : current.filter((value) => value !== id),
                        );
                      }}
                    />
                    <span>{item.brand} {item.model} #{item.id}</span>
                  </label>
                ))}
              </div>
              <div className="inline-actions">
                <button className="primary" type="submit">
                  {editingContractId ? "Atualizar contrato" : "Salvar contrato"}
                </button>
                {editingContractId ? (
                  <button type="button" className="secondary" onClick={resetContractEditor}>
                    Cancelar edição
                  </button>
                ) : null}
              </div>
            </form>
            <DataList
              items={contracts}
              searchableText={(contract) => `${contract.number} ${contract.notes || ""} ${contract.client_id} ${contract.plan_id}`}
              searchPlaceholder="Pesquisar contrato"
              filterOptions={[
                { value: "rascunho", label: "Rascunhos" },
                { value: "vigente", label: "Vigentes" },
                { value: "suspenso", label: "Suspensos" },
                { value: "encerrado", label: "Encerrados" },
              ]}
              filterPredicate={(contract, filterValue) => contract.status === filterValue}
              renderItem={(contract) => (
                <>
                  <div>
                    <strong>{contract.number}</strong>
                    <small>
                      Cliente #{contract.client_id} | Plano #{contract.plan_id} | {contract.status}
                    </small>
                  </div>
                  <div className="inline-actions">
                    <button type="button" className="secondary" onClick={() => editContract(contract)}>
                      Editar
                    </button>
                    <button type="button" className="secondary" onClick={() => duplicateContract(contract.id)}>
                      Duplicar
                    </button>
                    <button type="button" className="secondary" onClick={() => closeContract(contract.id)}>
                      Encerrar
                    </button>
                    <button type="button" onClick={() => removeItem("contract", contract.id)}>
                      Excluir
                    </button>
                  </div>
                </>
              )}
            />
          </Panel>

          <Panel title="Leituras" description="Lançamento manual inicial do faturamento">
            <form className="panel-form compact" onSubmit={createReading}>
              <Row>
                <Select
                  label="Contrato"
                  value={readingForm.contract_id}
                  onChange={(value) => {
                    const selected = contracts.find((contract) => String(contract.id) === value);
                    setReadingForm({ ...readingForm, contract_id: value, equipment_id: selected?.equipments?.[0] ? String(selected.equipments[0].equipment_id) : readingForm.equipment_id });
                  }}
                  options={contracts.map((contract) => ({ value: String(contract.id), label: `${contract.number} (#${contract.id})` }))}
                />
                <Select
                  label="Equipamento"
                  value={readingForm.equipment_id}
                  onChange={(value) => setReadingForm({ ...readingForm, equipment_id: value })}
                  options={equipment.map((item) => ({ value: String(item.id), label: `${item.brand} ${item.model} (#${item.id})` }))}
                />
              </Row>
              <Row>
                <Field label="Data de referência">
                  <input
                    type="date"
                    value={readingForm.reference_date}
                    onChange={(e) => setReadingForm({ ...readingForm, reference_date: e.target.value })}
                  />
                </Field>
                <Select
                  label="Origem"
                  value={readingForm.source}
                  onChange={(value) => setReadingForm({ ...readingForm, source: value as FonteLeitura })}
                  options={[
                    { value: "manual", label: "Manual" },
                    { value: "snmp", label: "SNMP" },
                    { value: "csv", label: "CSV" },
                    { value: "portal", label: "Portal" },
                  ]}
                />
              </Row>
              <Row>
                <Field label="Contador P&B atual">
                  <input
                    type="number"
                    value={readingForm.counter_pb_current}
                    onChange={(e) => setReadingForm({ ...readingForm, counter_pb_current: e.target.value })}
                  />
                </Field>
                <Field label="Contador P&B anterior">
                  <input
                    type="number"
                    value={readingForm.counter_pb_previous}
                    onChange={(e) => setReadingForm({ ...readingForm, counter_pb_previous: e.target.value })}
                  />
                </Field>
              </Row>
              <Row>
                <Field label="Contador Color atual">
                  <input
                    type="number"
                    value={readingForm.counter_color_current}
                    onChange={(e) => setReadingForm({ ...readingForm, counter_color_current: e.target.value })}
                  />
                </Field>
                <Field label="Contador Color anterior">
                  <input
                    type="number"
                    value={readingForm.counter_color_previous}
                    onChange={(e) => setReadingForm({ ...readingForm, counter_color_previous: e.target.value })}
                  />
                </Field>
              </Row>
              <Field label="Foto / link">
                <input value={readingForm.photo_url} onChange={(e) => setReadingForm({ ...readingForm, photo_url: e.target.value })} />
              </Field>
              <Field label="Observações">
                <textarea value={readingForm.notes} onChange={(e) => setReadingForm({ ...readingForm, notes: e.target.value })} />
              </Field>
              <label className="check-row">
                <input
                  type="checkbox"
                  checked={readingForm.validated}
                  onChange={(e) => setReadingForm({ ...readingForm, validated: e.target.checked })}
                />
                <span>Leitura validada</span>
              </label>
              <div className="inline-actions">
                <button className="primary" type="submit">
                  {editingReadingId ? "Atualizar leitura" : "Registrar leitura"}
                </button>
                {editingReadingId ? (
                  <button type="button" className="secondary" onClick={resetReadingEditor}>
                    Cancelar edição
                  </button>
                ) : null}
              </div>
            </form>
            <DataList
              items={readings}
              searchableText={(reading) => `${reading.id} ${reading.contract_id} ${reading.equipment_id} ${reading.reference_date} ${reading.source}`}
              searchPlaceholder="Pesquisar leitura"
              filterOptions={[
                { value: "manual", label: "Manuais" },
                { value: "snmp", label: "SNMP" },
                { value: "csv", label: "CSV" },
                { value: "portal", label: "Portal" },
              ]}
              filterPredicate={(reading, filterValue) => reading.source === filterValue}
              renderItem={(reading) => (
                <>
                  <div>
                    <strong>Leitura #{reading.id}</strong>
                    <small>
                      Contrato #{reading.contract_id} | Equipamento #{reading.equipment_id} | {reading.reference_date}
                    </small>
                  </div>
                  <div className="inline-actions">
                    <button type="button" className="secondary" onClick={() => editReading(reading)}>
                      Editar
                    </button>
                    <button type="button" onClick={() => removeItem("reading", reading.id)}>
                      Excluir
                    </button>
                  </div>
                </>
              )}
            />
          </Panel>
        </section>

        <section className="finance-section">
          <header className="section-head">
            <div>
              <span className="eyebrow">Fase 2</span>
              <h2>Financeiro</h2>
              <p>Contas a receber, contas a pagar, boletos, remessas, conciliação e inadimplência em um fluxo só.</p>
            </div>
          </header>

          <section className="metric-grid">
            <article className="metric-card">
              <span>Receber aberto</span>
              <strong>{currency(financeSummary?.receivable_open_total)}</strong>
            </article>
            <article className="metric-card">
              <span>Receber vencido</span>
              <strong>{currency(financeSummary?.receivable_overdue_total)}</strong>
            </article>
            <article className="metric-card">
              <span>Pagar aberto</span>
              <strong>{currency(financeSummary?.payable_open_total)}</strong>
            </article>
            <article className="metric-card">
              <span>Pagar vencido</span>
              <strong>{currency(financeSummary?.payable_overdue_total)}</strong>
            </article>
            <article className="metric-card">
              <span>Boletos</span>
              <strong>{financeSummary ? `${financeSummary.boletos_paid}/${financeSummary.boletos_open + financeSummary.boletos_paid}` : "-"}</strong>
            </article>
          </section>

          <section className="content-grid finance-grid">
            <Panel title="Gerar faturamento" description="Gera títulos e boletos por competência">
              <form className="panel-form compact" onSubmit={generateBilling}>
                <Row>
                  <Field label="Competência">
                    <input value={billingForm.competence} onChange={(e) => setBillingForm({ ...billingForm, competence: e.target.value })} />
                  </Field>
                  <Field label="Banco">
                    <input value={billingForm.bank_code} onChange={(e) => setBillingForm({ ...billingForm, bank_code: e.target.value })} />
                  </Field>
                </Row>
                <Row>
                  <Field label="Emissão">
                    <input type="date" value={billingForm.issue_date} onChange={(e) => setBillingForm({ ...billingForm, issue_date: e.target.value })} />
                  </Field>
                  <Field label="Vencimento">
                    <input type="date" value={billingForm.due_date} onChange={(e) => setBillingForm({ ...billingForm, due_date: e.target.value })} />
                  </Field>
                </Row>
                <Field label="Prefixo">
                  <input
                    value={billingForm.description_prefix}
                    onChange={(e) => setBillingForm({ ...billingForm, description_prefix: e.target.value })}
                  />
                </Field>
                <label className="check-row">
                  <input
                    type="checkbox"
                    checked={billingForm.generate_boleto}
                    onChange={(e) => setBillingForm({ ...billingForm, generate_boleto: e.target.checked })}
                  />
                  <span>Gerar boleto junto</span>
                </label>
                <button className="primary" type="submit">
                  Gerar faturamento
                </button>
              </form>
            </Panel>

            <Panel title="Contas a receber" description="Títulos emitidos contra contratos">
              <form className="panel-form compact" onSubmit={createReceivable}>
                <Row>
                  <Select
                    label="Contrato"
                    value={receivableForm.contract_id}
                    onChange={(value) => setReceivableForm({ ...receivableForm, contract_id: value })}
                    options={contracts.map((contract) => ({ value: String(contract.id), label: `${contract.number} (#${contract.id})` }))}
                  />
                  <Select
                    label="Cliente"
                    value={receivableForm.client_id}
                    onChange={(value) => setReceivableForm({ ...receivableForm, client_id: value })}
                    options={clients.map((client) => ({ value: String(client.id), label: `${client.name} (#${client.id})` }))}
                  />
                </Row>
                <Row>
                  <Field label="Emissão">
                    <input type="date" value={receivableForm.issue_date} onChange={(e) => setReceivableForm({ ...receivableForm, issue_date: e.target.value })} />
                  </Field>
                  <Field label="Vencimento">
                    <input type="date" value={receivableForm.due_date} onChange={(e) => setReceivableForm({ ...receivableForm, due_date: e.target.value })} />
                  </Field>
                </Row>
                <Row>
                  <Field label="Competência">
                    <input value={receivableForm.competence} onChange={(e) => setReceivableForm({ ...receivableForm, competence: e.target.value })} />
                  </Field>
                  <Field label="Valor">
                    <input type="number" step="0.01" value={receivableForm.original_amount} onChange={(e) => setReceivableForm({ ...receivableForm, original_amount: e.target.value })} />
                  </Field>
                </Row>
                <Field label="Descrição">
                  <input value={receivableForm.description} onChange={(e) => setReceivableForm({ ...receivableForm, description: e.target.value })} />
                </Field>
                <Field label="Observações">
                  <textarea value={receivableForm.notes} onChange={(e) => setReceivableForm({ ...receivableForm, notes: e.target.value })} />
                </Field>
                <div className="inline-actions">
                  <button className="primary" type="submit">
                    {editingReceivableId ? "Atualizar título" : "Salvar título"}
                  </button>
                  {editingReceivableId ? (
                    <button type="button" className="secondary" onClick={resetReceivableEditor}>
                      Cancelar edição
                    </button>
                  ) : null}
                </div>
              </form>
              <DataList
                items={receivables}
                searchableText={(item) => `${item.description} ${item.competence} ${item.due_date} ${item.status}`}
                searchPlaceholder="Pesquisar título"
                filterOptions={[
                  { value: "aberto", label: "Abertos" },
                  { value: "parcialmente_pago", label: "Parciais" },
                  { value: "pago", label: "Pagos" },
                  { value: "vencido", label: "Vencidos" },
                  { value: "cancelado", label: "Cancelados" },
                ]}
                filterPredicate={(item, filterValue) => item.status === filterValue}
                renderItem={(item) => (
                  <>
                    <div>
                      <strong>{item.description}</strong>
                      <small>
                        {item.competence} | {item.due_date} | {item.status} | {currency(item.original_amount)}
                      </small>
                    </div>
                    <div className="inline-actions">
                      <button className="secondary" type="button" onClick={() => editReceivable(item)}>Editar</button>
                      <button className="secondary" type="button" onClick={() => settleReceivable(item.id)}>Baixar</button>
                      <button type="button" onClick={() => removeItem("receivable", item.id)}>Excluir</button>
                    </div>
                  </>
                )}
              />
            </Panel>

            <Panel title="Contas a pagar" description="Despesas e obrigações operacionais">
              <form className="panel-form compact" onSubmit={createPayable}>
                <Row>
                  <Select
                    label="Contrato"
                    value={payableForm.contract_id}
                    onChange={(value) => setPayableForm({ ...payableForm, contract_id: value })}
                    options={[
                      { value: "", label: "Sem contrato" },
                      ...contracts.map((contract) => ({ value: String(contract.id), label: `${contract.number} (#${contract.id})` })),
                    ]}
                  />
                  <Field label="Categoria">
                    <input value={payableForm.category} onChange={(e) => setPayableForm({ ...payableForm, category: e.target.value })} />
                  </Field>
                </Row>
                <Row>
                  <Field label="Emissão">
                    <input type="date" value={payableForm.issue_date} onChange={(e) => setPayableForm({ ...payableForm, issue_date: e.target.value })} />
                  </Field>
                  <Field label="Vencimento">
                    <input type="date" value={payableForm.due_date} onChange={(e) => setPayableForm({ ...payableForm, due_date: e.target.value })} />
                  </Field>
                </Row>
                <Row>
                  <Field label="Fornecedor">
                    <input value={payableForm.supplier_name} onChange={(e) => setPayableForm({ ...payableForm, supplier_name: e.target.value })} />
                  </Field>
                  <Field label="Valor">
                    <input type="number" step="0.01" value={payableForm.original_amount} onChange={(e) => setPayableForm({ ...payableForm, original_amount: e.target.value })} />
                  </Field>
                </Row>
                <Field label="Descrição">
                  <input value={payableForm.description} onChange={(e) => setPayableForm({ ...payableForm, description: e.target.value })} />
                </Field>
                <Field label="Observações">
                  <textarea value={payableForm.notes} onChange={(e) => setPayableForm({ ...payableForm, notes: e.target.value })} />
                </Field>
                <div className="inline-actions">
                  <button className="primary" type="submit">
                    {editingPayableId ? "Atualizar conta" : "Salvar conta"}
                  </button>
                  {editingPayableId ? (
                    <button type="button" className="secondary" onClick={resetPayableEditor}>
                      Cancelar edição
                    </button>
                  ) : null}
                </div>
              </form>
              <DataList
                items={payables}
                searchableText={(item) => `${item.description} ${item.category} ${item.supplier_name || ""} ${item.status}`}
                searchPlaceholder="Pesquisar conta"
                filterOptions={[
                  { value: "aberto", label: "Abertas" },
                  { value: "parcialmente_pago", label: "Parciais" },
                  { value: "pago", label: "Pagas" },
                  { value: "vencido", label: "Vencidas" },
                  { value: "cancelado", label: "Canceladas" },
                ]}
                filterPredicate={(item, filterValue) => item.status === filterValue}
                renderItem={(item) => (
                  <>
                    <div>
                      <strong>{item.description}</strong>
                      <small>
                        {item.category} | {item.due_date} | {item.status} | {currency(item.original_amount)}
                      </small>
                    </div>
                    <div className="inline-actions">
                      <button className="secondary" type="button" onClick={() => editPayable(item)}>Editar</button>
                      <button className="secondary" type="button" onClick={() => settlePayable(item.id)}>Baixar</button>
                      <button type="button" onClick={() => removeItem("payable", item.id)}>Excluir</button>
                    </div>
                  </>
                )}
              />
            </Panel>

            <Panel title="Boletos" description="Emissão e operação de cobrança">
              <form className="panel-form compact" onSubmit={createBoleto}>
                <Row>
                  <Select
                    label="Conta a receber"
                    value={boletoForm.receivable_id}
                    onChange={(value) => setBoletoForm({ ...boletoForm, receivable_id: value, payable_id: "" })}
                    options={[
                      { value: "", label: "Nenhuma" },
                      ...receivables.map((item) => ({ value: String(item.id), label: `${item.description} (#${item.id})` })),
                    ]}
                  />
                  <Select
                    label="Conta a pagar"
                    value={boletoForm.payable_id}
                    onChange={(value) => setBoletoForm({ ...boletoForm, payable_id: value, receivable_id: "" })}
                    options={[
                      { value: "", label: "Nenhuma" },
                      ...payables.map((item) => ({ value: String(item.id), label: `${item.description} (#${item.id})` })),
                    ]}
                  />
                </Row>
                <Row>
                  <Field label="Banco">
                    <input value={boletoForm.bank_code} onChange={(e) => setBoletoForm({ ...boletoForm, bank_code: e.target.value })} />
                  </Field>
                  <Field label="Vencimento">
                    <input type="date" value={boletoForm.due_date} onChange={(e) => setBoletoForm({ ...boletoForm, due_date: e.target.value })} />
                  </Field>
                </Row>
                <Field label="Valor">
                  <input type="number" step="0.01" value={boletoForm.amount} onChange={(e) => setBoletoForm({ ...boletoForm, amount: e.target.value })} />
                </Field>
                <button className="primary" type="submit">Salvar boleto</button>
              </form>
              <DataList
                items={boletos}
                searchableText={(item) => `${item.nosso_numero} ${item.barcode || ""} ${item.bank_code} ${item.status}`}
                searchPlaceholder="Pesquisar boleto"
                filterOptions={[
                  { value: "gerado", label: "Gerados" },
                  { value: "enviado", label: "Enviados" },
                  { value: "registrado", label: "Registrados" },
                  { value: "pago", label: "Pagos" },
                  { value: "vencido", label: "Vencidos" },
                  { value: "cancelado", label: "Cancelados" },
                  { value: "rejeitado", label: "Rejeitados" },
                ]}
                filterPredicate={(item, filterValue) => item.status === filterValue}
                renderItem={(item) => (
                  <>
                    <div>
                      <strong>{item.nosso_numero}</strong>
                      <small>
                        {item.bank_code} | {item.due_date} | {item.status} | {currency(item.amount)}
                      </small>
                    </div>
                    <div className="inline-actions">
                      <button className="secondary" type="button" onClick={() => sendBoleto(item.id)}>Enviar</button>
                      <button className="secondary" type="button" onClick={() => settleBoleto(item.id)}>Baixar</button>
                      <button type="button" onClick={() => removeItem("boleto", item.id)}>Excluir</button>
                    </div>
                  </>
                )}
              />
            </Panel>

            <Panel title="Remessas" description="Lote CNAB ou envio bancário">
              <form className="panel-form compact" onSubmit={createRemittance}>
                <Row>
                  <Field label="Banco">
                    <input value={remittanceForm.bank_code} onChange={(e) => setRemittanceForm({ ...remittanceForm, bank_code: e.target.value })} />
                  </Field>
                  <Field label="Tipo de arquivo">
                    <input value={remittanceForm.file_type} onChange={(e) => setRemittanceForm({ ...remittanceForm, file_type: e.target.value })} />
                  </Field>
                </Row>
                <Field label="Nome do arquivo">
                  <input value={remittanceForm.file_name} onChange={(e) => setRemittanceForm({ ...remittanceForm, file_name: e.target.value })} />
                </Field>
                <div className="choice-list">
                  {boletos.filter((item) => item.status !== "pago").map((item) => (
                    <label key={item.id} className="choice-item">
                      <input
                        type="checkbox"
                        checked={remittanceSelection.includes(String(item.id))}
                        onChange={(e) => {
                          const id = String(item.id);
                          setRemittanceSelection((current) =>
                            e.target.checked ? [...current, id] : current.filter((value) => value !== id),
                          );
                        }}
                      />
                      <span>{item.nosso_numero} | {currency(item.amount)}</span>
                    </label>
                  ))}
                </div>
                <button className="primary" type="submit">Criar remessa</button>
              </form>
              <DataList
                items={remittances}
                searchableText={(item) => `${item.file_name} ${item.bank_code} ${item.status}`}
                searchPlaceholder="Pesquisar remessa"
                filterOptions={[
                  { value: "criada", label: "Criadas" },
                  { value: "enviada", label: "Enviadas" },
                  { value: "processada", label: "Processadas" },
                  { value: "falha", label: "Com falha" },
                ]}
                filterPredicate={(item, filterValue) => item.status === filterValue}
                renderItem={(item) => (
                  <>
                    <div>
                      <strong>{item.file_name}</strong>
                      <small>
                        {item.bank_code} | {item.status} | {currency(item.total_amount)}
                      </small>
                    </div>
                    <span>{item.total_titles} títulos</span>
                  </>
                )}
              />
            </Panel>

            <Panel title="Conciliação" description="Importação automática de extrato bancário">
              <form className="panel-form compact" onSubmit={importBankEntries}>
                <Row>
                  <Field label="Data">
                    <input
                      type="date"
                      value={bankEntryForm.statement_date}
                      onChange={(e) => setBankEntryForm({ ...bankEntryForm, statement_date: e.target.value })}
                    />
                  </Field>
                  <Field label="Valor">
                    <input type="number" step="0.01" value={bankEntryForm.amount} onChange={(e) => setBankEntryForm({ ...bankEntryForm, amount: e.target.value })} />
                  </Field>
                </Row>
                <Field label="Descrição">
                  <input value={bankEntryForm.description} onChange={(e) => setBankEntryForm({ ...bankEntryForm, description: e.target.value })} />
                </Field>
                <Field label="Referência">
                  <input value={bankEntryForm.reference} onChange={(e) => setBankEntryForm({ ...bankEntryForm, reference: e.target.value })} />
                </Field>
                <Field label="Observações">
                  <textarea value={bankEntryForm.notes} onChange={(e) => setBankEntryForm({ ...bankEntryForm, notes: e.target.value })} />
                </Field>
                <button className="primary" type="submit">Importar conciliação</button>
              </form>
              <DataList
                items={reconciliationEntries}
                searchableText={(item) => `${item.description} ${item.reference || ""} ${item.source} ${item.status}`}
                searchPlaceholder="Pesquisar lançamento"
                filterOptions={[
                  { value: "pendente", label: "Pendentes" },
                  { value: "casado", label: "Casados" },
                  { value: "ignorado", label: "Ignorados" },
                ]}
                filterPredicate={(item, filterValue) => item.status === filterValue}
                renderItem={(item) => (
                  <>
                    <div>
                      <strong>{item.description}</strong>
                      <small>
                        {item.statement_date} | {item.status} | {currency(item.amount)}
                      </small>
                    </div>
                    <span>{item.reference || "sem ref."}</span>
                  </>
                )}
              />
            </Panel>

            <Panel title="Aging" description="Mapa de inadimplência por faixa">
              {agingReport ? (
                <div className="aging-grid">
                  <div className="aging-block">
                    <h4>Receber</h4>
                    {agingReport.receivable_buckets.map((bucket) => (
                      <div className="aging-row" key={bucket.label}>
                        <span>{bucket.label}</span>
                        <strong>
                          {bucket.count} | {currency(bucket.total)}
                        </strong>
                      </div>
                    ))}
                  </div>
                  <div className="aging-block">
                    <h4>Pagar</h4>
                    {agingReport.payable_buckets.map((bucket) => (
                      <div className="aging-row" key={bucket.label}>
                        <span>{bucket.label}</span>
                        <strong>
                          {bucket.count} | {currency(bucket.total)}
                        </strong>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="empty-state">Sem dados de aging ainda.</div>
              )}
            </Panel>
          </section>
        </section>

        <section className="fiscal-section">
          <header className="section-head">
            <div>
              <span className="eyebrow">Fase 3</span>
              <h2>Fiscal</h2>
              <p>Configuração fiscal do tenant, emissão de documentos, autorização simulada e histórico de envios.</p>
            </div>
          </header>

          <section className="metric-grid">
            <article className="metric-card">
              <span>Total de documentos</span>
              <strong>{fiscalSummary ? fiscalSummary.total_documents : "-"}</strong>
            </article>
            <article className="metric-card">
              <span>Rascunhos</span>
              <strong>{fiscalSummary ? fiscalSummary.draft_documents : "-"}</strong>
            </article>
            <article className="metric-card">
              <span>Autorizados</span>
              <strong>{fiscalSummary ? fiscalSummary.authorized_documents : "-"}</strong>
            </article>
            <article className="metric-card">
              <span>Cancelados</span>
              <strong>{fiscalSummary ? fiscalSummary.cancelled_documents : "-"}</strong>
            </article>
            <article className="metric-card">
              <span>Valor total</span>
              <strong>{currency(fiscalSummary?.total_amount)}</strong>
            </article>
          </section>

          <section className="content-grid finance-grid">
            <Panel title="Configuração fiscal" description="Cadastro da base tributária do tenant">
              <form className="panel-form compact" onSubmit={saveFiscalConfig}>
                <Field label="Razão social">
                  <input
                    value={fiscalConfigForm.company_name}
                    onChange={(e) => setFiscalConfigForm({ ...fiscalConfigForm, company_name: e.target.value })}
                  />
                </Field>
                <Row>
                  <Field label="CNPJ">
                    <input
                      value={fiscalConfigForm.cnpj}
                      onChange={(e) => setFiscalConfigForm({ ...fiscalConfigForm, cnpj: e.target.value })}
                    />
                  </Field>
                  <Select
                    label="Regime"
                    value={fiscalConfigForm.regime_tributario}
                    onChange={(value) => setFiscalConfigForm({ ...fiscalConfigForm, regime_tributario: value as RegimeTributario })}
                    options={[
                      { value: "simples_nacional", label: "Simples Nacional" },
                      { value: "lucro_presumido", label: "Lucro Presumido" },
                      { value: "lucro_real", label: "Lucro Real" },
                      { value: "mei", label: "MEI" },
                      { value: "outro", label: "Outro" },
                    ]}
                  />
                </Row>
                <Row>
                  <Field label="Inscrição estadual">
                    <input
                      value={fiscalConfigForm.inscricao_estadual}
                      onChange={(e) => setFiscalConfigForm({ ...fiscalConfigForm, inscricao_estadual: e.target.value })}
                    />
                  </Field>
                  <Field label="Inscrição municipal">
                    <input
                      value={fiscalConfigForm.inscricao_municipal}
                      onChange={(e) => setFiscalConfigForm({ ...fiscalConfigForm, inscricao_municipal: e.target.value })}
                    />
                  </Field>
                </Row>
                <Row>
                  <Field label="Série NFe">
                    <input
                      type="number"
                      value={fiscalConfigForm.serie_nfe}
                      onChange={(e) => setFiscalConfigForm({ ...fiscalConfigForm, serie_nfe: e.target.value })}
                    />
                  </Field>
                  <Field label="Série NFS-e">
                    <input
                      type="number"
                      value={fiscalConfigForm.serie_nfse}
                      onChange={(e) => setFiscalConfigForm({ ...fiscalConfigForm, serie_nfse: e.target.value })}
                    />
                  </Field>
                </Row>
                <Row>
                  <Field label="ISS (%)">
                    <input
                      type="number"
                      step="0.01"
                      value={fiscalConfigForm.iss_rate}
                      onChange={(e) => setFiscalConfigForm({ ...fiscalConfigForm, iss_rate: e.target.value })}
                    />
                  </Field>
                  <div className="stacked-checkboxes">
                    <label className="check-row">
                      <input
                        type="checkbox"
                        checked={fiscalConfigForm.nfe_enabled}
                        onChange={(e) => setFiscalConfigForm({ ...fiscalConfigForm, nfe_enabled: e.target.checked })}
                      />
                      <span>NFe habilitada</span>
                    </label>
                    <label className="check-row">
                      <input
                        type="checkbox"
                        checked={fiscalConfigForm.nfse_enabled}
                        onChange={(e) => setFiscalConfigForm({ ...fiscalConfigForm, nfse_enabled: e.target.checked })}
                      />
                      <span>NFS-e habilitada</span>
                    </label>
                  </div>
                </Row>
                <Field label="Observações">
                  <textarea
                    value={fiscalConfigForm.notes}
                    onChange={(e) => setFiscalConfigForm({ ...fiscalConfigForm, notes: e.target.value })}
                  />
                </Field>
                <button className="primary" type="submit">
                  Salvar configuração fiscal
                </button>
              </form>
            </Panel>

            <Panel title="Emissão fiscal" description="Emissão de NFe/NFS-e a partir de conta, contrato ou manual">
              <form className="panel-form compact" onSubmit={saveFiscalDocument}>
                <Row>
                  <Select
                    label="Tipo"
                    value={fiscalDocumentForm.document_type}
                    onChange={(value) => setFiscalDocumentForm({ ...fiscalDocumentForm, document_type: value as TipoDocumentoFiscal })}
                    options={[
                      { value: "nfse", label: "NFS-e" },
                      { value: "nfe", label: "NFe" },
                    ]}
                  />
                  <Select
                    label="Origem"
                    value={fiscalDocumentForm.origin}
                    onChange={(value) => setFiscalDocumentForm({ ...fiscalDocumentForm, origin: value as OrigemDocumentoFiscal })}
                    options={[
                      { value: "manual", label: "Manual" },
                      { value: "receivable", label: "Conta a receber" },
                      { value: "contract", label: "Contrato" },
                      { value: "batch", label: "Lote" },
                    ]}
                  />
                </Row>
                <Row>
                  <Select
                    label="Conta a receber"
                    value={fiscalDocumentForm.receivable_id}
                    onChange={(value) => setFiscalDocumentForm({ ...fiscalDocumentForm, receivable_id: value })}
                    options={[
                      { value: "", label: "Nenhuma" },
                      ...receivables.map((item) => ({ value: String(item.id), label: `${item.description} (#${item.id})` })),
                    ]}
                  />
                  <Select
                    label="Contrato"
                    value={fiscalDocumentForm.contract_id}
                    onChange={(value) => setFiscalDocumentForm({ ...fiscalDocumentForm, contract_id: value })}
                    options={[
                      { value: "", label: "Nenhum" },
                      ...contracts.map((item) => ({ value: String(item.id), label: `${item.number} (#${item.id})` })),
                    ]}
                  />
                </Row>
                <Row>
                  <Select
                    label="Cliente"
                    value={fiscalDocumentForm.client_id}
                    onChange={(value) => setFiscalDocumentForm({ ...fiscalDocumentForm, client_id: value })}
                    options={[
                      { value: "", label: "Nenhum" },
                      ...clients.map((item) => ({ value: String(item.id), label: `${item.name} (#${item.id})` })),
                    ]}
                  />
                  <Field label="Série">
                    <input
                      type="number"
                      value={fiscalDocumentForm.series}
                      onChange={(e) => setFiscalDocumentForm({ ...fiscalDocumentForm, series: e.target.value })}
                    />
                  </Field>
                </Row>
                <Row>
                  <Field label="Emissão">
                    <input
                      type="date"
                      value={fiscalDocumentForm.issue_date}
                      onChange={(e) => setFiscalDocumentForm({ ...fiscalDocumentForm, issue_date: e.target.value })}
                    />
                  </Field>
                  <Field label="Competência">
                    <input
                      value={fiscalDocumentForm.competence}
                      onChange={(e) => setFiscalDocumentForm({ ...fiscalDocumentForm, competence: e.target.value })}
                    />
                  </Field>
                </Row>
                <Row>
                  <Field label="Nome do destinatário">
                    <input
                      value={fiscalDocumentForm.recipient_name}
                      onChange={(e) => setFiscalDocumentForm({ ...fiscalDocumentForm, recipient_name: e.target.value })}
                    />
                  </Field>
                  <Field label="Documento do destinatário">
                    <input
                      value={fiscalDocumentForm.recipient_document}
                      onChange={(e) => setFiscalDocumentForm({ ...fiscalDocumentForm, recipient_document: e.target.value })}
                    />
                  </Field>
                </Row>
                <Field label="Descrição">
                  <input
                    value={fiscalDocumentForm.description}
                    onChange={(e) => setFiscalDocumentForm({ ...fiscalDocumentForm, description: e.target.value })}
                  />
                </Field>
                <Row>
                  <Field label="Valor">
                    <input
                      type="number"
                      step="0.01"
                      value={fiscalDocumentForm.amount}
                      onChange={(e) => setFiscalDocumentForm({ ...fiscalDocumentForm, amount: e.target.value })}
                    />
                  </Field>
                  <Field label="Base de cálculo">
                    <input
                      type="number"
                      step="0.01"
                      value={fiscalDocumentForm.tax_base}
                      onChange={(e) => setFiscalDocumentForm({ ...fiscalDocumentForm, tax_base: e.target.value })}
                    />
                  </Field>
                </Row>
                <Row>
                  <Field label="Alíquota">
                    <input
                      type="number"
                      step="0.01"
                      value={fiscalDocumentForm.tax_rate}
                      onChange={(e) => setFiscalDocumentForm({ ...fiscalDocumentForm, tax_rate: e.target.value })}
                    />
                  </Field>
                  <Field label="Imposto">
                    <input
                      type="number"
                      step="0.01"
                      value={fiscalDocumentForm.tax_amount}
                      onChange={(e) => setFiscalDocumentForm({ ...fiscalDocumentForm, tax_amount: e.target.value })}
                    />
                  </Field>
                </Row>
                <Field label="Observações">
                  <textarea
                    value={fiscalDocumentForm.notes}
                    onChange={(e) => setFiscalDocumentForm({ ...fiscalDocumentForm, notes: e.target.value })}
                  />
                </Field>
                <label className="check-row">
                  <input
                    type="checkbox"
                    checked={fiscalDocumentForm.authorize}
                    onChange={(e) => setFiscalDocumentForm({ ...fiscalDocumentForm, authorize: e.target.checked })}
                  />
                  <span>Autorizar imediatamente</span>
                </label>
                <div className="inline-actions">
                  <button className="primary" type="submit">
                    {editingFiscalDocumentId ? "Atualizar documento" : "Emitir documento"}
                  </button>
                  {editingFiscalDocumentId ? (
                    <button type="button" className="secondary" onClick={resetFiscalDocumentEditor}>
                      Cancelar edição
                    </button>
                  ) : null}
                </div>
              </form>
            </Panel>

            <Panel title="Lote fiscal" description="Seleciona contas a receber para emissão em massa">
              <form className="panel-form compact" onSubmit={batchIssueFiscalDocuments}>
                <div className="choice-list">
                  {receivables.map((item) => (
                    <label key={item.id} className="choice-item">
                      <input
                        type="checkbox"
                        checked={fiscalBatchReceivables.includes(String(item.id))}
                        onChange={(e) => {
                          const id = String(item.id);
                          setFiscalBatchReceivables((current) =>
                            e.target.checked ? [...current, id] : current.filter((value) => value !== id),
                          );
                        }}
                      />
                      <span>{item.description} | {currency(item.original_amount)}</span>
                    </label>
                  ))}
                </div>
                <div className="inline-actions">
                  <button className="primary" type="submit" disabled={fiscalBatchReceivables.length === 0}>
                    Gerar em lote
                  </button>
                  <button type="button" className="secondary" onClick={() => setFiscalBatchReceivables([])}>
                    Limpar seleção
                  </button>
                </div>
              </form>
            </Panel>

            <Panel title="Documentos fiscais" description="Histórico de emissão, autorização e cancelamento">
              <DataList
                items={fiscalDocuments}
                searchableText={(item) => `${item.recipient_name} ${item.number}/${item.series} ${item.document_type} ${item.status}`}
                searchPlaceholder="Pesquisar documento"
                filterOptions={[
                  { value: "rascunho", label: "Rascunhos" },
                  { value: "autorizado", label: "Autorizados" },
                  { value: "cancelado", label: "Cancelados" },
                  { value: "rejeitado", label: "Rejeitados" },
                ]}
                filterPredicate={(item, filterValue) => item.status === filterValue}
                renderItem={(item) => (
                  <>
                    <div>
                      <strong>{item.document_type.toUpperCase()} {item.number}/{item.series}</strong>
                      <small>
                        {item.recipient_name} | {item.competence} | {item.status} | {currency(item.amount)}
                      </small>
                    </div>
                    <div className="inline-actions">
                      <button type="button" className="secondary" onClick={() => editFiscalDocument(item)}>
                        Editar
                      </button>
                      <button type="button" className="secondary" onClick={() => authorizeFiscalDocument(item.id)}>
                        Autorizar
                      </button>
                      <button type="button" className="secondary" onClick={() => cancelFiscalDocument(item.id)}>
                        Cancelar
                      </button>
                      <button type="button" onClick={() => removeFiscalDocument(item.id)}>
                        Excluir
                      </button>
                    </div>
                  </>
                )}
              />
            </Panel>
          </section>
        </section>
      </main>
    </div>
  );
}

function Panel({ title, description, children }: { title: string; description: string; children: ReactNode }) {
  return (
    <section className="panel">
      <div className="panel-head">
        <div>
          <h3>{title}</h3>
          <p>{description}</p>
        </div>
      </div>
      {children}
    </section>
  );
}

function DataList<T extends { id: number }>({
  items,
  renderItem,
  searchableText,
  searchPlaceholder = "Pesquisar",
  filterOptions,
  filterPredicate,
  emptyText = "Nenhum registro ainda.",
}: {
  items: T[];
  renderItem: (item: T) => ReactNode;
  searchableText?: (item: T) => string;
  searchPlaceholder?: string;
  filterOptions?: Array<{ value: string; label: string }>;
  filterPredicate?: (item: T, filterValue: string) => boolean;
  emptyText?: string;
}) {
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(5);
  const [filterValue, setFilterValue] = useState(filterOptions?.[0]?.value ?? "all");
  const filterSignature = useMemo(() => (filterOptions ?? []).map((option) => option.value).join("|"), [filterOptions]);

  useEffect(() => {
    setFilterValue(filterOptions?.[0]?.value ?? "all");
  }, [filterSignature]);

  const filteredItems = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return items.filter((item) => {
      const searchMatch =
        !searchableText || !normalizedQuery || searchableText(item).toLowerCase().includes(normalizedQuery);
      const filterMatch = !filterPredicate || !filterOptions || filterValue === "all" || filterPredicate(item, filterValue);
      return searchMatch && filterMatch;
    });
  }, [filterOptions, filterPredicate, filterValue, items, query, searchableText]);

  useEffect(() => {
    setPage(1);
  }, [query, filterValue, pageSize, items.length]);

  const totalPages = Math.max(1, Math.ceil(filteredItems.length / pageSize));
  const currentPage = Math.min(page, totalPages);
  const start = (currentPage - 1) * pageSize;
  const pageItems = filteredItems.slice(start, start + pageSize);

  if (items.length === 0) {
    return <div className="empty-state">{emptyText}</div>;
  }

  return (
    <div className="list-shell">
      {searchableText || filterOptions ? (
        <div className="list-toolbar">
          <input
            placeholder={searchPlaceholder}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          {filterOptions ? (
            <select value={filterValue} onChange={(event) => setFilterValue(event.target.value)}>
              <option value="all">Todos</option>
              {filterOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          ) : null}
          <select value={pageSize} onChange={(event) => setPageSize(Number(event.target.value))}>
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={25}>25</option>
          </select>
        </div>
      ) : null}

      {filteredItems.length === 0 ? (
        <div className="empty-state">Nenhum resultado encontrado.</div>
      ) : (
        <div className="data-list">
          {pageItems.map((item) => (
            <div className="data-row" key={item.id}>
              {renderItem(item)}
            </div>
          ))}
        </div>
      )}

      {filteredItems.length > pageSize ? (
        <div className="pagination">
          <span>
            Mostrando {start + 1}-{Math.min(start + pageSize, filteredItems.length)} de {filteredItems.length}
          </span>
          <div className="pagination-actions">
            <button type="button" className="secondary" onClick={() => setPage((current) => Math.max(1, current - 1))} disabled={currentPage === 1}>
              Anterior
            </button>
            <button
              type="button"
              className="secondary"
              onClick={() => setPage((current) => Math.min(totalPages, current + 1))}
              disabled={currentPage === totalPages}
            >
              Próxima
            </button>
          </div>
        </div>
      ) : null}
    </div>
  );
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="field">
      <span>{label}</span>
      {children}
    </label>
  );
}

function Select({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: Array<{ value: string; label: string }>;
}) {
  return (
    <label className="field">
      <span>{label}</span>
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        <option value="">Selecione</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}

function Row({ children }: { children: ReactNode }) {
  return <div className="row">{children}</div>;
}

export default App;
