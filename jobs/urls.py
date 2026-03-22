from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('quick-load-posting/', views.quick_load_posting, name='quick_load_posting'),
    path('quick-load-posting/<int:pk>/edit/', views.quick_load_posting, name='quick_load_posting_edit'),
    path('load-list/', views.load_list, name='load_list'),
    path('<int:pk>/detail/', views.job_detail, name='job_detail'),
    path('<int:pk>/cancel/', views.cancel_job, name='cancel_job'),
    path('unconnected/', views.unconnected_list, name='unconnected_list'),
    path('export-csv/', views.export_csv, name='export_csv'),
    path('api/customer-search/', views.customer_search_api, name='customer_search_api'),
]
