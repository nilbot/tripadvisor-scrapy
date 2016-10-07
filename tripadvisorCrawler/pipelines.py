# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import simplejson as json
import logging

from tripadvisorCrawler.items import HotelItem, ReviewItem, HotelURLItem

logger = logging.getLogger()

class TripadvisorcrawlerPipeline(object):
    def __init__(self):
        if not os.path.exists('result'):
            os.makedirs('result')

        self.hotel = open('result/hotel_items.jl','a')
        self.review = open('result/review_items.jl', 'a')
        self.urls = open('result/urls.txt','a')
        logger.info('Pipeline ready')

    def process_item(self, item, spider):
        if type(item) is HotelItem:
            data = {'item_id': item['item_id'],
                    'item_title': item['item_title'],
                    'description': item['description'],
                    'city': item['city'],
                    'site_name': 'TripAdvisor',
                    'batch_id': item['batch_id'],
                    'url': item['url']}
            line = json.dumps(dict(data)) + "\n"
            self.hotel.write(line)
        elif type(item) is ReviewItem:
            data = {'user_id': item['user_id'],
                    'item_id': item['item_id'],
                    'batch_id': item['batch_id'],
                    'review_id': item['review_id'],
                    'review_title': item['review_title'],
                    'rating': item['rating'],
                    'rating_percentage':item['rating_percentage'],
                    'timestamp_rating': item['timestamp_rating'],
                    'site_name': 'TripAdvisor',
                    'review_text': item['review_text'],
                    'url': item['url']}
            line = json.dumps(dict(data)) + "\n"
            self.review.write(line)
        elif type(item) is HotelURLItem:
            data = {'hotel_name': item['hotel_name'],'hotel_href': item['hotel_href']}
            line = json.dumps(dict(data)) + "\n"
            self.urls.write(line)

        return item

    def __del__(self):
        logger.info('Pipeline closed')
