from django.urls import path
from . import views


urlpatterns = [
    path('books/', views.book_list_create_api_view),
    path('order-create/', views.order_create_api_view),
    path('author-detail/<int:pk>/', views.author_detail_api_view),
]