# Plano de Implementacao - PrintManager Pro

## 1. Visao geral

O documento do projeto descreve um ERP voltado para locacao e outsourcing de impressoras. A proposta cobre operação, financeiro, fiscal, automação e portal do cliente.

## 2. Leitura pratica do escopo

### O que ja esta claro

- o sistema deve ser web
- o backend sera em Python com FastAPI
- o frontend sera em React com TypeScript
- o banco principal sera PostgreSQL
- o sistema precisa suportar multi-tenant
- existem tres modelos de cobranca:
  - por pagina
  - mensalidade fixa
  - franquia com excedente

### O que deve entrar primeiro

Para um primeiro corte de entrega, o melhor caminho e construir o nucleo operacional:

- autenticacao e permissao
- clientes
- equipamentos
- planos
- contratos
- leituras
- faturamento

## 3. Fases sugeridas

### Fase 0 - Fundacao

Objetivo: deixar o projeto pronto para crescer sem retrabalho.

Entregas:

- estrutura do repositório
- configuracao do backend
- configuracao do frontend
- banco PostgreSQL
- migracoes
- autenticação base
- padrao de log e auditoria

### Fase 1 - MVP Core

Objetivo: permitir cadastrar contrato e faturar.

Entregas:

- usuarios e permissoes
- clientes
- equipamentos
- planos de locacao
- contratos
- leituras manuais
- calculo de faturamento
- geracao de fatura

### Fase 2 - Financeiro

Entregas:

- contas a receber
- contas a pagar
- boletos
- conciliacao
- inadimplencia

### Fase 3 - Fiscal

Entregas:

- NF-e
- NFS-e
- XMLs
- cancelamento
- CC-e

### Fase 4 - Portal

Entregas:

- acesso do cliente
- envio de leitura com foto
- visualizacao de faturas
- notificacoes

### Fase 5 - Automacao e BI

Entregas:

- SNMP
- importacao CSV
- alertas
- dashboards
- DRE

## 4. Ordem de implementacao recomendada

1. modelagem do banco
2. autenticacao
3. cadastros basicos
4. contratos
5. leituras
6. faturamento
7. frontend do MVP
8. financeiro
9. fiscal

## 5. Decisoes que ainda precisam ser fechadas

- o sistema vai começar como SaaS multi-tenant ou como uma unica empresa com preparo para multi-tenant
- qual banco bancario sera usado primeiro para boletos
- quais municipios entram primeiro na NFS-e
- qual sera o modelo padrao de contrato
- se o portal do cliente entra no MVP ou depois

## 6. Proximo passo tecnico

Montar a base do projeto com:

- backend FastAPI
- estrutura de apps por modulo
- configuracao de ambiente
- migrations
- autenticacao
- primeira modelagem do dominio
