__author__ = 'ruihaidong'

import re
import os
import simplejson as json

import scrapy
from scrapy.selector import Selector
from datetime import datetime

from ..items import HotelItem, ReviewItem, HotelURLItem


def get_timestamp():
    import time
    # https://docs.python.org/2/library/time.html#time.strftime
    # datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    return time.strftime("%Y%m%d%H%M%S")


batch_id = get_timestamp()

dublin_hotel_uri = "https://www.tripadvisor.ie/Hotels-g186605-Dublin_County_Dublin-Hotels.html"
cork_hotel_uri = "https://www.tripadvisor.ie/Hotels-g186600-Cork_County_Cork-Hotels.html"
galway_hotel_uri = "https://www.tripadvisor.ie/Hotels-g186609-Galway_County_Galway_Western_Ireland-Hotels.html"
hotel_urls = [dublin_hotel_uri, cork_hotel_uri, galway_hotel_uri]


class HomeSpider(scrapy.Spider):
    name = "hspider"
    page_curr = 1

    def __init__(self, *args, **kwargs):
        super(HomeSpider, self).__init__(*args, **kwargs)
        city = int(kwargs.get("city"))
        self.start_urls = [hotel_urls[city]]

    def parse(self, response):
        baseurl = 'https://www.tripadvisor.ie'
        sel = Selector(response)
        # find next hotel list page
        nextlistLink = sel.xpath(
            '//span[starts-with(@class,"pageNum") and substring(@class, string-length(@class) - string-length("current") + 1)="current"]/following-sibling::a[1]/@href'
        ).extract()

        if len(nextlistLink) != 0:
            self.logger.info(
                'NEXT HOTEL LIST PAGE LINK: {}'.format(nextlistLink[0]))
            request = scrapy.Request(
                baseurl + nextlistLink[0], callback=self.parse)
            yield request

        sel = Selector(response)
        url_divs = sel.xpath('//div[@class="listing_title"]/a')
        for div in url_divs:
            hotel = HotelURLItem()
            hotel['hotel_name'] = div.xpath('text()').extract()[0]
            hotel['hotel_href'] = baseurl + div.xpath('@href').extract()[0]
            yield hotel


def as_hotelurlitem(jsonItem):
    if 'hotel_name' in jsonItem and 'hotel_href' in jsonItem:
        res = HotelURLItem()
        res['hotel_name'] = jsonItem['hotel_name']
        res['hotel_href'] = jsonItem['hotel_href']
        return res
    return None


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
                jsonarray = [
                    json.loads(
                        url, object_hook=as_hotelurlitem)
                    for url in f.readlines() if url.startswith('{')
                ]
                self.start_urls = [
                    j['hotel_href'] for j in jsonarray if j['hotel_href']
                ]

    def parse(self, response):
        city = self.get_city(response.request.url)
        # get Hotel information
        hxs = Selector(response)
        hitem = HotelItem()
        hitem['url'] = response.url
        hitem['batch_id'] = batch_id
        hitem['city'] = city
        hitem['item_title'] = 'unknown'
        item_title = hxs.xpath('//*[@id="HEADING"]/text()').extract()
        if len(item_title) > 1:
            hitem['item_title'] = item_title[1]
        else:
            hitem['item_title'] = item_title[0]

        hitem['description'] = 'unknown'
        description = hxs.xpath(
            '//meta[@name="description"]/@content').extract()
        if len(description) > 0:
            hitem['description'] = description[0]

        # use the part of url between .ie/ and .html as hotel_id
        hotel_id = re.compile(
            'https://www.tripadvisor\.([^/]*)/([^\.]*).html').match(
                response.url)
        if hotel_id:
            hitem['item_id'] = hotel_id.group(2)
        else:
            hitem['item_id'] = response.url

        recommendation_list = hxs.xpath(
            '//div[@class="propertyLink"]').extract()
        hitem['recommendation_list'] = recommendation_list

        yield hitem

        # getReviews
        request = scrapy.Request(response.url, callback=self.parse_review_list)
        request.meta['item_id'] = hitem['item_id']
        yield request

    def parse_review_list(self, response):

        baseurl = 'https://www.tripadvisor.ie'

        burem = bu = re.compile('(http[s]{0,1}://[^/]*)/').match(response.url)
        if burem:
            baseurl = burem.group(0)

        hxs = Selector(response)
        # find next review list page
        nextlistLink = hxs.xpath(
            '//span[@class="pageNum current"]/following-sibling::a[1]/@href'
        ).extract()
        item_id = response.meta['item_id']

        if len(nextlistLink) != 0:
            self.logger.info('NEXT PAGE LINK:' + nextlistLink[0])
            request = scrapy.Request(
                baseurl + nextlistLink[0], callback=self.parse_review_list)
            request.meta['item_id'] = item_id
            yield request

        # for each review on the current review list page, to find review link and then to visit review page to get full review
        reviewLinks = hxs.xpath(
            '//div[@id="REVIEWS"]/descendant::a[span]/@href').extract()

        self.logger.info(len(reviewLinks))

        for rlink in reviewLinks:
            self.logger.info('REVIEW LINKS:' + rlink)
            item = ReviewItem()
            item['item_id'] = item_id
            request = scrapy.Request(
                baseurl + rlink, callback=self.parse_review)
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
        rating = rnode.xpath(
            '//descendant::span[@class="rate sprite-rating_s rating_s"]').re(
                ratingRe)
        if len(rating) > 0:
            item['rating'] = rating[0]

        if item['rating'] != 'unknown':
            item['rating_percentage'] = str(
                (float(item['rating']) - self.rmin) / (self.rmax - self.rmin))
        else:
            item['rating_percentage'] = 'unknown'

        item['review_title'] = 'unknown'
        reviewTitle = rnode.xpath(
            '//descendant::div[@class="quote"]/text()').extract()
        if len(reviewTitle) > 0:
            item['review_title'] = reviewTitle[0]

        item['user_id'] = 'unknown'
        # userIdRe = re.compile('user_name_name_click\'\)\">([^<]*)</span>')
        #userIdRe = re.compile('class=\"expand_inline scrname hvrIE6 mbrName_([^\"]*)\"')
        userIdRe = re.compile(
            'class=\"expand_inline scrname mbrName_([^\"]*)\"')

        userId = rnode.xpath('//descendant::span').re(userIdRe)
        if userId:
            item['user_id'] = userId[0]

        item['url'] = response.url
        item['review_id'] = 'unknown'
        rid = rnode.xpath('//descendant::p/@id').extract()

        if len(rid) > 0:
            item["review_id"] = rid[0]

        item['timestamp_rating'] = 'unknown'
        ratingDateRe = re.compile(' content="([^\"]*)"')
        ratingDate = rnode.xpath(
            '//descendant::span[@class="ratingDate" or @class="ratingDate relativeDate"]'
        ).re(ratingDateRe)
        if len(ratingDate) > 0:
            rating_date = datetime.strptime(ratingDate[0],
                                            '%Y-%m-%d').isoformat()
            self.logger.info(rating_date)
            item['timestamp_rating'] = rating_date
            #item['rating_date'] = ratingDate[0]

        return item

    def get_city(self, urlString):
        base = "https://www.tripadvisor.ie"
        regex = re.compile(base + '/.*-(?P<city>[a-z]+)_.*\.html')
        found = regex.search(urlString.lower())
        if found is None:
            print('urlString is {}'.format(
                urlString.lower()))  #self.logger.warning
            return ''
        return found.group('city')
