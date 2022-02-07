from django.urls import path
from . import views

app_name    = "finance"
urlpatterns = [
    path('', views.index, name="index"),
    path('category',views.category,name="category"),
    path('category_edit/<int:pk>', views.category_edit, name="category_edit"),
    path('category_delete/<int:pk>', views.category_delete, name="category_delete"),
    path('balance_delete/<int:pk>', views.balance_delete, name="balance_delete"),
]
