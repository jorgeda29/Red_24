from django.urls import path
from . import views

urlpatterns = [
    # URLs existentes
    path('', views.terminal_view, name='terminal'),
    path('api/producto/<str:codigo_barras>/', views.buscar_producto_por_codigo, name='buscar_producto'),
    path('api/registrar_venta/', views.registrar_venta, name='registrar_venta'),

    # --- AÑADE ESTA NUEVA LÍNEA AQUÍ ---
    path('api/buscar_productos/', views.api_buscar_productos, name='api_buscar_productos'),

    # URLs de pedidos a cocina (estas van después)
    path('cocina/', views.cocina_view, name='cocina'),
    path('caja/pedidos/', views.caja_pedidos_view, name='caja_pedidos'),
    path('api/pedidos/', views.api_pedidos_cocina, name='api_pedidos'),
    path('api/pedidos/crear/', views.api_crear_pedido, name='api_crear_pedido'),
    path('api/pedidos/marcar_listo/<int:pedido_id>/', views.api_marcar_listo, name='api_marcar_listo'),
    path('api/pedidos/marcar_entregado/<int:pedido_id>/', views.api_marcar_entregado, name='api_marcar_entregado'),
    path('api/pedidos/marcar_notificado/<int:pedido_id>/', views.api_marcar_notificado, name='api_marcar_notificado'),
]