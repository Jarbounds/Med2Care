from dataclasses import dataclass, field


@dataclass
class Pregnancy:
    name: str = field(init=True, default_factory=str)
    description: str = field(init=True, default_factory=str)
