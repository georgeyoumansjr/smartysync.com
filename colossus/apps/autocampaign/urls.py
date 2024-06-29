from django.urls import path

from . import views

app_name = 'autocampaign'


urlpatterns = [
    path('', views.AutoCampaignListView.as_view(), name='autocampaign_list'),
    path('add/', views.AutoCampaignCreateView.as_view(), name='autocampaign_add'),
    path('confirm/send/<int:pk>/', views.confim_send, name='autocampaign_confirm_send'),
    # path('send/<int:pk>/',views.auto_campaign_send,name='autocampaign_send'),
    path('<int:pk>/delete/', views.AutoCampaignDeleteView.as_view(), name='autocampaign_delete'),
    path('<int:pk>/', views.AutoCampaignDetailView.as_view(), name='autocampaign_detail'),
#     path('<int:pk>/edit/', views.EmailTemplateUpdateView.as_view(), name='emailtemplate_edit'),
#     path('<int:pk>/preview/', views.email_template_preview, name='emailtemplate_preview'),
#     path('<int:pk>/autosave/', views.email_template_autosave, name='emailtemplate_autosave'),
#     path('<int:pk>/delete/', views.EmailTemplateDeleteView.as_view(), name='emailtemplate_delete')
]
