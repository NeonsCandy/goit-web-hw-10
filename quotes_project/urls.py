from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from quotes import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('tag/<str:tag_name>/', views.tag_detail, name='tag_detail'),
    path('author/<int:pk>/', views.author_detail, name='author_detail'),
    
    path('add-author/', views.add_author, name='add_author'),
    path('add-quote/', views.add_quote, name='add_quote'),
    
    path('scrape/', views.scrape_data, name='scrape_data'),
    
    
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]