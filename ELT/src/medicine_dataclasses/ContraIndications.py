from dataclasses import dataclass, field


@dataclass
class ContraIndications:
    disease: list = field(init=False, default_factory=list)
    pregnancy: str = field(init=False, default_factory=str)
    machine_ops: str = field(init=False, default_factory=str)
    excipients: str = field(init=False, default_factory=str)
    incompatibilities: str = field(init=False, default_factory=str)
