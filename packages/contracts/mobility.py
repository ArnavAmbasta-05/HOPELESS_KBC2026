"""Transport & Mobility Data Contracts (Sprint 8, TRN-001..008, AT-03, TAD §15)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from pydantic import BaseModel, Field


class VehicleStatus(StrEnum):
    AVAILABLE = "available"
    IN_TRANSIT = "in_transit"
    MAINTENANCE = "maintenance"
    UNAVAILABLE = "unavailable"


class TripStatus(StrEnum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REROUTED = "rerouted"


class Stop(BaseModel):
    stop_id: str
    name: str
    building: str
    lat: float = 20.354
    lng: float = 85.818


class Route(BaseModel):
    route_id: str
    name: str
    origin_stop_id: str
    destination_stop_id: str
    estimated_duration_minutes: int
    waypoints: list[str] = Field(default_factory=list)


class Vehicle(BaseModel):
    vehicle_id: str
    name: str
    vehicle_type: str  # shuttle_bus, heavy_bus, electric_cart
    capacity: int
    status: VehicleStatus = VehicleStatus.AVAILABLE
    driver_name: str | None = None
    driver_phone: str | None = None
    current_location: str = "Campus 6 Transport Hub"


class Trip(BaseModel):
    trip_id: str = Field(default_factory=lambda: f"trp_{uuid.uuid4().hex[:8]}")
    route_id: str
    vehicle_id: str
    departure_time: str
    arrival_time: str
    allocated_cohort_id: str | None = None
    allocated_passenger_count: int = 0
    status: TripStatus = TripStatus.SCHEDULED
    source: str = "SCHEDULED_DISPATCH"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class TransportDisruptionEvent(BaseModel):
    disruption_id: str = Field(default_factory=lambda: f"dis_trn_{uuid.uuid4().hex[:8]}")
    vehicle_id: str
    reason: str
    reported_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class VehicleTask(BaseModel):
    task_id: str = Field(default_factory=lambda: f"vtsk_{uuid.uuid4().hex[:8]}")
    vehicle_id: str
    driver_name: str
    instructions: str
    pickup_stop_id: str
    dropoff_stop_id: str
    scheduled_time: str
    status: str = "PENDING"


class TransportNotice(BaseModel):
    notice_id: str = Field(default_factory=lambda: f"tnot_{uuid.uuid4().hex[:8]}")
    cohort_id: str
    previous_pickup: str
    new_pickup: str
    vehicle_assigned: str
    effective_time: str
    instructions: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class TransportReallocationPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"trplan_{uuid.uuid4().hex[:8]}")
    disrupted_vehicle_id: str
    reallocated_vehicle_id: str
    affected_cohort_id: str
    recalculated_capacity: int
    vehicle_tasks: list[VehicleTask] = Field(default_factory=list)
    passenger_notices: list[TransportNotice] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "PROPOSED"
