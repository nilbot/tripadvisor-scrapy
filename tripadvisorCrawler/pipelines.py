# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import requests
import simplejson as json
import logging

from tripadvisorCrawler.items import HotelItem

logger = logging.getLogger()

class TripadvisorcrawlerPipeline(object):
    def __init__(self):
        self.r_uri = 'http://localhost:8889/api/v1/reviews'
        self.p_uri = 'http://localhost:8889/api/v1/products'
        self.headers = {'Content-Type': 'application/json'}
        logger.info('Pipeline ready')

    def process_item(self, item, spider):
        if type(item) is HotelItem:
            data = {'item_id': item['item_id'],
                    'item_title': item['item_title'],
                    'description': item['description'],
                    'site_name': 'TripAdvisor',
                    'batch_id': item['batch_id'],
                    'url': item['url']}
            p = requests.post(self.p_uri, data=json.dumps(data), headers=self.headers)
        else:
            data = {'user_id': item['user_id'],
                    'item_id': item['item_id'],
                    'batch_id': item['batch_id'],
                    'review_id': item['review_id'],
                    'review_title': item['review_title'],
                    'rating': item['rating'],
                    'rating_percentage':item['rating_percentage'],
                    'rating_date': item['rating_date'],
                    'site_name': 'TripAdvisor',
                    'review_text': item['review_text'],
                    'url': item['url']}
            r = requests.post(self.r_uri, data=json.dumps(data), headers=self.headers)

        return item

    def __del__(self):
        logger.info('Pipeline closed')
