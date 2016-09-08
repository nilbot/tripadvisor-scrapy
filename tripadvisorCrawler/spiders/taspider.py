__author__ = 'ruihaidong'

import re
import os

import scrapy
from scrapy.selector import Selector
from datetime import datetime

from ..items import HotelItem, ReviewItem

def get_timestamp():
    import time
    # https://docs.python.org/2/library/time.html#time.strftime
    # datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    return time.strftime("%Y%m%d%H%M%S")


batch_id = get_timestamp()


class MySpider(scrapy.Spider):
    name = "taspider"

    rmax = 5.0
    rmin = 1.0

    def __init__(self, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        urls_file = kwargs.get('urls')

        if not os.path.isfile(urls_file):
            raise IOError('Failed to find URLs file "{}"'.format(urls_file))
        else:
            with open(urls_file) as f:
                self.start_urls = [url.strip() for url in f.readlines() if url.startswith('http://')]

    def parse(self, response):

        # get Hotel information
        hxs = Selector(response)
        hitem = HotelItem()
        hitem['url'] = response.url
        hitem['batch_id'] = batch_id

        hitem['item_title'] = 'unknown'
        item_title = hxs.xpath('//*[@id="HEADING"]/text()').extract()
        if len(item_title) > 1:
            hitem['item_title'] = item_title[1]
        else:
            hitem['item_title'] = item_title[0]

        hitem['description'] = 'unknown'
        description = hxs.xpath('//meta[@name="description"]/@content').extract()
        if len(description) > 0:
            hitem['description'] = description[0]

        # use the part of url between .ie/ and .html as hotel_id
        hotel_id = re.compile('http://www.tripadvisor\.([^/]*)/([^\.]*).html').match(response.url)
        if hotel_id:
            hitem['item_id'] = hotel_id.group(2)
        else:
            hitem['item_id'] = response.url

        yield hitem

        # getReviews
        request = scrapy.Request(response.url, callback=self.parse_review_list)
        request.meta['item_id'] = hitem['item_id']
        yield request

    def parse_review_list(self, response):

        baseurl = 'http://www.tripadvisor.ie'

        burem = bu = re.compile('(http[s]{0,1}://[^/]*)/').match(response.url)
        if burem:
            baseurl = burem.group(0)

        hxs = Selector(response)
        # find next review list page
        nextlistLink = hxs.xpath('//span[@class="pageNum current"]/following-sibling::a[1]/@href').extract()
        item_id = response.meta['item_id']

        if len(nextlistLink) != 0:
            self.logger.info('NEXT PAGE LINK:' + nextlistLink[0])
            request = scrapy.Request(baseurl + nextlistLink[0], callback=self.parse_review_list)
            request.meta['item_id'] = item_id
            yield request

        # for each review on the current review list page, to find review link and then to visit review page to get full review
        reviewLinks = hxs.xpath('//div[@id="REVIEWS"]/descendant::a[span]/@href').extract()

        self.logger.info(len(reviewLinks))

        for rlink in reviewLinks:
            self.logger.info('REVIEW LINKS:' + rlink)
            item = ReviewItem()
            item['item_id'] = item_id
            request = scrapy.Request(baseurl + rlink, callback=self.parse_review)
            request.meta['item'] = item
            yield request

    def parse_review(self, response):
        self.logger.info('To parse Review!')

        item = response.meta['item']
        hxs = Selector(response)

        # rtext = hxs.select('//div[@class="  reviewSelector "][1]/descendant::p/text()').extract()

        rnode = hxs.xpath('//div[@class="  reviewSelector "][1]')

        item['batch_id'] = batch_id
        item['review_text'] = 'unknown'
        rtext = rnode.xpath('//descendant::p/text()').extract()
        if len(rtext) > 0:
            item["review_text"] = rtext[0]

        item['rating'] = 'unknown'
        ratingRe = re.compile('alt="([0-5]) of 5 stars"')
        rating = rnode.xpath('//descendant::span[@class="rate sprite-rating_s rating_s"]').re(ratingRe)
        if len(rating) > 0:
            item['rating'] = rating[0]

        if item['rating'] != 'unknown':
            item['rating_percentage'] = str((float(item['rating'])-self.rmin)/(self.rmax-self.rmin))
        else:
            item['rating_percentage'] = 'unknown'

        item['review_title'] = 'unknown'
        reviewTitle = rnode.xpath('//descendant::div[@class="quote"]/text()').extract()
        if len(reviewTitle) > 0:
            item['review_title'] = reviewTitle[0]

        item['user_id'] = 'unknown'
        # userIdRe = re.compile('user_name_name_click\'\)\">([^<]*)</span>')
        #userIdRe = re.compile('class=\"expand_inline scrname hvrIE6 mbrName_([^\"]*)\"')
        userIdRe = re.compile('class=\"expand_inline scrname mbrName_([^\"]*)\"')

        userId = rnode.xpath('//descendant::span').re(userIdRe)
        if userId:
            item['user_id'] = userId[0]

        item['url'] = response.url
        item['review_id'] = 'unknown'
        rid = rnode.xpath('//descendant::p/@id').extract()

        if len(rid) > 0:
            item["review_id"] = rid[0]

        item['rating_date'] = 'unknown'
        ratingDateRe = re.compile(' content="([^\"]*)"')
        ratingDate = rnode.xpath('//descendant::span[@class="ratingDate" or @class="ratingDate relativeDate"]').re(
            ratingDateRe)
        if len(ratingDate) > 0:
            rating_date = datetime.strptime(ratingDate[0],'%Y-%m-%d').isoformat()
            self.logger.info(rating_date)
            item['rating_date'] = rating_date
            #item['rating_date'] = ratingDate[0]

        return item
