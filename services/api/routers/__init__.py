"""API routers package for KoreX."""

from services.api.routers.ai import router as ai_router
from services.api.routers.attendance import router as attendance_router
from services.api.routers.audit import router as audit_router
from services.api.routers.crowd import router as crowd_router
from services.api.routers.dependencies import router as dependencies_router
from services.api.routers.events import router as events_router
from services.api.routers.knowledge import router as knowledge_router
from services.api.routers.notifications import router as notifications_router
from services.api.routers.notion import router as notion_router
from services.api.routers.participants import router as participants_router
from services.api.routers.planning import router as planning_router
from services.api.routers.proposals import router as proposals_router
from services.api.routers.governance import router as governance_router
from services.api.routers.itinerary import router as itinerary_router
from services.api.routers.resources import router as resources_router
from services.api.routers.scenario import router as scenario_router
from services.api.routers.sessions import router as sessions_router
from services.api.routers.transport import router as transport_router
from services.api.routers.venues import router as venues_router
from services.api.routers.weather import router as weather_router
from services.api.routers.carto import router as carto_router

__all__ = [
    "events_router",
    "venues_router",
    "sessions_router",
    "participants_router",
    "resources_router",
    "audit_router",
    "dependencies_router",
    "planning_router",
    "proposals_router",
    "ai_router",
    "notion_router",
    "notifications_router",
    "attendance_router",
    "transport_router",
    "crowd_router",
    "weather_router",
    "knowledge_router",
    "carto_router",
    "scenario_router",
    "governance_router",
    "itinerary_router",
]



