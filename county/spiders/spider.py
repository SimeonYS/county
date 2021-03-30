import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import CountyItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class CountySpider(scrapy.Spider):
	name = 'county'
	start_urls = ['https://firstcountybank.com/resources/news/']

	def parse(self, response):
		post_links = response.xpath('//p[@class="t-entry-readmore btn-container"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//li[@class="page-next"]/a/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):
		date = response.xpath('//div[@class="date-info"]/text()').get()
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="post-content style-light double-bottom-padding"]//text()[not (ancestor::div[@class="post-title-wrapper"] or ancestor::em)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=CountyItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
