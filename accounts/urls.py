from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('select-branch/', views.select_branch, name='select_branch'),
    path('switch-branch/', views.switch_branch, name='switch_branch'),
]
