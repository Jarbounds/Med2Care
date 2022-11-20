from dataclasses import dataclass, field
from .Pregnancy import Pregnancy


@dataclass
class ContraIndications:
    disease: list = field(init=False, default_factory=list)
    pregnancy: list[Pregnancy] = field(init=False, default_factory=list)
    machine_ops: str = field(init=False, default_factory=str)
    excipients: str = field(init=False, default_factory=str)
    incompatibilities: str = field(init=False, default_factory=str)
