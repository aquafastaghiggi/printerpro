from fastapi import APIRouter

from app.api.v1.routes import auth, billing, clients, contracts, equipment, finance, fiscal, plans, portal, readings, tenants, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(clients.router, prefix="/clientes", tags=["clientes"])
api_router.include_router(equipment.router, prefix="/equipamentos", tags=["equipamentos"])
api_router.include_router(plans.router, prefix="/planos", tags=["planos"])
api_router.include_router(contracts.router, prefix="/contratos", tags=["contratos"])
api_router.include_router(readings.router, prefix="/leituras", tags=["leituras"])
api_router.include_router(billing.router, prefix="/faturamento", tags=["faturamento"])
api_router.include_router(finance.router, prefix="/financeiro", tags=["financeiro"])
api_router.include_router(fiscal.router, prefix="/fiscal", tags=["fiscal"])
api_router.include_router(portal.router, prefix="/portal", tags=["portal"])
