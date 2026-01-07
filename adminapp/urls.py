from django.urls import path
from adminapp import views

urlpatterns = [
    path('index_page/', views.index_page, name='index_page'),
    path('login_page/', views.login_page, name='login_page'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('view_messages/', views.view_messages, name='view_messages'),
    path('view_users/', views.view_users, name='view_users'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('view_watchlist/', views.view_watchlist, name='view_watchlist'),
    path('delete_watchlist/<int:item_id>/', views.delete_watchlist_item, name='delete_watchlist_item'),


]
