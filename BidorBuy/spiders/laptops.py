# -*- coding: utf-8 -*-
from scrapy import Spider
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from scrapy.selector import Selector
from scrapy.http import Request
from time import sleep
from datetime import datetime

# List of brands needed
types = ['Apple Laptops', 'Laptops & Notebooks']
# Day and hour of data
datestring = datetime.strftime(datetime.now(), '%Y-%m-%d-%H-%M-%S')

# Starting parameters
class SmartphonesSpider(Spider):
    name = "laptops"
    allowed_domains = ["www.bidorbuy.co.za"]
    start_urls = ['https://www.bidorbuy.co.za/jsp/category/Winners.jsp']
    custom_settings = {'FEED_FORMAT':'csv', 'FEED_URI': 'laptops '+str(datestring)+'.csv'}

    # Going into home page
    def start_requests(self):

        # List of products
        products = []

        self.driver = webdriver.Chrome('C:/Coding/chromedriver')
        sleep(5)
        self.driver.get('https://www.bidorbuy.co.za/jsp/category/Winners.jsp')
        sleep(5)

        # Choosing cellphones filter
        self.driver.find_element_by_link_text("Computers & Networking").click()
        sleep(5)

        # Choosing condition filter - secondhand
        self.driver.find_element_by_link_text("Secondhand").click()
        sleep(5)

        #Selecting apple or other laptops
        for type in types:

            self.driver.find_element_by_link_text("Laptops & Notebooks").click()
            self.driver.find_element_by_link_text(type).click()
            sleep(5)

            while True:
                try:
                    sel = Selector(text=self.driver.page_source)
                    items = sel.xpath('//*[@class="tradelist_title"]/a/@href').extract()

                    # Going through all items on page
                    for item in items:
                        products.append(item)
                        self.logger.info('ITEMS FOUND:' + str(len(products)))

                    # Pagination
                    next_page = self.driver.find_element_by_link_text('Next »')
                    self.logger.info('Sleeping for 3 seconds')
                    next_page.click()
                    sleep(3)

                except NoSuchElementException:
                    self.logger.info('No more pages to load.')
                    break

            # Getting details
            for product in products:
                yield Request(product, callback=self.parse_item)

    # Details of each offering
    def parse_item(self, response):
        title = response.xpath('//*[@class="item_title"]/text()').extract()
        url = response.request.url
        product = response.xpath('normalize-space(//*[@class="product_attribute_block"][text()])').extract()
        items_available = response.xpath('//@property="v:quantity"').extract()
        price = response.xpath("//div[@class='float_left']/div[@class='big_price']/span[@class='bigPriceText2']/text()").extract()
        winning_bid = response.xpath('normalize-space(//p[@class ="item_purchase_history"]/text())').extract()
        date = response.xpath('//*[@class="priceValidUntil"]/@content').extract()
        seller = response.xpath('//*[@class="seller_header"]/*[@class="strong"]/*[@class="user-summary"]/*[@class="alias"]/a/text()').extract()
        seller_page = response.xpath('//*[@class="seller_header"]/*[@class="strong"]/*[@class="user-summary"]/*[@class="alias"]/a/@href').extract()
        description = response.xpath (".//*[@class='description']//text()").extract()

        yield {'Title': title, 'URL': url, 'Product': product, 'Items Available': items_available, 'Final Price': price, 'Winning bid': winning_bid,
               'Date closed': date, 'Seller name': seller, 'Seller page': seller_page, 'Description': description}



