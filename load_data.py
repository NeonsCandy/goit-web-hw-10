import json
from models import Author, Quote

def load_authors():
    with open('authors.json', 'r', encoding='utf-8') as f:
        authors = json.load(f)
        for author_data in authors:
            Author(
                fullname=author_data['fullname'],
                born_date=author_data['born_date'],
                born_location=author_data['born_location'],
                description=author_data['description']
            ).save()

def load_quotes():
    with open('qoutes.json', 'r', encoding='utf-8') as f:
        quotes = json.load(f)
        for quote_data in quotes:
            author = Author.objects(fullname=quote_data['author']).first()
            if author:
                Quote(
                    tags=quote_data['tags'],
                    author=author,
                    quote=quote_data['quote']
                ).save()

if __name__ == '__main__':
    Quote.drop_collection()
    Author.drop_collection()
    
    load_authors()
    load_quotes()
    print("Дані завантажено")