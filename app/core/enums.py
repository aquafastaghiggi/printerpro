from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    ADMIN = "administrador"
    FINANCEIRO = "financeiro"
    TECNICO = "tecnico"
    COMERCIAL = "comercial"
    LEITURA = "leitura"


class PessoaTipo(str, Enum):
    PF = "pf"
    PJ = "pj"


class StatusEquipamento(str, Enum):
    DISPONIVEL = "disponivel"
    LOCADO = "locado"
    MANUTENCAO = "em_manutencao"
    BAIXADO = "baixado"


class TipoPlano(str, Enum):
    POR_PAGINA = "por_pagina"
    MENSALIDADE = "mensalidade"
    FRANQUIA = "franquia"


class StatusContrato(str, Enum):
    RASCUNHO = "rascunho"
    VIGENTE = "vigente"
    SUSPENSO = "suspenso"
    ENCERRADO = "encerrado"


class FonteLeitura(str, Enum):
    MANUAL = "manual"
    SNMP = "snmp"
    CSV = "csv"
    PORTAL = "portal"


class StatusTitulo(str, Enum):
    ABERTO = "aberto"
    PARCIAL = "parcialmente_pago"
    PAGO = "pago"
    VENCIDO = "vencido"
    CANCELADO = "cancelado"


class StatusBoleto(str, Enum):
    GERADO = "gerado"
    ENVIADO = "enviado"
    REGISTRADO = "registrado"
    PAGO = "pago"
    VENCIDO = "vencido"
    CANCELADO = "cancelado"
    REJEITADO = "rejeitado"


class StatusRemessa(str, Enum):
    CRIADA = "criada"
    ENVIADA = "enviada"
    PROCESSADA = "processada"
    FALHA = "falha"


class StatusConciliacao(str, Enum):
    PENDENTE = "pendente"
    CASADO = "casado"
    IGNORADO = "ignorado"


class RegimeTributario(str, Enum):
    SIMPLES_NACIONAL = "simples_nacional"
    LUCRO_PRESUMIDO = "lucro_presumido"
    LUCRO_REAL = "lucro_real"
    MEI = "mei"
    OUTRO = "outro"


class TipoDocumentoFiscal(str, Enum):
    NFE = "nfe"
    NFSE = "nfse"


class StatusDocumentoFiscal(str, Enum):
    RASCUNHO = "rascunho"
    AUTORIZADO = "autorizado"
    CANCELADO = "cancelado"
    REJEITADO = "rejeitado"


class OrigemDocumentoFiscal(str, Enum):
    MANUAL = "manual"
    RECEIVABLE = "receivable"
    CONTRACT = "contract"
    BATCH = "batch"


class StatusChamado(str, Enum):
    ABERTO = "aberto"
    EM_ATENDIMENTO = "em_atendimento"
    RESOLVIDO = "resolvido"
    CANCELADO = "cancelado"


class PrioridadeChamado(str, Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
