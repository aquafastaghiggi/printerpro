# PrintManager Pro

Sistema de gestão para locação e outsourcing de impressoras.

## Objetivo

Centralizar a operação de uma empresa de impressão em um único sistema com:

- cadastros de clientes, equipamentos e contratos
- controle de leituras e faturamento mensal
- financeiro com contas a receber e a pagar
- emissão fiscal
- integrações com boletos, SNMP, e-mail e armazenamento de arquivos
- arquitetura preparada para multi-tenant

## Stack alvo

- Backend: Python + FastAPI
- Frontend: React + TypeScript
- Banco: PostgreSQL
- Cache e filas: Redis + Celery
- Arquivos: MinIO/S3
- Integrações: SEFAZ, bancos, SNMP, e-mail

## Foco inicial recomendado

Para não tentar construir tudo ao mesmo tempo, o primeiro MVP deve entregar:

1. autenticação e perfis de acesso
2. cadastro de clientes
3. cadastro de equipamentos
4. cadastro de planos
5. contratos
6. lançamento de leituras
7. faturamento básico

Depois disso, a evolução natural é:

1. financeiro
2. boletos e conciliação
3. NF-e e NFS-e
4. portal do cliente
5. automações e BI

## Estrutura de trabalho

O projeto deve ser construído em fases:

- Fase 0: fundação técnica e regras do domínio
- Fase 1: núcleo operacional do MVP
- Fase 2: financeiro
- Fase 3: fiscal, com configuração tributária, emissão e autorização simulada
- Fase 4: portal e automações
- Fase 5: BI e mobile

## Próximo passo

Definir o recorte exato do MVP e começar a montar a base do backend.

## Como rodar a base local

1. criar um arquivo `.env` a partir do `.env.example`
2. instalar as dependencias do projeto
3. rodar as migrations com:

```bash
python -m alembic upgrade head
```

4. rodar tudo em localhost com um comando:

```bash
npm run dev
```

Isso sobe:

- backend em `http://127.0.0.1:8000`
- frontend em `http://127.0.0.1:4173`
- documentação da API em `http://127.0.0.1:8000/docs`

5. acessar no navegador:

- frontend: `http://127.0.0.1:4173`
- API health: `http://127.0.0.1:8000/health`
- API docs: `http://127.0.0.1:8000/docs`

## Seed inicial

Para criar um tenant e um usuario administrador inicial:

```bash
python scripts/create_admin.py
```

O login usa:

- tenant: `documento` ou `nome`
- e-mail do usuário
- senha

O portal do cliente usa:

- tenant: `documento` ou `nome`
- documento do cliente

No painel interno, o MVP já inclui:

- edição completa de clientes, equipamentos, planos, contratos e leituras
- busca, filtros e paginação nas listas
- ações rápidas para duplicar e encerrar contratos
- ação rápida para ativar ou desativar equipamentos
- portal do cliente com leituras manuais, boletos, relatórios e chamados

Por padrão, o bootstrap e o seed usam:

- tenant: `00000000000000`
- e-mail: `admin@demo.com`
- senha: `admin123`
