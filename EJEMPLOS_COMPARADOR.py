"""
EJEMPLOS DE USO - Comparador de Imágenes

Este archivo contiene ejemplos de cómo usar el Comparador de Imágenes
en diferentes contextos.
"""

# =============================================================================
# EJEMPLO 1: Uso desde Python (Backend)
# =============================================================================

from api.image_comparison import ImageComparator, compare_with_database
import os

# Crear comparador
comparator = ImageComparator(threshold=0.6)

# Ejemplo A: Cargar desde archivo
image_path = "media/llaves_img/ejemplo.jpg"
img = comparator.load_image_from_file(image_path)

# Ejemplo B: Cargar desde bytes
with open("imagen_local.jpg", "rb") as f:
    image_bytes = f.read()
img = comparator.load_image_from_bytes(image_bytes)

# Ejemplo C: Extraer características
kp, des, gray = comparator.extract_features(img)
print(f"Características encontradas: {len(kp) if kp else 0}")

# Ejemplo D: Comparar dos imágenes
from api.models import Llaves
llave1 = Llaves.objects.get(cod_llave="LK001")
llave2 = Llaves.objects.get(cod_llave="LK002")

img1 = comparator.load_image_from_file(llave1.img.path)
img2 = comparator.load_image_from_file(llave2.img.path)

result = comparator.compare_images(img1, img2)
print(f"Similitud: {result['similarity']*100:.1f}%")
print(f"Es coincidencia: {result['is_match']}")


# =============================================================================
# EJEMPLO 2: Uso desde API REST (HTTP)
# =============================================================================

import requests
import os

# URL del servidor
BASE_URL = "http://localhost:8000/api"
TOKEN = "tu_token_jwt_aqui"

# Headers con autenticación
headers = {
    "Authorization": f"Bearer {TOKEN}"
}

# Preparar archivo
files = {
    'uploaded_image': open('imagen_prueba.jpg', 'rb')
}
data = {
    'threshold': '0.6'
}

# Hacer request
response = requests.post(
    f"{BASE_URL}/images/compare/",
    files=files,
    data=data,
    headers=headers
)

# Procesar respuesta
if response.status_code == 200:
    results = response.json()
    print(f"Total de resultados: {results['total']}")
    print(f"Coincidencias encontradas: {results['matches']}")
    
    for result in results['results'][:5]:  # Mostrar top 5
        print(f"\n{result['name']}")
        print(f"  Similitud: {result['similarity']*100:.1f}%")
        print(f"  Proveedor: {result['proveedor']}")
        print(f"  Stock: {result['cantidad']}")
else:
    print(f"Error: {response.status_code}")
    print(response.json())


# =============================================================================
# EJEMPLO 3: Uso desde cURL (Terminal)
# =============================================================================

"""
# Obtener token JWT primero
TOKEN=$(curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}' \
  | grep -o '"access":"[^"]*' | cut -d'"' -f4)

# Comparar imagen
curl -X POST http://localhost:8000/api/images/compare/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "uploaded_image=@imagen_prueba.jpg" \
  -F "threshold=0.6"
"""


# =============================================================================
# EJEMPLO 4: Uso desde JavaScript/TypeScript (Frontend)
# =============================================================================

"""
// typescript/javascript

import api from '@/services/api'

async function compareImages(imageFile: File, threshold: number = 0.6) {
    const formData = new FormData()
    formData.append('uploaded_image', imageFile)
    formData.append('threshold', threshold.toString())
    
    try {
        const response = await api.post('/images/compare/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
        
        console.log('Resultados:', response.data)
        return response.data
    } catch (error) {
        console.error('Error:', error)
        throw error
    }
}

// Uso
const input = document.querySelector('input[type="file"]') as HTMLInputElement
const file = input.files?.[0]

if (file) {
    const results = await compareImages(file, 0.6)
    results.results.forEach(result => {
        console.log(`${result.name}: ${(result.similarity * 100).toFixed(1)}%`)
    })
}
"""


# =============================================================================
# EJEMPLO 5: Procesamiento por lotes (Batch Processing)
# =============================================================================

from api.image_comparison import compare_with_database
from api.models import Llaves
import os

def compare_multiple_images(image_folder):
    """
    Compara múltiples imágenes contra la BD.
    """
    
    # Obtener todas las llaves con imagen
    database_images = []
    for llave in Llaves.objects.filter(img__isnull=False).exclude(img=''):
        database_images.append({
            'id': llave.id,
            'name': llave.cod_llave,
            'path': llave.img.path,
            'proveedor': llave.proveedor.nombre
        })
    
    # Procesar todas las imágenes del folder
    for filename in os.listdir(image_folder):
        if filename.endswith(('.jpg', '.png', '.bmp')):
            filepath = os.path.join(image_folder, filename)
            
            with open(filepath, 'rb') as f:
                results = compare_with_database(f.read(), database_images, 0.6)
            
            print(f"\n{filename}:")
            if results['results']:
                best_match = results['results'][0]
                print(f"  Mejor coincidencia: {best_match['name']}")
                print(f"  Similitud: {best_match['similarity']*100:.1f}%")

# Uso
compare_multiple_images('comparaciones/')


# =============================================================================
# EJEMPLO 6: Personalización de Algoritmo
# =============================================================================

class CustomImageComparator(ImageComparator):
    """
    Comparador personalizado con pesos ajustables.
    """
    
    def __init__(self, orb_weight=0.7, hist_weight=0.3, threshold=0.6):
        super().__init__(threshold)
        self.orb_weight = orb_weight
        self.hist_weight = hist_weight
    
    def compare_images(self, img1, img2):
        """Override para usar pesos personalizados."""
        orb_sim = self.calculate_similarity_orb(img1, img2)
        hist_sim = self.calculate_histogram_similarity(img1, img2)
        
        # Usar pesos personalizados
        combined = (orb_sim * self.orb_weight + 
                   hist_sim * self.hist_weight)
        
        return {
            'similarity': float(combined),
            'orb_similarity': float(orb_sim),
            'histogram_similarity': float(hist_sim),
            'is_match': combined >= self.threshold
        }

# Uso: Más peso a características (mejor para llaves)
custom_comparator = CustomImageComparator(orb_weight=0.8, hist_weight=0.2)


# =============================================================================
# EJEMPLO 7: Análisis de Resultados
# =============================================================================

def analyze_comparison_results(results):
    """
    Analiza los resultados y proporciona insights.
    """
    
    data = results['results']
    
    if not data:
        print("No hay resultados")
        return
    
    similarities = [r['similarity'] for r in data]
    matches = [r for r in data if r['is_match']]
    
    print(f"Total de comparaciones: {len(data)}")
    print(f"Coincidencias encontradas: {len(matches)}")
    print(f"Similitud promedio: {sum(similarities)/len(similarities)*100:.1f}%")
    print(f"Similitud máxima: {max(similarities)*100:.1f}%")
    print(f"Similitud mínima: {min(similarities)*100:.1f}%")
    
    # Distribuir en categorías
    muy_probable = len([r for r in data if r['similarity'] >= 0.8])
    probable = len([r for r in data if 0.6 <= r['similarity'] < 0.8])
    moderada = len([r for r in data if 0.4 <= r['similarity'] < 0.6])
    baja = len([r for r in data if r['similarity'] < 0.4])
    
    print(f"\nDistribución:")
    print(f"  Muy probable (80-100%): {muy_probable}")
    print(f"  Probable (60-80%): {probable}")
    print(f"  Moderada (40-60%): {moderada}")
    print(f"  Baja (<40%): {baja}")


# =============================================================================
# EJEMPLO 8: Exportar Resultados
# =============================================================================

import json
import csv
from datetime import datetime

def export_results(results, format='json'):
    """
    Exporta resultados a diferentes formatos.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format == 'json':
        filename = f"resultados_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Exportado a {filename}")
    
    elif format == 'csv':
        filename = f"resultados_{timestamp}.csv"
        with open(filename, 'w', newline='') as f:
            if results['results']:
                writer = csv.DictWriter(f, fieldnames=[
                    'id', 'name', 'similarity', 'is_match', 
                    'proveedor', 'cantidad', 'precio_compra'
                ])
                writer.writeheader()
                for row in results['results']:
                    writer.writerow(row)
        print(f"Exportado a {filename}")
    
    elif format == 'txt':
        filename = f"resultados_{timestamp}.txt"
        with open(filename, 'w') as f:
            f.write(f"Comparación de Imágenes\n")
            f.write(f"Fecha: {timestamp}\n")
            f.write(f"Total de resultados: {results['total']}\n")
            f.write(f"Coincidencias: {results['matches']}\n\n")
            
            for r in results['results']:
                f.write(f"{r['name']}\n")
                f.write(f"  Similitud: {r['similarity']*100:.1f}%\n")
                f.write(f"  Proveedor: {r['proveedor']}\n")
                f.write(f"  Stock: {r['cantidad']}\n\n")
        print(f"Exportado a {filename}")


# =============================================================================
# EJEMPLO 9: Cache y Optimización
# =============================================================================

from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def cached_image_hash(image_path):
    """
    Crea hash de imagen para caché.
    """
    with open(image_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

# Uso para evitar comparaciones duplicadas
compared_pairs = {}

def compare_with_cache(img1_path, img2_path):
    """
    Compara con caché para evitar trabajo duplicado.
    """
    hash1 = cached_image_hash(img1_path)
    hash2 = cached_image_hash(img2_path)
    
    pair_key = tuple(sorted([hash1, hash2]))
    
    if pair_key in compared_pairs:
        return compared_pairs[pair_key]
    
    # Si no está en caché, comparar
    comparator = ImageComparator()
    img1 = comparator.load_image_from_file(img1_path)
    img2 = comparator.load_image_from_file(img2_path)
    
    result = comparator.compare_images(img1, img2)
    compared_pairs[pair_key] = result
    
    return result


# =============================================================================
# EJEMPLO 10: Integración con Sistema de Alertas
# =============================================================================

def auto_identify_key(image_bytes):
    """
    Identifica automáticamente una llave y crea alertas.
    """
    from api.models import Llaves
    from django.contrib.auth.models import User
    
    # Comparar imagen
    database_images = []
    for llave in Llaves.objects.filter(img__isnull=False):
        database_images.append({
            'id': llave.id,
            'name': llave.cod_llave,
            'path': llave.img.path,
            'proveedor': llave.proveedor.nombre,
            'cantidad': llave.cantidad
        })
    
    results = compare_with_database(image_bytes, database_images, 0.7)
    
    if results['results']:
        best_match = results['results'][0]
        
        # Si está bajo stock, alertar
        if best_match['cantidad'] < 100:
            print(f"⚠️  ALERTA: {best_match['name']} tiene bajo stock ({best_match['cantidad']})")
        
        # Si no hay coincidencia clara, avisar
        if best_match['similarity'] < 0.8:
            print(f"⚠️  ADVERTENCIA: Similitud baja ({best_match['similarity']*100:.1f}%)")
        
        return best_match
    
    return None


# =============================================================================
# Fin de Ejemplos
# =============================================================================

print("""
EJEMPLOS DE USO - Comparador de Imágenes
=========================================

Los ejemplos anteriores demuestran:

1. Uso desde Python backend
2. Uso desde API REST (HTTP)
3. Uso desde cURL (Terminal)
4. Uso desde JavaScript/TypeScript (Frontend)
5. Procesamiento por lotes
6. Personalización de algoritmo
7. Análisis de resultados
8. Exportación de resultados
9. Cache y optimización
10. Integración con alertas

Para más información, ver:
- COMPARADOR_IMAGENES.md
- INSTALACION_COMPARADOR.md
- IMPLEMENTACION_COMPARADOR.md
""")
