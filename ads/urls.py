from django.urls import path
from . import views
from .views import signup

urlpatterns = [
    path('', views.ad_list, name='ad_list'),
    path('signup/', signup, name='signup'),

    path('ads/<int:ad_id>/', views.ad_detail, name='ad_detail'),
    path('ads/create/', views.ad_create, name='ad_create'),
    path('ads/<int:ad_id>/edit/', views.ad_edit, name='ad_edit'),
    path('ads/<int:ad_id>/delete/', views.ad_delete, name='ad_delete'),

    path('proposals/', views.proposal_list, name='proposal_list'),
    path('proposals/create/', views.proposal_create, name='proposal_create'),
    path('proposals/<int:proposal_id>/update/', views.proposal_update, name='proposal_update'),

]
