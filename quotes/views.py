from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib.auth.forms import UserCreationForm
from .models import Quote, Author, Tag
from .forms import AuthorForm, QuoteForm
import requests
from bs4 import BeautifulSoup

def index(request):
    quotes_list = Quote.objects.all()
    
    paginator = Paginator(quotes_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    top_tags = Tag.objects.annotate(num_quotes=Count('quote')).order_by('-num_quotes')[:10]

    return render(request, 'quotes/index.html', {'page_obj': page_obj, 'top_tags': top_tags})

def tag_detail(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    quotes = Quote.objects.filter(tags=tag)
    return render(request, 'quotes/tag_detail.html', {'tag': tag, 'quotes': quotes})

def author_detail(request, pk):
    author = get_object_or_404(Author, pk=pk)
    return render(request, 'quotes/author_detail.html', {'author': author})

@login_required
def add_author(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = AuthorForm()
    return render(request, 'quotes/add_author.html', {'form': form})

@login_required
def add_quote(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = QuoteForm()
    return render(request, 'quotes/add_quote.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def scrape_data(request):
    url = "http://quotes.toscrape.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    for quote_block in soup.find_all('div', class_='quote'):
        text = quote_block.find('span', class_='text').text
        author_name = quote_block.find('small', class_='author').text
        tags = [tag.text for tag in quote_block.find_all('a', class_='tag')]
        
        author, _ = Author.objects.get_or_create(fullname=author_name)
        quote, _ = Quote.objects.get_or_create(text=text, author=author)
        
        for tag_name in tags:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            quote.tags.add(tag)
            
    return redirect('index')