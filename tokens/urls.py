from django.urls import path
from . import views

app_name = 'tokens'

urlpatterns = [
    path('event/<int:pk>', views.token, name='token_event'),
    path('print_token/<int:num>/<int:pk>', views.print_token, name='print_token'),
    path('generate_tokens/', views.generate_tokens, name='generate_tokens'),
    path('update_print_status/', views.update_print_status, name='update_print_status'),
    path('scanner_dist/<int:pk>', views.scanner_dist, name='scanner_dist'),
    path('scanner_receive/<int:pk>', views.scanner_receive, name='scanner_receive'),
    path('token_activate/', views.token_activate, name='token_activate'),
    path('token_activate_new/', views.token_activate_new, name='token_activate_new'),
    path('token_receive/', views.token_receive, name='token_receive'),
]