from dataclasses import dataclass, field
from .ClinicalParticulars import ClinicalParticulars


@dataclass
class Metadata:
    name: str = field(init=False, default_factory=str)
    composition: str = field(init=False, default_factory=str)
    clinical_particulars: ClinicalParticulars = field(init=False, default_factory=ClinicalParticulars)
    revision_date: str = field(init=False, default_factory=str)
