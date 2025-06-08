from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('query_results/', views.query_results_view, name='query_results'),
    path('add_new_app/', views.add_new_app_view, name='add_new_app'),
    path('install_app/', views.install_app_view, name='install_app'),

    path('delete_app/', views.delete_app_view, name='delete_app'),

]
