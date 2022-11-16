from dataclasses import dataclass, field
from .Metadata import Metadata

# TODO: Find a medicine id (ATC Code cannot be used, because various medicines can contain the same active principle,
# aka same ATC Code.


@dataclass
class Medicine:
    medicine_id: str = field(init=False, default_factory=str)
    metadata: Metadata = field(init=False, default_factory=Metadata)
