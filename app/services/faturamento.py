from __future__ import annotations

from decimal import Decimal

from app.core.enums import TipoPlano
from app.models.contract import Contract
from app.models.reading import Reading


class FaturamentoService:
    def calcular_preview(self, contrato: Contract, leituras: list[Reading]) -> dict[str, object]:
        total_pb = sum(max(0, leitura.counter_pb_current - leitura.counter_pb_previous) for leitura in leituras)
        total_color = sum(max(0, leitura.counter_color_current - leitura.counter_color_previous) for leitura in leituras)

        itens: list[dict[str, object]] = []
        valor_total = Decimal("0.00")

        if contrato.plan.type == TipoPlano.MENSALIDADE:
            valor_total = Decimal(str(contrato.monthly_value or 0))
            itens.append({"descricao": "Mensalidade", "valor": float(valor_total)})

        elif contrato.plan.type == TipoPlano.POR_PAGINA:
            valor_pb = Decimal(str(contrato.plan.price_pb or 0)) * Decimal(total_pb)
            valor_color = Decimal(str(contrato.plan.price_color or 0)) * Decimal(total_color)
            valor_total = valor_pb + valor_color
            itens.extend(
                [
                    {"descricao": f"Impressoes P&B ({total_pb})", "valor": float(valor_pb)},
                    {"descricao": f"Impressoes Color ({total_color})", "valor": float(valor_color)},
                ]
            )

        elif contrato.plan.type == TipoPlano.FRANQUIA:
            monthly = Decimal(str(contrato.monthly_value or 0))
            franquia_pb = contrato.franchise_pb or contrato.plan.franchise_pb or 0
            franquia_color = contrato.franchise_color or contrato.plan.franchise_color or 0
            extra_pb = max(0, total_pb - franquia_pb)
            extra_color = max(0, total_color - franquia_color)
            valor_extra_pb = Decimal(str(contrato.price_excess_pb or contrato.plan.extra_pb or 0)) * Decimal(extra_pb)
            valor_extra_color = Decimal(str(contrato.price_excess_color or contrato.plan.extra_color or 0)) * Decimal(extra_color)
            valor_total = monthly + valor_extra_pb + valor_extra_color
            itens.extend(
                [
                    {"descricao": "Mensalidade / Franquia", "valor": float(monthly)},
                    {"descricao": f"Excedente P&B ({extra_pb})", "valor": float(valor_extra_pb)},
                    {"descricao": f"Excedente Color ({extra_color})", "valor": float(valor_extra_color)},
                ]
            )

        return {
            "contrato_id": contrato.id,
            "total_pb": total_pb,
            "total_color": total_color,
            "valor_total": float(valor_total),
            "itens": itens,
        }
