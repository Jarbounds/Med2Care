# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os

# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter

import jsonpickle
from . import Medicine
from .spiders import EMCMedicineInfoSpider


class EMCMedicinePipeline:

    def process_item(self, item: Medicine, spider):
        if isinstance(spider, EMCMedicineInfoSpider):
            path: str = spider.kwargs['output_dir']
            medicine_id: str = item.medicine_id

            with open(f'{path}/{medicine_id}.json', 'w', encoding='utf-8') as file:
                file.write(jsonpickle.encode(item, unpicklable=False, indent=4))

        return item
