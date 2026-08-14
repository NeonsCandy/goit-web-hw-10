import os
import django
import json
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quotes_project.settings")
django.setup()
from quotes.models import Author, Quote, Tag
def load_data():
    with open('authors.json', 'r', encoding='utf-8') as f:
        authors = json.load(f)
        for item in authors:
            Author.objects.get_or_create(
                fullname=item['fullname'],
                born_date=item['born_date'],
                born_location=item['born_location'],
                description=item['description']
            )
            
    with open('qoutes.json', 'r', encoding='utf-8') as f:
        quotes = json.load(f)
        for item in quotes:
            author = Author.objects.filter(fullname=item['author']).first()
            if author:
                quote, created = Quote.objects.get_or_create(
                    text=item['quote'],
                    author=author
                )
                for tag_name in item['tags']:
                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                    quote.tags.add(tag)

if __name__ == '__main__':
    load_data()
    print("Дані мігровано")