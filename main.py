import json
import os
import scrapy
from scrapy.crawler import CrawlerProcess
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["quotes_db"]


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
    visited_authors = set()

    def parse(self, response):
        for quote in response.xpath("//div[@class='quote']"):
            author_link = quote.xpath("span/a/@href").get()
            if author_link and author_link not in self.visited_authors:
                self.visited_authors.add(author_link)
                yield scrapy.Request(
                    url=response.urljoin(author_link),
                    callback=self.parse_author
                )

        next_link = response.xpath("//li[@class='next']/a/@href").get()
        if next_link:
            yield scrapy.Request(url=response.urljoin(next_link))

    def parse_author(self, response):
        fullname = response.xpath("//h3[@class='author-title']/text()").get()
        born_date = response.xpath("//span[@class='author-born-date']/text()").get()
        born_location = response.xpath("//span[@class='author-born-location']/text()").get()
        description = response.xpath("//div[@class='author-description']/text()").get()

        yield {
            "fullname": fullname.strip() if fullname else "",
            "born_date": born_date.strip() if born_date else "",
            "born_location": born_location.strip() if born_location else "",
            "description": description.strip() if description else ""
        }


def load_data_to_mongo():
    """Завантажує зібрані Scrapy JSON-файли безпосередньо в MongoDB"""
    if os.path.exists("authors.json"):
        with open("authors.json", "r", encoding="utf-8") as f:
            authors_data = json.load(f)
            if authors_data:
                db.authors.drop()
                db.authors.insert_many(authors_data)
                print(f"До MongoDB імпортовано {len(authors_data)} авторів.")

    if os.path.exists("qoutes.json"):
        with open("qoutes.json", "r", encoding="utf-8") as f:
            quotes_data = json.load(f)
            if quotes_data:
                db.quotes.drop()
                db.quotes.insert_many(quotes_data)
                print(f"До MongoDB імпортовано {len(quotes_data)} цитат.")


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(QuotesSpider)
    process.crawl(AuthorsSpider)
    process.start()

    load_data_to_mongo()