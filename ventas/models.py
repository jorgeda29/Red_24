from django.db import models
from django.utils import timezone

class Producto(models.Model):
    nombre = models.CharField(max_length=200, help_text="Nombre del producto")
    codigo_barras = models.CharField(max_length=100, unique=True, help_text="Código de barras único del producto")
    precio = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio de venta al público")
    stock = models.PositiveIntegerField(default=0, help_text="Cantidad actual en inventario")

    def __str__(self):
        return f"{self.nombre} (${self.precio})"

class Venta(models.Model):
    fecha_hora = models.DateTimeField(default=timezone.now, help_text="Fecha y hora en que se realizó la venta")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Monto total de la venta")

    def __str__(self):
        return f"Venta #{self.id} - ${self.total} - {self.fecha_hora.strftime('%Y-%m-%d %H:%M')}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT) # Evita borrar productos si tienen ventas
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio del producto al momento de la venta")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} en Venta #{self.venta.id}"
class PedidoCocina(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('LISTO', 'Listo para retirar'),
        ('ENTREGADO', 'Entregado'),
    ]
    
    descripcion = models.CharField(max_length=255, help_text="Descripción del pedido, ej: Sandwich Milanesa Completo")
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='PENDIENTE')
    fecha_hora_creacion = models.DateTimeField(auto_now_add=True)
    notificado_caja = models.BooleanField(default=False, help_text="Indica si la caja ya fue notificada con la alarma")

    def __str__(self):
        return f"Pedido #{self.id}: {self.descripcion} ({self.estado})"

    class Meta:
        ordering = ['fecha_hora_creacion'] # Los pedidos más antiguos primero
    