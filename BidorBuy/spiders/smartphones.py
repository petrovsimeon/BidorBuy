# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from scrapy.selector import Selector
from scrapy.http import Request
from time import sleep


class SmartphonesSpider(scrapy.Spider):
    name = "smartphones"
    allowed_domains = ["www.bidorbuy.co.za"]
    start_urls = ['https://www.bidorbuy.co.za/jsp/category/Winners.jsp']
    driver = webdriver.Chrome('C:/Coding/chromedriver')

    def start_requests(self):
        self.driver = webdriver.Chrome('C:/Coding/chromedriver')
        self.driver.get('https://www.bidorbuy.co.za/jsp/category/Winners.jsp')
        self.driver.find_element_by_link_text("Cell Phones & Accessories").click()
        sleep(5)
        self.driver.find_element_by_link_text("Cell Phones & Smartphones").click()
        sleep(5)

        sel = Selector(text=self.driver.page_source)

        items = sel.xpath('//*[@class="tradelist_title"]/a/@href').extract()

        for item in items:
            url = item
            yield Request(url, callback=self.parse_item)

    def parse_item(self, response):
        title = response.xpath('//*[@class="item_title"]/text()').extract()
        url = response.request.url
        yield {'title': title, 'url': url}

