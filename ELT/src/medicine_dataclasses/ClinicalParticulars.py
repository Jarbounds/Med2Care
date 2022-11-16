from dataclasses import dataclass, field
from ELT.src.medicine_dataclasses.ContraIndications import ContraIndications


@dataclass
class ClinicalParticulars:
    therapeutic_indications: str = field(init=False, default_factory=str)
    contraindications: ContraIndications = field(init=False, default_factory=ContraIndications)
