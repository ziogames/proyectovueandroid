from rest_framework import viewsets
from django.contrib.auth.models import User
from .models import Proveedor, Llaves, HistorialSalida, HistorialCompra
from .serializers import ProveedorSerializer, LlavesSerializer, UserSerializer, HistorialSalidaSerializer, HistorialCompraSerializer
from rest_framework.decorators import action
from django.db import transaction
from rest_framework.response import Response

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'])
    def update_profile(self, request):
        user = request.user
        if not hasattr(user, 'profile'):
             from .models import UserProfile
             UserProfile.objects.create(user=user)
        
        from .serializers import UserProfileSerializer
        profile_data = request.data
        serializer = UserProfileSerializer(user.profile, data=profile_data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer

class LlavesViewSet(viewsets.ModelViewSet):
    queryset = Llaves.objects.all()
    serializer_class = LlavesSerializer

    def get_queryset(self):
        queryset = Llaves.objects.all()
        proveedor_id = self.request.query_params.get('proveedor')
        if proveedor_id:
            queryset = queryset.filter(proveedor_id=proveedor_id)
        return queryset

    @action(detail=False, methods=['post'])
    def bulk_decrement(self, request):
        items = request.data.get('items', [])
        if not items:
            return Response({'error': 'No se proporcionaron items'}, status=400)
        
        try:
            with transaction.atomic():
                for item in items:
                    llave_id = item.get('id')
                    cantidad_a_restar = item.get('cantidad', 1)
                    
                    try:
                        llave = Llaves.objects.get(id=llave_id)
                        if llave.cantidad >= cantidad_a_restar:
                            llave.cantidad -= cantidad_a_restar
                            llave.save()

                            # Guardar en Historial
                            from .models import HistorialSalida
                            HistorialSalida.objects.create(
                                llave=llave,
                                user=request.user if request.user.is_authenticated else None,
                                cantidad=cantidad_a_restar
                            )
                        else:
                            return Response({'error': f'Stock insuficiente para la llave {llave.cod_llave}'}, status=400)
                    except Llaves.DoesNotExist:
                        return Response({'error': f'Llave con ID {llave_id} no encontrada'}, status=404)
            
            return Response({'status': 'Stock actualizado correctamente'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class HistorialSalidaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HistorialSalida.objects.all().order_by('-fecha')
    serializer_class = HistorialSalidaSerializer

    def get_queryset(self):
        queryset = HistorialSalida.objects.all().order_by('-fecha')
        user_id = self.request.query_params.get('user')
        fecha = self.request.query_params.get('fecha')

        if user_id and user_id != '':
            queryset = queryset.filter(user_id=user_id)
        if fecha and fecha != '':
            queryset = queryset.filter(fecha__date=fecha)
            
        return queryset

    @action(detail=False, methods=['post'])
    def bulk_increment(self, request):
        items = request.data.get('items', [])
        if not items:
            return Response({'error': 'No se proporcionaron items'}, status=400)
        
        try:
            with transaction.atomic():
                for item in items:
                    llave_id = item.get('id')
                    cantidad_a_sumar = item.get('cantidad', 1)
                    
                    try:
                        llave = Llaves.objects.get(id=llave_id)
                        llave.cantidad += cantidad_a_sumar
                        llave.save()

                        # Guardar en Historial de Compra con el precio actual
                        HistorialCompra.objects.create(
                            llave=llave,
                            proveedor=llave.proveedor,
                            cantidad=cantidad_a_sumar,
                            precio_pago=llave.precio_compra
                        )
                    except Llaves.DoesNotExist:
                        return Response({'error': f'Llave con ID {llave_id} no encontrada'}, status=404)
            
            return Response({'status': 'Stock recibido correctamente'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class HistorialCompraViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HistorialCompra.objects.all().order_by('-fecha')
    serializer_class = HistorialCompraSerializer

    def get_queryset(self):
        queryset = HistorialCompra.objects.all().order_by('-fecha')
        proveedor_id = self.request.query_params.get('proveedor')
        fecha = self.request.query_params.get('fecha')

        if proveedor_id and proveedor_id != '':
            queryset = queryset.filter(proveedor_id=proveedor_id)
        if fecha and fecha != '':
            queryset = queryset.filter(fecha__date=fecha)
            
        return queryset

from rest_framework.views import APIView
from rest_framework.response import Response
from .ai_service import ask_sql_assistant
from .image_comparison import compare_with_database
import os

class AIChatView(APIView):
    def post(self, request):
        question = request.data.get('question')
        if not question:
            return Response({'error': 'La pregunta es requerida'}, status=400)
        
        result = ask_sql_assistant(question)
        return Response(result)

class ImageComparisonView(APIView):
    """
    Endpoint para comparar una imagen cargada con las imágenes de llaves en la BD.
    POST: Carga una imagen y obtiene coincidencias
    """
    
    def post(self, request):
        """
        Compara una imagen cargada con todas las imágenes de llaves en la base de datos.
        
        Esperado:
        - uploaded_image: archivo de imagen en el request
        - threshold: (opcional) umbral de similitud (0-1, default: 0.6)
        
        Retorna:
        - Lista de coincidencias ordenadas por similitud
        """
        if 'uploaded_image' not in request.FILES:
            return Response({'error': 'Se requiere una imagen'}, status=400)
        
        try:
            uploaded_file = request.FILES['uploaded_image']
            threshold = float(request.data.get('threshold', 0.6))
            
            # Validar tipo de archivo
            valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            if file_ext not in valid_extensions:
                return Response({'error': 'Tipo de archivo no válido. Use JPG, PNG, BMP o TIFF'}, status=400)
            
            # Leer bytes de la imagen
            uploaded_image_bytes = uploaded_file.read()
            
            # Obtener todas las llaves con imágenes
            llaves = Llaves.objects.filter(img__isnull=False).exclude(img='')
            
            # Preparar lista de imágenes de la BD
            database_images = []
            for llave in llaves:
                try:
                    image_path = llave.img.path if llave.img else None
                    if image_path and os.path.exists(image_path):
                        database_images.append({
                            'id': llave.id,
                            'name': llave.cod_llave,
                            'path': image_path,
                            'image_url': llave.img.url if llave.img else None,
                            'proveedor': llave.proveedor.nombre if llave.proveedor else 'Desconocido',
                            'cantidad': llave.cantidad,
                            'precio_compra': float(llave.precio_compra)
                        })
                except Exception as e:
                    continue
            
            if not database_images:
                return Response({
                    'error': 'No hay imágenes de llaves disponibles en la base de datos',
                    'results': [],
                    'total': 0,
                    'matches': 0
                }, status=200)
            
            # Comparar imágenes
            comparison_result = compare_with_database(uploaded_image_bytes, database_images, threshold)
            
            return Response(comparison_result, status=200)
        
        except ValueError as e:
            return Response({'error': f'Error de validación: {str(e)}'}, status=400)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error en ImageComparisonView: {str(e)}")
            return Response({'error': f'Error al comparar imágenes: {str(e)}'}, status=500)
