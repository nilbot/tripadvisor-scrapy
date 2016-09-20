# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class HotelItem(Item):
    item_id = Field()
    item_title = Field()
    description = Field()
    site_name = Field()
    url = Field()
    batch_id = Field()


class ReviewItem(Item):
    user_id = Field()
    item_id = Field()
    review_id = Field()
    review_title = Field()
    rating = Field()
    rating_percentage=Field()
    timestamp_rating = Field()
    review_text = Field()
    site_name = Field()
    url = Field()
    batch_id = Field()

class HotelURLItem(Item):
    hotel_name = Field()
    hotel_href = Field()
