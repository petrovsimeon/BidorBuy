# -*- coding: utf-8 -*-
from scrapy import Spider
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from scrapy.selector import Selector
from scrapy.http import Request
from time import sleep
from datetime import datetime

# List of brands needed
types = ['Apple Laptops']
# Day and hour of data
datestring = datetime.strftime(datetime.now(), '%Y-%m-%d-%H-%M-%S')

# Starting parameters
class SmartphonesSpider(Spider):
    name = "laptops"
    allowed_domains = ["www.bidorbuy.co.za"]
    start_urls = ['https://www.bidorbuy.co.za/jsp/category/Winners.jsp']
    driver = webdriver.Chrome('C:/Coding/chromedriver')
    custom_settings = {'FEED_FORMAT':'csv', 'FEED_URI': 'laptops '+str(datestring)+'.csv'}

    # Going into home page
    def start_requests(self):
        self.driver = webdriver.Chrome('C:/Coding/chromedriver')
        self.driver.get('https://www.bidorbuy.co.za/jsp/category/Winners.jsp')

        # Choosing cellphones filter
        self.driver.find_element_by_link_text("Computers & Networking").click()
        sleep(5)
        self.driver.find_element_by_link_text("Laptops & Notebooks").click()
        sleep(5)

        # Choosing condition filter - secondhand
        self.driver.find_element_by_link_text("Secondhand").click()
        sleep(5)

        #Selecting apple or other laptops
        for type in types:

            self.driver.find_element_by_link_text(type).click()
            sleep(5)

            sel = Selector(text=self.driver.page_source)

            items = sel.xpath('//*[@class="tradelist_title"]/a/@href').extract()

            # Going through all items on page
            for item in items:
                url = item
                yield Request(url, callback=self.parse_item)

            # Pagination
            while True:
                try:
                    next_page = self.driver.find_element_by_link_text('Next »').click()
                    sleep(3)
                    self.logger.info ('Sleeping for 3 seconds')
                    next_page.click()

                except NoSuchElementException:
                    self.logger.info('No more pages to load.')
                    break


            # Removing Apple Laptops Filters so that other brands can be chosen
            self.driver.find_element_by_link_text('Laptops & Notebooks').click()
            sleep(5)

    # Details of each offering
    def parse_item(self, response):
        title = response.xpath('//*[@class="item_title"]/text()').extract()
        url = response.request.url
        product = response.xpath('//*[@class="product_attribute_block"]/text()').extract()
        items_available = response.xpath('//@property="v:quantity"').extract()
        price = response.xpath("//div[@class='float_left']/div[@class='big_price']/span[@class='bigPriceText2']/text()").extract()
        date = response.xpath('//*[@class="priceValidUntil"]/@content').extract()
        seller = response.xpath('//*[@class="seller_header"]/*[@class="strong"]/*[@class="user-summary"]/*[@class="alias"]/a/text()').extract()
        seller_page = response.xpath('//*[@class="seller_header"]/*[@class="strong"]/*[@class="user-summary"]/*[@class="alias"]/a/@href').extract()
        description = response.xpath ("//*[@class='description']//text()").extract()

        yield {'Title': title, 'URL': url, 'Product': product, 'Items Available': items_available, 'Final Price': price,
               'Date closed': date, 'Seller name': seller, 'Seller page': seller_page, 'Description': description}


