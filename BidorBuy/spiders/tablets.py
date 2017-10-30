# -*- coding: utf-8 -*-
from scrapy import Spider
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from scrapy.selector import Selector
from scrapy.http import Request
from time import sleep
from datetime import datetime

# List of brands needed
brands = ['Apple', 'Samsung']
# Day and hour of data
datestring = datetime.strftime(datetime.now(), '%Y-%m-%d-%H-%M-%S')

# Starting parameters
class SmartphonesSpider(Spider):
    name = "tablets"
    allowed_domains = ["www.bidorbuy.co.za"]
    start_urls = ['https://www.bidorbuy.co.za/jsp/category/Winners.jsp']
    driver = webdriver.Chrome('C:/Coding/chromedriver')
    custom_settings = {'FEED_FORMAT':'csv', 'FEED_URI':'tablets '+str(datestring)+'.csv'}

    # Going into home page
    def start_requests(self):
        self.driver = webdriver.Chrome('C:/Coding/chromedriver')
        sleep (5)
        self.driver.get('https://www.bidorbuy.co.za/jsp/category/Winners.jsp')
        sleep (5)

        # Choosing cellphones filter
        self.driver.find_element_by_link_text("Computers & Networking").click()
        sleep(5)
        self.driver.find_element_by_link_text("iPads, Tablets & eReaders").click()
        sleep(5)
        self.driver.find_element_by_link_text ("Devices").click()
        sleep (5)

        # Choosing condition filter - secondhand
        self.driver.find_element_by_link_text("Secondhand").click()
        sleep(5)

        #Selecting each brand from brand list
        for brand in brands:

            self.driver.find_element_by_link_text(brand).click()
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


            # Removing brand filter so that the next brand filter can be chosen
            self.driver.find_element_by_link_text(brand).click()
            sleep(5)

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


