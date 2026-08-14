import redis
import json
from models import Author, Quote

cache = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def search_quotes(command, value):
    cache_key = f"{command}:{value}"
    cached_result = cache.get(cache_key)
    
    if cached_result:
        print("Результат з кешу:")
        return json.loads(cached_result)
    result = []
    
    if command == 'name':
        authors = Author.objects(fullname__istartswith=value)
        for author in authors:
            quotes = Quote.objects(author=author)
            for q in quotes:
                result.append(q.quote)
                
    elif command == 'tag':
        quotes = Quote.objects(tags__istartswith=value)
        for q in quotes:
            result.append(q.quote) 
    elif command == 'tags':
        tags_list = value.split(',')
        quotes = Quote.objects(tags__in=tags_list)
        for q in quotes:
            result.append(q.quote)

    if result:
        cache.set(cache_key, json.dumps(result))
    return result

if __name__ == '__main__':
    while True:
        user_input = input("Введіть команду (name:..., tag:..., tags:..., exit): ").strip()
        if user_input == 'exit':
            break
            
        try:
            command, value = user_input.split(':', 1)
            command = command.strip()
            value = value.strip()
            
            if command in ['name', 'tag', 'tags']:
                quotes = search_quotes(command, value)
                if quotes:
                    for idx, q in enumerate(quotes, 1):
                        print(f"{idx}. {q}".encode('utf-8').decode('utf-8'))
                else:
                    print("Нічого не знайдено.")
            else:
                print("Невірна команда. Доступні: name, tag, tags, exit.")
        except ValueError:
            print("Формат команди має бути 'команда:значення'.")