import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import Producto, Venta, DetalleVenta

def terminal_view(request):
    """
    Renderiza la página principal del terminal de venta.
    """
    # CORRECCIÓN: Se especifica la ruta completa del template dentro de la carpeta de la app.
    return render(request, 'ventas/terminal_de_venta.html')

def buscar_producto_por_codigo(request, codigo_barras):
    """
    API endpoint para buscar un producto por su código de barras.
    Devuelve los datos del producto en formato JSON.
    """
    try:
        producto = Producto.objects.get(codigo_barras=codigo_barras)
        if producto.stock > 0:
            data = {
                'id': producto.id,
                'nombre': producto.nombre,
                'precio': str(producto.precio),
                'stock': producto.stock,
            }
            return JsonResponse(data)
        else:
            return JsonResponse({'error': 'Producto sin stock'}, status=404)
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)

@csrf_exempt # Desactivar CSRF para esta API, en producción usar un método más seguro.
@transaction.atomic # Asegura que todas las operaciones de DB se completen o ninguna lo haga.
def registrar_venta(request):
    """
    API endpoint para registrar una nueva venta.
    Recibe un JSON con los productos y sus cantidades.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items_venta = data.get('items', [])
            
            if not items_venta:
                return JsonResponse({'error': 'La venta no tiene productos'}, status=400)

            # 1. Crear la venta
            nueva_venta = Venta.objects.create()
            total_venta = 0

            # 2. Procesar cada item
            for item in items_venta:
                producto_id = item.get('id')
                cantidad = int(item.get('cantidad', 1))

                producto = Producto.objects.select_for_update().get(id=producto_id)

                if producto.stock < cantidad:
                    raise Exception(f'Stock insuficiente para {producto.nombre}')

                # 3. Crear el detalle de la venta
                DetalleVenta.objects.create(
                    venta=nueva_venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio
                )

                # 4. Actualizar el stock del producto
                producto.stock -= cantidad
                producto.save()
                
                total_venta += producto.precio * cantidad

            # 5. Actualizar el total de la venta
            nueva_venta.total = total_venta
            nueva_venta.save()
            
            return JsonResponse({'success': 'Venta registrada correctamente', 'venta_id': nueva_venta.id}, status=201)

        except Producto.DoesNotExist:
            transaction.set_rollback(True)
            return JsonResponse({'error': 'Uno de los productos no existe'}, status=400)
        except Exception as e:
            transaction.set_rollback(True)
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

from .models import PedidoCocina # Asegúrate de importar el nuevo modelo al principio del archivo

# Vistas para las páginas HTML
def cocina_view(request):
    """ Muestra la interfaz para la cocina. """
    return render(request, 'ventas/cocina.html')

def caja_pedidos_view(request):
    """ Muestra la interfaz para que la caja gestione y cree pedidos. """
    return render(request, 'ventas/caja_pedidos.html')

# API Endpoints para la comunicación en tiempo real
def api_pedidos_cocina(request):
    """ Devuelve la lista de pedidos pendientes y listos en formato JSON. """
    pedidos = PedidoCocina.objects.filter(estado__in=['PENDIENTE', 'LISTO']).values()
    return JsonResponse(list(pedidos), safe=False)

@csrf_exempt
def api_crear_pedido(request):
    """ Crea un nuevo pedido desde la caja. """
    if request.method == 'POST':
        data = json.loads(request.body)
        descripcion = data.get('descripcion')
        if descripcion:
            PedidoCocina.objects.create(descripcion=descripcion)
            return JsonResponse({'success': 'Pedido creado'})
    return JsonResponse({'error': 'Petición inválida'}, status=400)

@csrf_exempt
def api_marcar_listo(request, pedido_id):
    """ La cocina marca un pedido como listo. """
    try:
        pedido = PedidoCocina.objects.get(id=pedido_id)
        pedido.estado = 'LISTO'
        pedido.save()
        return JsonResponse({'success': 'Pedido marcado como listo'})
    except PedidoCocina.DoesNotExist:
        return JsonResponse({'error': 'Pedido no encontrado'}, status=404)
        
@csrf_exempt
def api_marcar_entregado(request, pedido_id):
    """ La caja marca un pedido como entregado (lo saca de la vista). """
    try:
        pedido = PedidoCocina.objects.get(id=pedido_id)
        pedido.estado = 'ENTREGADO'
        pedido.save()
        return JsonResponse({'success': 'Pedido marcado como entregado'})
    except PedidoCocina.DoesNotExist:
        return JsonResponse({'error': 'Pedido no encontrado'}, status=404)

@csrf_exempt
def api_marcar_notificado(request, pedido_id):
    """ La caja marca un pedido como notificado para que no vuelva a sonar la alarma. """
    try:
        pedido = PedidoCocina.objects.get(id=pedido_id)
        pedido.notificado_caja = True
        pedido.save()
        return JsonResponse({'success': 'Pedido marcado como notificado'})
    except PedidoCocina.DoesNotExist:
        return JsonResponse({'error': 'Pedido no encontrado'}, status=404)

from django.db.models import Q # Asegúrate de añadir esta importación al principio del archivo

def api_buscar_productos(request):
    """
    API para buscar productos por nombre o código de barras.
    Acepta un parámetro 'q' en la URL.
    """
    query = request.GET.get('q', None)
    productos = []
    if query:
        # Buscamos si el 'query' está contenido en el nombre O en el código de barras
        # '__icontains' significa que no distingue mayúsculas/minúsculas
        productos = Producto.objects.filter(
            Q(nombre__icontains=query) | Q(codigo_barras__icontains=query),
            stock__gt=0 # Solo productos con stock > 0
        ).values('id', 'nombre', 'codigo_barras', 'precio', 'stock')[:10] # Devolvemos máximo 10 resultados
    
    return JsonResponse(list(productos), safe=False)
