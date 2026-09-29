from dataclasses import dataclass, field
from typing import List

@dataclass
class MachineConfig:
    category: str
    count: int
    mttf: float
    repair_min: float
    repair_max: float

@dataclass
class AdjusterConfig:
    adjuster_id: str
    skills: List[str] = field(default_factory=list)
    skill_capacity: dict = field(default_factory=dict)

@dataclass
class Scenario:
    machine_configs: List[MachineConfig]
    adjusters: List[AdjusterConfig]
    duration: float = 10000.0
    warmup: float = 0.0
    seed: int = 1
