# -*- coding: utf-8 -*-

# Scrapy settings for tripadvisorCrawler project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'tripadvisorCrawler'

SPIDER_MODULES = ['tripadvisorCrawler.spiders']
NEWSPIDER_MODULE = 'tripadvisorCrawler.spiders'

LOG_LEVEL = 'ERROR'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'tripadvisorCrawler (+http://www.yourdomain.com)'

ITEM_PIPELINES = {
    'tripadvisorCrawler.pipelines.TripadvisorcrawlerPipeline':300,
#    'myproject.pipeline.JsonWriterPipeline',
}