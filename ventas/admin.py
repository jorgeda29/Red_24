from django.contrib import admin
from .models import Producto, Venta, DetalleVenta, PedidoCocina

# Creamos una vista más detallada para los productos en el admin
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo_barras', 'precio', 'stock')
    search_fields = ('nombre', 'codigo_barras')

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0 # No mostrar extras para añadir
    readonly_fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal') # Solo lectura

class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_hora', 'total')
    inlines = [DetalleVentaInline] # Muestra los detalles dentro de la venta
    readonly_fields = ('fecha_hora', 'total')

class PedidoCocinaAdmin(admin.ModelAdmin):
    list_display = ('id', 'descripcion', 'estado', 'fecha_hora_creacion')
    list_filter = ('estado',)

# Registramos los modelos con sus configuraciones personalizadas
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Venta, VentaAdmin)
admin.site.register(PedidoCocina, PedidoCocinaAdmin)
