from pydantic import BaseModel
from typing import Optional, Dict, List

class PlotDetails(BaseModel):
    length: float
    width: float
    unit: str
    shape: str
    facing: str

class BuildingConfig(BaseModel):
    floors: str
    building_type: str
    built_up_area: Optional[float] = None

class RoomRequirements(BaseModel):
    bedrooms: int
    bathrooms: int
    kitchen: bool
    living_room: bool
    dining_area: bool
    pooja_room: bool
    study_room: Optional[bool] = False
    balcony: Optional[bool] = False
    parking: bool

class DesignPreferences(BaseModel):
    style: str
    layout_type: str
    natural_lighting: str
    visualization: str

class EntrancePreferences(BaseModel):
    main_entrance_preference: Optional[List[str]] = []
    separate_service_entry: bool = False

class RoomSizePreferences(BaseModel):
    master_bedroom: str = "medium"
    kitchen: str = "medium"
    living_room: str = "medium"

class LifestylePreferences(BaseModel):
    layout_style: str = "modern"
    open_kitchen: bool = True
    natural_light_priority: str = "medium"

class OutputPreferences(BaseModel):
    number_of_plans: int = 3
    output_format: str = "2D"
    export_format: List[str] = ["PDF"]

class UserInput(BaseModel):
    plot: PlotDetails
    building: BuildingConfig
    rooms: RoomRequirements
    vastu_preference: str # Low, Medium, High
    entrance: Optional[EntrancePreferences] = None
    room_sizes: Optional[RoomSizePreferences] = None
    lifestyle: Optional[LifestylePreferences] = None
    output: OutputPreferences
    # Legacy support
    design: Optional[DesignPreferences] = None
    vastu_level: Optional[str] = None

class PromptOutput(BaseModel):
    optimized_prompt: str
    vastu_score: float
    vastu_breakdown: dict
    vastu_notes: Optional[list] = []

class DesignOutput(BaseModel):
    image_base64: Optional[str] = "" # Deprecated, kept for backward compat
    images: list[str] = [] # List of base64 images
    reports: list[str] = [] # List of base64 PDFs
    prompt: str
