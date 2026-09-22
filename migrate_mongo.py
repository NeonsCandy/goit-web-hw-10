import os
import django
from pymongo import MongoClient

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quotes_project.settings')
django.setup()

from quotes.models import Author, Quote, Tag  
def migrate_data():
    mongo_client = MongoClient("mongodb://localhost:27017")
    mongo_db = mongo_client["quotes_db"]  

    authors_collection = mongo_db["authors"]
    for author_data in authors_collection.find():
        Author.objects.get_or_create(
            fullname=author_data.get("fullname"),
            defaults={
                "born_date": author_data.get("born_date"),
                "born_location": author_data.get("born_location"),
                "description": author_data.get("description"),
            }
        )
    print("Авторів успішно перенесено.")

    quotes_collection = mongo_db["quotes"]
    for quote_data in quotes_collection.find():
        author_name = quote_data.get("author")
        author = Author.objects.filter(fullname=author_name).first()

        if author:
            quote, created = Quote.objects.get_or_create(
                text=quote_data.get("quote"),
                author=author
            )
            for tag_name in quote_data.get("tags", []):
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                quote.tags.add(tag)

    print("Цитати та теги успішно перенесено.")

if __name__ == '__main__':
    migrate_data()