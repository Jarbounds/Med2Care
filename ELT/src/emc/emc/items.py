# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from dataclasses import dataclass, field

import scrapy


# @dataclass
# class Pregnancy:
#     name: str = field(init=True, default_factory=str)
#     description: str = field(init=True, default_factory=str)


@dataclass
class ContraIndications:
    disease: str = field(init=True, default_factory=str)
    pregnancy: str = field(init=True, default_factory=str)
    machine_ops: str = field(init=True, default_factory=str)
    excipients: str = field(init=True, default_factory=str)
    incompatibilities: str = field(init=True, default_factory=str)


@dataclass
class ClinicalParticulars:
    therapeutic_indications: str = field(init=True, default_factory=str)
    contraindications: ContraIndications = field(init=True, default_factory=ContraIndications)


@dataclass
class Metadata:
    name: str = field(init=True, default_factory=str)
    composition: str = field(init=True, default_factory=str)
    clinical_particulars: ClinicalParticulars = field(init=True, default_factory=ClinicalParticulars)
    revision_date: str = field(init=True, default_factory=str)


@dataclass
class Medicine:
    medicine_id: str = field(init=True, default_factory=str)
    emc_id: str = field(init=True, default_factory=str)
    metadata: Metadata = field(init=True, default_factory=Metadata)


class EmcMedicinesScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    a = scrapy.Item()
    pass
