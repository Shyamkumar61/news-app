from django.urls import path
from apps.account.apis import views

urlpatterns = [
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('sign-up', views.AccountCreateView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('users/', views.UserListView.as_view(), name='users'),
    path('profile/<str:username>', views.ProfilAPIView.as_view(), name='profile'),
]