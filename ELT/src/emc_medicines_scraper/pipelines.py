# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter

import jsonpickle
from . import Medicine
from .spiders import EMCMedicineInfoCrawler


class EmcMedicinesScraperPipeline:
    custom_settings: dict = {
        'base_dir': '../data/json/'
    }

    def process_item(self, item: Medicine, spider):
        if isinstance(spider, EMCMedicineInfoCrawler):
            medicine_id = item.medicine_id
            with open(f'{self.custom_settings["base_dir"]}{medicine_id}.json', 'w', encoding='utf-8') as file:
                file.write(jsonpickle.encode(item, unpicklable=False, indent=4))
        return item
