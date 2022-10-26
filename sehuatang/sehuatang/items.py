# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SehuatangItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    number = scrapy.Field()
    date = scrapy.Field()
    tid = scrapy.Field()
    img = scrapy.Field()
    post_time = scrapy.Field()
    magnet = scrapy.Field()
    f_id = scrapy.Field()
    f_id_page = scrapy.Field()  # tid所在页数
