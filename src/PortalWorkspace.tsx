import { type FormEvent, type ReactNode, useEffect, useMemo, useState } from "react";
import { api } from "./api";
import type {
  Boleto,
  Client,
  Contract,
  Equipment,
  PortalReadingCreate,
  PortalReport,
  PortalSummary,
  PortalTicket,
  PortalTicketCreate,
  Reading,
} from "./types";

type PortalWorkspaceProps = {
  token: string;
  onLogout: () => void;
};

const today = new Date().toISOString().slice(0, 10);

const emptyReadingForm = {
  contract_id: "",
  equipment_id: "",
  reference_date: today,
  counter_pb_current: "",
  counter_pb_previous: "0",
  counter_color_current: "",
  counter_color_previous: "0",
  notes: "",
};

const emptyTicketForm = {
  subject: "",
  description: "",
  contract_id: "",
  equipment_id: "",
  priority: "media" as PortalTicketCreate["priority"],
};

function currency(value: number | null | undefined) {
  if (value === null || value === undefined) return "-";
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(value);
}

function formatDate(value: string | null | undefined) {
  if (!value) return "-";
  return value.slice(0, 10);
}

function PortalWorkspace({ token, onLogout }: PortalWorkspaceProps) {
  const [client, setClient] = useState<Client | null>(null);
  const [summary, setSummary] = useState<PortalSummary | null>(null);
  const [report, setReport] = useState<PortalReport | null>(null);
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [readings, setReadings] = useState<Reading[]>([]);
  const [boletos, setBoletos] = useState<Boleto[]>([]);
  const [tickets, setTickets] = useState<PortalTicket[]>([]);
  const [readingForm, setReadingForm] = useState(emptyReadingForm);
  const [ticketForm, setTicketForm] = useState(emptyTicketForm);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void loadPortalData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  async function loadPortalData() {
    setLoading(true);
    try {
      const [clientData, summaryData, reportData, contractsData, equipmentData, readingsData, boletosData, ticketsData] =
        await Promise.all([
          api.portalMe(token),
          api.portalSummary(token),
          api.portalReport(token),
          api.portalContracts(token),
          api.portalEquipments(token),
          api.portalReadings(token),
          api.portalBoletos(token),
          api.portalTickets(token),
        ]);

      setClient(clientData);
      setSummary(summaryData);
      setReport(reportData);
      setContracts(contractsData);
      setEquipment(equipmentData);
      setReadings(readingsData);
      setBoletos(boletosData);
      setTickets(ticketsData);

      setReadingForm((current) => ({
        ...current,
        contract_id: current.contract_id || String(contractsData[0]?.id ?? ""),
        equipment_id: current.equipment_id || String(equipmentData[0]?.id ?? ""),
      }));
      setTicketForm((current) => ({
        ...current,
        contract_id: current.contract_id || String(contractsData[0]?.id ?? ""),
        equipment_id: current.equipment_id || String(equipmentData[0]?.id ?? ""),
      }));
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao carregar portal");
      const errorText = error instanceof Error ? error.message : "";
      if (errorText.includes("Nao autenticado") || errorText.includes("Cliente portal invalido")) {
        onLogout();
      }
    } finally {
      setLoading(false);
    }
  }

  async function submitReading(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      const payload: PortalReadingCreate = {
        contract_id: Number(readingForm.contract_id),
        equipment_id: Number(readingForm.equipment_id),
        reference_date: readingForm.reference_date,
        counter_pb_current: Number(readingForm.counter_pb_current),
        counter_pb_previous: Number(readingForm.counter_pb_previous),
        counter_color_current: Number(readingForm.counter_color_current),
        counter_color_previous: Number(readingForm.counter_color_previous),
        notes: readingForm.notes || null,
      };
      await api.portalCreateReading(token, payload);
      setReadingForm(emptyReadingForm);
      await loadPortalData();
      setMessage("Leitura enviada com sucesso.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao enviar leitura");
    } finally {
      setBusy(false);
    }
  }

  async function submitTicket(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      const payload: PortalTicketCreate = {
        subject: ticketForm.subject,
        description: ticketForm.description,
        contract_id: ticketForm.contract_id ? Number(ticketForm.contract_id) : null,
        equipment_id: ticketForm.equipment_id ? Number(ticketForm.equipment_id) : null,
        priority: ticketForm.priority,
      };
      await api.portalCreateTicket(token, payload);
      setTicketForm(emptyTicketForm);
      await loadPortalData();
      setMessage("Chamado aberto com sucesso.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao abrir chamado");
    } finally {
      setBusy(false);
    }
  }

  async function downloadBoleto(boleto: Boleto) {
    setBusy(true);
    setMessage("");
    try {
      const response = await api.portalDownloadBoleto(token, boleto.id);
      if (response.download_url) {
        window.open(response.download_url, "_blank", "noopener,noreferrer");
        setMessage("Download do boleto aberto em nova aba.");
      } else if (response.barcode) {
        setMessage(`Linha digitavel: ${response.barcode}`);
      } else {
        setMessage("Boleto sem arquivo disponível no momento.");
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha ao baixar boleto");
    } finally {
      setBusy(false);
    }
  }

  const cards = useMemo(
    () => [
      { label: "Contratos", value: summary?.contracts ?? 0 },
      { label: "Equipamentos", value: summary?.equipments ?? 0 },
      { label: "Leituras", value: summary?.readings ?? 0 },
      { label: "Boletos abertos", value: summary?.boletos_open ?? 0 },
      { label: "Chamados abertos", value: summary?.tickets_open ?? 0 },
    ],
    [summary],
  );

  if (loading) {
    return (
      <div className="portal-shell">
        <div className="portal-loading">
          <div className="brand-mark">PM</div>
          <h1>Carregando portal</h1>
          <p>Estamos montando a visão do cliente com contratos, leituras e boletos.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="portal-shell">
      <aside className="portal-sidebar">
        <div>
          <div className="brand-mark">PM</div>
          <h1>Portal do cliente</h1>
          <p>Visão operacional de contratos, impressoras, leituras e cobranças.</p>
        </div>

        <div className="sidebar-block">
          <span className="sidebar-label">Cliente</span>
          <strong>{client?.name || "Cliente"}</strong>
          <small>{client?.document || "-"}</small>
        </div>

        <div className="sidebar-block">
          <span className="sidebar-label">Última leitura</span>
          <strong>{summary?.last_reading_at ? formatDate(summary.last_reading_at) : "-"}</strong>
          <small>{report?.total_due ? currency(report.total_due) : "Sem pendências"}</small>
        </div>

        <button className="ghost" onClick={onLogout}>
          Sair do portal
        </button>
      </aside>

      <main className="portal-workspace">
        <header className="workspace-header">
          <div>
            <span className="eyebrow">Portal</span>
            <h2>Visão do cliente em tempo real.</h2>
            <p>Contratos, equipamentos, leituras, boletos, relatórios e chamados em um fluxo simples.</p>
          </div>
          <div className="header-message">{busy ? "Processando..." : message || "Tudo pronto para consulta."}</div>
        </header>

        <section className="metric-grid">
          {cards.map((card) => (
            <article key={card.label} className="metric-card">
              <span>{card.label}</span>
              <strong>{card.value}</strong>
            </article>
          ))}
        </section>

        <section className="portal-grid">
          <PortalPanel title="Resumo financeiro" description="Posição consolidada do cliente">
            <div className="portal-summary">
              <div className="portal-summary-row">
                <span>Contratos</span>
                <strong>{report?.contracts ?? 0}</strong>
              </div>
              <div className="portal-summary-row">
                <span>Leituras</span>
                <strong>{report?.readings ?? 0}</strong>
              </div>
              <div className="portal-summary-row">
                <span>Chamados abertos</span>
                <strong>{report?.tickets_open ?? 0}</strong>
              </div>
              <div className="portal-summary-row">
                <span>Boletos abertos</span>
                <strong>{report?.boletos_open ?? 0}</strong>
              </div>
              <div className="portal-summary-row">
                <span>Total em aberto</span>
                <strong>{currency(report?.total_due)}</strong>
              </div>
            </div>
          </PortalPanel>

          <PortalPanel title="Enviar leitura" description="Leitura manual pelo portal">
            {contracts.length === 0 || equipment.length === 0 ? (
              <div className="empty-state">Não há contratos ou equipamentos vinculados ao cliente.</div>
            ) : (
              <form className="panel-form compact" onSubmit={submitReading}>
                <Row>
                  <Field label="Contrato">
                    <select
                      value={readingForm.contract_id}
                      onChange={(event) =>
                        setReadingForm({
                          ...readingForm,
                          contract_id: event.target.value,
                          equipment_id: readingForm.equipment_id || String(equipment[0]?.id ?? ""),
                        })
                      }
                    >
                      <option value="">Selecione</option>
                      {contracts.map((contract) => (
                        <option key={contract.id} value={contract.id}>
                          {contract.number}
                        </option>
                      ))}
                    </select>
                  </Field>
                  <Field label="Equipamento">
                    <select
                      value={readingForm.equipment_id}
                      onChange={(event) => setReadingForm({ ...readingForm, equipment_id: event.target.value })}
                    >
                      <option value="">Selecione</option>
                      {equipment.map((item) => (
                        <option key={item.id} value={item.id}>
                          {item.brand} {item.model}
                        </option>
                      ))}
                    </select>
                  </Field>
                </Row>
                <Row>
                  <Field label="Referência">
                    <input
                      type="date"
                      value={readingForm.reference_date}
                      onChange={(event) => setReadingForm({ ...readingForm, reference_date: event.target.value })}
                    />
                  </Field>
                  <Field label="P&B atual">
                    <input
                      type="number"
                      value={readingForm.counter_pb_current}
                      onChange={(event) => setReadingForm({ ...readingForm, counter_pb_current: event.target.value })}
                    />
                  </Field>
                </Row>
                <Row>
                  <Field label="P&B anterior">
                    <input
                      type="number"
                      value={readingForm.counter_pb_previous}
                      onChange={(event) => setReadingForm({ ...readingForm, counter_pb_previous: event.target.value })}
                    />
                  </Field>
                  <Field label="Color atual">
                    <input
                      type="number"
                      value={readingForm.counter_color_current}
                      onChange={(event) => setReadingForm({ ...readingForm, counter_color_current: event.target.value })}
                    />
                  </Field>
                </Row>
                <Field label="Color anterior">
                  <input
                    type="number"
                    value={readingForm.counter_color_previous}
                    onChange={(event) => setReadingForm({ ...readingForm, counter_color_previous: event.target.value })}
                  />
                </Field>
                <Field label="Observações">
                  <textarea value={readingForm.notes} onChange={(event) => setReadingForm({ ...readingForm, notes: event.target.value })} />
                </Field>
                <button className="primary" type="submit" disabled={busy}>
                  Enviar leitura
                </button>
              </form>
            )}
          </PortalPanel>

          <PortalPanel title="Abrir chamado" description="Suporte simples pelo portal">
            <form className="panel-form compact" onSubmit={submitTicket}>
              <Row>
                <Field label="Assunto">
                  <input value={ticketForm.subject} onChange={(event) => setTicketForm({ ...ticketForm, subject: event.target.value })} />
                </Field>
                <Field label="Prioridade">
                  <select value={ticketForm.priority} onChange={(event) => setTicketForm({ ...ticketForm, priority: event.target.value as PortalTicketCreate["priority"] })}>
                    <option value="baixa">Baixa</option>
                    <option value="media">Média</option>
                    <option value="alta">Alta</option>
                  </select>
                </Field>
              </Row>
              <Row>
                <Field label="Contrato">
                  <select
                    value={ticketForm.contract_id}
                    onChange={(event) => setTicketForm({ ...ticketForm, contract_id: event.target.value })}
                  >
                    <option value="">Opcional</option>
                    {contracts.map((contract) => (
                      <option key={contract.id} value={contract.id}>
                        {contract.number}
                      </option>
                    ))}
                  </select>
                </Field>
                <Field label="Equipamento">
                  <select
                    value={ticketForm.equipment_id}
                    onChange={(event) => setTicketForm({ ...ticketForm, equipment_id: event.target.value })}
                  >
                    <option value="">Opcional</option>
                    {equipment.map((item) => (
                      <option key={item.id} value={item.id}>
                        {item.brand} {item.model}
                      </option>
                    ))}
                  </select>
                </Field>
              </Row>
              <Field label="Descrição">
                <textarea value={ticketForm.description} onChange={(event) => setTicketForm({ ...ticketForm, description: event.target.value })} />
              </Field>
              <button className="primary" type="submit" disabled={busy}>
                Abrir chamado
              </button>
            </form>
          </PortalPanel>

          <PortalPanel title="Contratos" description="Acordos ativos e históricos">
            <PortalList
              items={contracts}
              searchableText={(item) => `${item.number} ${item.status} ${item.notes || ""}`}
              searchPlaceholder="Pesquisar contrato"
              renderItem={(item) => (
                <>
                  <div>
                    <strong>{item.number}</strong>
                    <small>
                      Cliente #{item.client_id} | Plano #{item.plan_id} | {item.status}
                    </small>
                  </div>
                  <span>{formatDate(item.start_date)} {item.end_date ? `- ${formatDate(item.end_date)}` : ""}</span>
                </>
              )}
            />
          </PortalPanel>

          <PortalPanel title="Equipamentos" description="Impressoras vinculadas">
            <PortalList
              items={equipment}
              searchableText={(item) => `${item.brand} ${item.model} ${item.serial_number} ${item.status}`}
              searchPlaceholder="Pesquisar equipamento"
              renderItem={(item) => (
                <>
                  <div>
                    <strong>
                      {item.brand} {item.model}
                    </strong>
                    <small>
                      {item.serial_number} | {item.status}
                    </small>
                  </div>
                  <span>{item.location || "Sem local"}</span>
                </>
              )}
            />
          </PortalPanel>

          <PortalPanel title="Leituras" description="Histórico de medições">
            <PortalList
              items={readings}
              searchableText={(item) => `${item.reference_date} ${item.source} ${item.contract_id} ${item.equipment_id}`}
              searchPlaceholder="Pesquisar leitura"
              renderItem={(item) => (
                <>
                  <div>
                    <strong>Leitura {formatDate(item.reference_date)}</strong>
                    <small>
                      Contrato #{item.contract_id} | Equipamento #{item.equipment_id} | {item.source}
                    </small>
                  </div>
                  <span>
                    {item.counter_pb_current} / {item.counter_color_current}
                  </span>
                </>
              )}
            />
          </PortalPanel>

          <PortalPanel title="Boletos" description="Cobranças disponíveis para download">
            <PortalList
              items={boletos}
              searchableText={(item) => `${item.nosso_numero} ${item.bank_code} ${item.status}`}
              searchPlaceholder="Pesquisar boleto"
              renderItem={(item) => (
                <>
                  <div>
                    <strong>{item.nosso_numero}</strong>
                    <small>
                      {item.bank_code} | {formatDate(item.due_date)} | {item.status} | {currency(item.amount)}
                    </small>
                  </div>
                  <button type="button" className="secondary" onClick={() => downloadBoleto(item)}>
                    Baixar
                  </button>
                </>
              )}
            />
          </PortalPanel>

          <PortalPanel title="Chamados" description="Histórico de suporte">
            <PortalList
              items={tickets}
              searchableText={(item) => `${item.subject} ${item.status} ${item.priority}`}
              searchPlaceholder="Pesquisar chamado"
              renderItem={(item) => (
                <>
                  <div>
                    <strong>{item.subject}</strong>
                    <small>
                      {item.priority} | {item.status}
                    </small>
                  </div>
                  <span>{formatDate(item.last_response_at || item.resolved_at)}</span>
                </>
              )}
            />
          </PortalPanel>
        </section>
      </main>
    </div>
  );
}

function PortalPanel({ title, description, children }: { title: string; description: string; children: ReactNode }) {
  return (
    <section className="panel portal-panel">
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

function PortalList<T extends { id: number }>({
  items,
  renderItem,
  searchableText,
  searchPlaceholder,
}: {
  items: T[];
  renderItem: (item: T) => ReactNode;
  searchableText?: (item: T) => string;
  searchPlaceholder: string;
}) {
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(5);

  const filtered = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return items.filter((item) => !searchableText || !normalized || searchableText(item).toLowerCase().includes(normalized));
  }, [items, query, searchableText]);

  useEffect(() => {
    setPage(1);
  }, [query, pageSize, items.length]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const currentPage = Math.min(page, totalPages);
  const start = (currentPage - 1) * pageSize;
  const pageItems = filtered.slice(start, start + pageSize);

  return (
    <div className="list-shell">
      <div className="list-toolbar">
        <input placeholder={searchPlaceholder} value={query} onChange={(event) => setQuery(event.target.value)} />
        <select value={pageSize} onChange={(event) => setPageSize(Number(event.target.value))}>
          <option value={5}>5</option>
          <option value={10}>10</option>
          <option value={25}>25</option>
        </select>
      </div>

      {filtered.length === 0 ? (
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

      {filtered.length > pageSize ? (
        <div className="pagination">
          <span>
            Mostrando {start + 1}-{Math.min(start + pageSize, filtered.length)} de {filtered.length}
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

function Row({ children }: { children: ReactNode }) {
  return <div className="row">{children}</div>;
}

export default PortalWorkspace;
