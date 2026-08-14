import scrapy
from scrapy.crawler import CrawlerProcess

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    custom_settings = {
        "FEEDS": {
            "qoutes.json": {"format": "json", "encoding": "utf8", "overwrite": True}
        }
    }
    start_urls = ["http://quotes.toscrape.com/"]

    def parse(self, response):
        for quote in response.xpath("//div[@class='quote']"):
            tags = quote.xpath("div[@class='tags']/a/text()").extract()
            author = quote.xpath("span/small/text()").get()
            quote_text = quote.xpath("span[@class='text']/text()").get()

            yield {
                "tags": tags,
                "author": author,
                "quote": quote_text
            }
        next_link = response.xpath("//li[@class='next']/a/@href").get()
        if next_link:
            yield scrapy.Request(url=response.urljoin(next_link))

class AuthorsSpider(scrapy.Spider):
    name = "authors"
    custom_settings = {
        "FEEDS": {
            "authors.json": {"format": "json", "encoding": "utf8", "overwrite": True}
        }
    }
    start_urls = ["http://quotes.toscrape.com/"]

    def parse(self, response):
        for quote in response.xpath("//div[@class='quote']"):
            author_link = quote.xpath("span/a/@href").get()
            yield scrapy.Request(url=response.urljoin(author_link), callback=self.parse_author)
        
        next_link = response.xpath("//li[@class='next']/a/@href").get()
        if next_link:
            yield scrapy.Request(url=response.urljoin(next_link))

    def parse_author(self, response):
        fullname = response.xpath("//h3[@class='author-title']/text()").get().strip()
        born_date = response.xpath("//span[@class='author-born-date']/text()").get().strip()
        born_location = response.xpath("//span[@class='author-born-location']/text()").get().strip()
        description = response.xpath("//div[@class='author-description']/text()").get().strip()
        
        yield {
            "fullname": fullname,
            "born_date": born_date,
            "born_location": born_location,
            "description": description
        }

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(QuotesSpider)
    process.crawl(AuthorsSpider)
    process.start()