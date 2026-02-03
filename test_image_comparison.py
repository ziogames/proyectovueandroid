"""
Script de prueba para el endpoint de comparación de imágenes.
Ejecutar desde la raíz del proyecto Django.

Uso:
    python test_image_comparison.py
"""

import os
import django
from django.core.files.base import ContentFile

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client
from api.models import Llaves, Proveedor
import io

def test_image_comparison():
    """Prueba el endpoint de comparación de imágenes."""
    
    client = Client()
    
    # Crear un usuario de prueba y autenticar
    from django.contrib.auth.models import User
    from rest_framework_simplejwt.tokens import RefreshToken
    
    # Crear usuario si no existe
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
    
    # Obtener token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    # Crear proveedor de prueba
    proveedor, _ = Proveedor.objects.get_or_create(
        nombre='Proveedor Test',
        defaults={
            'direccion': 'Test',
            'telefono': '123456789',
            'correo': 'test@provider.com'
        }
    )
    
    # Crear algunas llaves con imágenes de prueba
    print("Creando llaves de prueba...")
    
    # Crear imagen de prueba simple (1x1 píxel azul)
    from PIL import Image
    
    test_image = Image.new('RGB', (100, 100), color='blue')
    image_bytes = io.BytesIO()
    test_image.save(image_bytes, format='PNG')
    image_bytes.seek(0)
    
    # Crear llave 1
    llave1, _ = Llaves.objects.get_or_create(
        cod_llave='LK001',
        proveedor=proveedor,
        defaults={
            'cantidad': 50,
            'precio_compra': 1.99
        }
    )
    
    # Crear llave 2
    test_image2 = Image.new('RGB', (100, 100), color='red')
    image_bytes2 = io.BytesIO()
    test_image2.save(image_bytes2, format='PNG')
    image_bytes2.seek(0)
    
    llave2, _ = Llaves.objects.get_or_create(
        cod_llave='LK002',
        proveedor=proveedor,
        defaults={
            'cantidad': 30,
            'precio_compra': 2.50
        }
    )
    
    # Agregar imágenes
    if not llave1.img or llave1.img.name == '':
        llave1.img.save('test_key_1.png', ContentFile(image_bytes.getvalue()), save=True)
    
    if not llave2.img or llave2.img.name == '':
        llave2.img.save('test_key_2.png', ContentFile(image_bytes2.getvalue()), save=True)
    
    print(f"✓ Llave 1 (LK001) creada con imagen")
    print(f"✓ Llave 2 (LK002) creada con imagen")
    
    # Preparar imagen de prueba para comparación
    test_upload_image = Image.new('RGB', (100, 100), color='blue')
    upload_bytes = io.BytesIO()
    test_upload_image.save(upload_bytes, format='PNG')
    upload_bytes.seek(0)
    upload_bytes.name = 'test_upload.png'
    
    # Hacer request
    print("\nHaciendo request al endpoint /api/images/compare/...")
    
    from django.test import Client
    from django.files.uploadedfile import SimpleUploadedFile
    
    client = Client()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    # Crear archivo subido
    uploaded_file = SimpleUploadedFile(
        "test.png",
        upload_bytes.getvalue(),
        content_type="image/png"
    )
    
    response = client.post(
        '/api/images/compare/',
        {'uploaded_image': uploaded_file, 'threshold': 0.5},
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ Comparación exitosa!")
        print(f"  - Total de resultados: {data.get('total', 0)}")
        print(f"  - Coincidencias encontradas: {data.get('matches', 0)}")
        if data.get('results'):
            print(f"\nPrimeros resultados:")
            for result in data['results'][:3]:
                print(f"  - {result['name']}: {result['similarity']*100:.1f}% similitud")
    else:
        print(f"✗ Error en la comparación")

if __name__ == '__main__':
    try:
        test_image_comparison()
        print("\n✓ Prueba completada exitosamente!")
    except Exception as e:
        print(f"\n✗ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
