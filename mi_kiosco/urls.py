from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ventas.urls')), # Añadir esta línea para conectar la app 'ventas'
]