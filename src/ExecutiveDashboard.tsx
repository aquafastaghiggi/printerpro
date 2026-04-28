import type { ReactNode } from "react";
import type {
  DashboardOverview,
  DashboardSeriesPoint,
  MaintenanceTask,
  OperationalNotification,
} from "./types";

type ExecutiveDashboardProps = {
  overview: DashboardOverview | null;
  maintenanceTasks: MaintenanceTask[];
  notifications: OperationalNotification[];
  onSyncNotifications: () => void;
  onDispatchNotifications: () => void;
  onSyncMaintenance: () => void;
  onMarkNotificationRead: (id: number) => void;
  onStartMaintenanceTask: (id: number) => void;
  onCompleteMaintenanceTask: (id: number) => void;
  onDispatchMaintenanceTask: (id: number) => void;
};

function currency(value: number | null | undefined) {
  if (value === null || value === undefined) return "-";
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(value);
}

function formatDateTime(value: string | null | undefined) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

function formatDate(value: string | null | undefined) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("pt-BR", { dateStyle: "short" }).format(new Date(value));
}

function jumpTo(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function formatMonthLabel(label: string) {
  const [year, month] = label.split("-");
  if (!year || !month) return label;
  return new Intl.DateTimeFormat("pt-BR", { month: "short", year: "2-digit" }).format(new Date(Number(year), Number(month) - 1, 1));
}

function maxValue(points: DashboardSeriesPoint[]) {
  return Math.max(1, ...points.map((point) => Number(point.value) || 0));
}

function statusTone(status: string) {
  if (status === "pendente" || status === "em_manutencao") return "warning";
  if (status === "em_execucao" || status === "agendada") return "info";
  if (status === "concluida") return "success";
  return "muted";
}

function ExecutiveDashboard({
  overview,
  maintenanceTasks,
  notifications,
  onSyncNotifications,
  onDispatchNotifications,
  onSyncMaintenance,
  onMarkNotificationRead,
  onStartMaintenanceTask,
  onCompleteMaintenanceTask,
  onDispatchMaintenanceTask,
}: ExecutiveDashboardProps) {
  if (!overview) {
    return null;
  }

  const metrics: Array<{ label: string; value: ReactNode }> = [
    { label: "Clientes", value: overview.metrics.clients_total },
    { label: "Contratos vigentes", value: overview.metrics.active_contracts },
    { label: "Equipamentos ativos", value: overview.metrics.active_equipment },
    { label: "Leituras 30 dias", value: overview.metrics.readings_last_30_days },
    { label: "Tickets abertos", value: overview.metrics.open_tickets },
    { label: "Renovacoes 30 dias", value: overview.metrics.contracts_expiring_30_days },
    { label: "Leituras sem validacao", value: overview.metrics.unvalidated_readings },
    { label: "Receber vencido", value: currency(overview.metrics.receivables_overdue_total) },
    { label: "Pagar vencido", value: currency(overview.metrics.payables_overdue_total) },
    { label: "Manutencoes abertas", value: overview.bi.maintenance_open_total },
  ];

  const shortcuts = [
    { label: "Cadastros", target: "cadastros" },
    { label: "Financeiro", target: "financeiro" },
    { label: "Fiscal", target: "fiscal" },
    { label: "Operacao", target: "operacao" },
  ];

  return (
    <section className="executive-dashboard">
      <header className="dashboard-hero">
        <div>
          <span className="eyebrow">Cockpit executivo</span>
          <h2>Automacao, mobilidade e previsibilidade em uma unica visao.</h2>
          <p>
            Este painel combina alertas automaticos, BI operacional, fila de manutencao e visao de clientes para
            acelerar a decisao.
          </p>
        </div>
        <div className="dashboard-meta">
          <strong>{formatDateTime(overview.generated_at)}</strong>
          <small>Atualizado com dados do tenant atual.</small>
          <div className="dashboard-meta-actions">
            <button type="button" className="secondary dashboard-refresh" onClick={onSyncNotifications}>
              Sincronizar alertas
            </button>
            <button type="button" className="secondary dashboard-refresh" onClick={onDispatchNotifications}>
              Enviar alertas
            </button>
          </div>
        </div>
      </header>

      <div className="dashboard-shortcuts">
        {shortcuts.map((shortcut) => (
          <button key={shortcut.target} type="button" className="secondary dashboard-shortcut" onClick={() => jumpTo(shortcut.target)}>
            {shortcut.label}
          </button>
        ))}
      </div>

      <section className="metric-grid dashboard-metric-grid">
        {metrics.map((metric) => (
          <article key={metric.label} className="metric-card dashboard-metric-card">
            <span>{metric.label}</span>
            <strong>{metric.value}</strong>
          </article>
        ))}
      </section>

      <section className="dashboard-panels">
        <article className="panel dashboard-panel dashboard-panel-wide" id="operacao">
          <div className="panel-head">
            <div>
              <h3>BI operacional</h3>
              <p>Leituras, faturamento, status do parque e fila tecnica em uma leitura unica.</p>
            </div>
            <button type="button" className="secondary" onClick={onSyncMaintenance}>
              Sincronizar fila tecnica
            </button>
          </div>
          <div className="bi-grid">
            <ChartCard
              title="Receita por mes"
              description="Competencia com maior concentracao de faturamento."
              points={overview.bi.revenue_by_month}
              valueFormatter={currency}
            />
            <ChartCard
              title="Leituras por mes"
              description="Volume de leituras recebidas no periodo."
              points={overview.bi.readings_by_month}
              valueFormatter={(value) => new Intl.NumberFormat("pt-BR").format(value)}
            />
            <BreakdownCard
              title="Status dos equipamentos"
              description="Distribuicao atual do parque instalado."
              items={overview.bi.equipment_status}
            />
            <BreakdownCard
              title="Fila de manutencao"
              description="Tarefas abertas, agendadas e concluídas."
              items={overview.bi.maintenance_status}
            />
          </div>
        </article>

        <article className="panel dashboard-panel" id="notificacoes">
          <div className="panel-head">
            <div>
              <h3>Central de notificacoes</h3>
              <p>Alertas persistidos para acompanhamento da equipe.</p>
            </div>
          </div>
          {notifications.length === 0 ? (
            <div className="empty-state">Nenhuma notificacao ainda.</div>
          ) : (
            <div className="dashboard-alert-list">
              {notifications.map((notification) => (
                <article
                  key={notification.id}
                  className={`dashboard-alert dashboard-alert--${notification.severity} ${notification.is_read ? "dashboard-alert--read" : ""}`}
                >
                  <div className="dashboard-alert-head">
                    <strong>{notification.title}</strong>
                    <span>{notification.is_read ? "lida" : "nova"}</span>
                  </div>
                  <p>{notification.detail}</p>
                  <small>{notification.suggested_action}</small>
                  {!notification.is_read ? (
                    <button type="button" className="secondary dashboard-inline-action" onClick={() => onMarkNotificationRead(notification.id)}>
                      Marcar como lida
                    </button>
                  ) : null}
                </article>
              ))}
            </div>
          )}
        </article>

        <article className="panel dashboard-panel">
          <div className="panel-head">
            <div>
              <h3>Alertas automaticos</h3>
              <p>Acoes sugeridas para cobranca, renovacao, validacao e suporte.</p>
            </div>
          </div>
          {overview.alerts.length === 0 ? (
            <div className="empty-state">Nenhum alerta no momento.</div>
          ) : (
            <div className="dashboard-alert-list">
              {overview.alerts.map((alert) => (
                <article key={`${alert.title}-${alert.count}`} className={`dashboard-alert dashboard-alert--${alert.severity}`}>
                  <div className="dashboard-alert-head">
                    <strong>{alert.title}</strong>
                    <span>{alert.count}</span>
                  </div>
                  <p>{alert.detail}</p>
                  <small>{alert.suggested_action}</small>
                </article>
              ))}
            </div>
          )}
        </article>

        <article className="panel dashboard-panel" id="manutencao">
          <div className="panel-head">
            <div>
              <h3>Fila de manutencao preventiva</h3>
              <p>Tarefas tecnicas com prioridades, prazos e controle de andamento.</p>
            </div>
            <button type="button" className="secondary" onClick={onSyncMaintenance}>
              Recarregar fila
            </button>
          </div>
          {maintenanceTasks.length === 0 ? (
            <div className="empty-state">Sem tarefas tecnicas no momento.</div>
          ) : (
            <div className="dashboard-list">
              {maintenanceTasks.map((task) => (
                <div key={task.id} className="dashboard-list-row maintenance-row">
                  <div>
                    <strong>{task.title}</strong>
                    <small>
                      {task.description}
                    </small>
                    <div className="row-tags">
                      <span className={`status-pill status-pill--${statusTone(task.status)}`}>{task.status}</span>
                      <span className="status-pill status-pill--muted">{task.priority}</span>
                      <span className="status-pill status-pill--muted">Prazo: {formatDate(task.due_date)}</span>
                    </div>
                  </div>
                  <div className="dashboard-list-meta maintenance-actions">
                    <span>{task.technician_name || "Sem tecnico"}</span>
                    <small>{task.client_id ? `Cliente #${task.client_id}` : "Sem cliente vinculado"}</small>
                    <div className="inline-actions">
                    {(task.status === "pendente" || task.status === "agendada") ? (
                        <button type="button" className="secondary" onClick={() => onStartMaintenanceTask(task.id)}>
                          Iniciar
                        </button>
                      ) : null}
                      {task.status === "em_execucao" ? (
                        <button type="button" className="secondary" onClick={() => onCompleteMaintenanceTask(task.id)}>
                          Concluir
                        </button>
                      ) : null}
                      <button type="button" className="secondary" onClick={() => onDispatchMaintenanceTask(task.id)}>
                        Enviar aviso
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </article>

        <article className="panel dashboard-panel">
          <div className="panel-head">
            <div>
              <h3>Renovacoes proximas</h3>
              <p>Contratos que merecem acompanhamento comercial.</p>
            </div>
          </div>
          {overview.renewals.length === 0 ? (
            <div className="empty-state">Sem contratos com vencimento proximo.</div>
          ) : (
            <div className="dashboard-list">
              {overview.renewals.map((renewal) => (
                <div key={renewal.contract_id} className="dashboard-list-row">
                  <div>
                    <strong>{renewal.number}</strong>
                    <small>{renewal.client_name}</small>
                  </div>
                  <div className="dashboard-list-meta">
                    <span>{renewal.days_left} dias</span>
                    <small>{renewal.end_date}</small>
                  </div>
                </div>
              ))}
            </div>
          )}
        </article>

        <article className="panel dashboard-panel">
          <div className="panel-head">
            <div>
              <h3>Equipamentos em atencao</h3>
              <p>Maquinas em manutencao ou sem vinculo operacional.</p>
            </div>
          </div>
          {overview.equipment_issues.length === 0 ? (
            <div className="empty-state">Sem equipamentos com pendencias.</div>
          ) : (
            <div className="dashboard-list">
              {overview.equipment_issues.map((item) => (
                <div key={item.equipment_id} className="dashboard-list-row">
                  <div>
                    <strong>
                      {item.brand} {item.model}
                    </strong>
                    <small>
                      {item.serial_number} | {item.client_name || "Sem cliente"}
                    </small>
                  </div>
                  <div className="dashboard-list-meta">
                    <span>{item.issue}</span>
                    <small>{item.location || item.status}</small>
                  </div>
                </div>
              ))}
            </div>
          )}
        </article>

        <article className="panel dashboard-panel dashboard-panel-wide">
          <div className="panel-head">
            <div>
              <h3>Clientes em destaque</h3>
              <p>Ranking de base para BI e priorizacao comercial.</p>
            </div>
          </div>
          {overview.top_clients.length === 0 ? (
            <div className="empty-state">Sem dados financeiros suficientes para o ranking.</div>
          ) : (
            <div className="dashboard-table">
              {overview.top_clients.map((client) => (
                <div key={client.client_id} className="dashboard-table-row">
                  <div>
                    <strong>{client.client_name}</strong>
                    <small>{client.contracts} contrato(s)</small>
                  </div>
                  <div className="dashboard-table-values">
                    <span>Aberto: {currency(client.open_total)}</span>
                    <small>Vencido: {currency(client.overdue_total)}</small>
                  </div>
                </div>
              ))}
            </div>
          )}
        </article>
      </section>
    </section>
  );
}

function ChartCard({
  title,
  description,
  points,
  valueFormatter,
}: {
  title: string;
  description: string;
  points: DashboardSeriesPoint[];
  valueFormatter: (value: number) => string;
}) {
  const max = maxValue(points);
  return (
    <article className="bi-card">
      <div className="panel-head panel-head-compact">
        <div>
          <h4>{title}</h4>
          <p>{description}</p>
        </div>
      </div>
      <div className="chart-stack">
        {points.length === 0 ? (
          <div className="empty-state">Sem dados para exibir.</div>
        ) : (
          points.map((point) => {
            const rawValue = Number(point.value) || 0;
            const width = Math.max(8, (rawValue / max) * 100);
            return (
              <div key={point.label} className="chart-row">
                <span>{formatMonthLabel(point.label)}</span>
                <div className="chart-track">
                  <div className="chart-fill" style={{ width: `${width}%` }} />
                </div>
                <strong>{valueFormatter(rawValue)}</strong>
              </div>
            );
          })
        )}
      </div>
    </article>
  );
}

function BreakdownCard({
  title,
  description,
  items,
}: {
  title: string;
  description: string;
  items: Array<{ label: string; count: number }>;
}) {
  const max = Math.max(1, ...items.map((item) => item.count));
  return (
    <article className="bi-card">
      <div className="panel-head panel-head-compact">
        <div>
          <h4>{title}</h4>
          <p>{description}</p>
        </div>
      </div>
      <div className="chart-stack">
        {items.length === 0 ? (
          <div className="empty-state">Sem dados para exibir.</div>
        ) : (
          items.map((item) => {
            const width = Math.max(8, (item.count / max) * 100);
            return (
              <div key={item.label} className="chart-row">
                <span>{item.label}</span>
                <div className="chart-track">
                  <div className="chart-fill chart-fill--neutral" style={{ width: `${width}%` }} />
                </div>
                <strong>{item.count}</strong>
              </div>
            );
          })
        )}
      </div>
    </article>
  );
}

export default ExecutiveDashboard;
