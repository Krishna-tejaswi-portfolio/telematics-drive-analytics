from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class TelemetryEvent(BaseModel):
    device_id: str
    trip_id: str
    ts: datetime
    lat: float
    lon: float
    speed: Optional[float] = Field(default=None, ge=0)
    rpm: Optional[int] = Field(default=None, ge=0)
    coolant_temp: Optional[float] = None
    fuel_level: Optional[float] = Field(default=None, ge=0, le=100)
    event_type: Literal["telemetry","diagnostic","event"] = "telemetry"
