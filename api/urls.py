# from django.urls import path
# from . import views

# urlpatterns = [
#     path('get-product/', views.get_product, name='get_product'),
#     path('add-product/', views.add_product, name='add_product'),
# ]

from django.contrib import admin
from django.urls import path,include

urlpatterns = [

path('admin/', admin.site.urls),

path('api/users/',include('users.urls')),

path('api/',include('products.urls')),

]