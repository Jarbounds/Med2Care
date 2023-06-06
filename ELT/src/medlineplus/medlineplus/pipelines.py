# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from .spiders import MedicineInfoSpider


class MedlineplusPipeline:
    def process_item(self, item: dict, spider):
        if isinstance(spider, MedicineInfoSpider):
            path: str = spider.kwargs['output_dir']
            medicine_id: str = item['medicine_id']

            with open(f'{path}/{medicine_id}.json', 'w', encoding='utf-8') as file:
                file.write(json.dumps(item))

        return item
