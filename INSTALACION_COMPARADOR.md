# Guía de Instalación - Comparador de Imágenes

## ✅ Paso 1: Verificar Instalación de Dependencias

El sistema requiere las siguientes librerías Python:

```bash
# Las siguientes ya deben estar instaladas:
pip list | grep -E "opencv|numpy|pillow|django|djangorestframework"
```

### Dependencias instaladas:
- ✅ `opencv-python>=4.5.0` - Procesamiento de imágenes
- ✅ `numpy>=1.20.0` - Operaciones numéricas
- ✅ `pillow>=8.0.0` - Manipulación de imágenes
- ✅ `Django>=3.2` - Framework web (ya existente)
- ✅ `djangorestframework>=3.12` - API REST (ya existente)

Si alguna falta, instálala con:
```bash
pip install opencv-python numpy pillow
```

## ✅ Paso 2: Verificar Archivos Nuevos

Los siguientes archivos han sido creados/modificados:

### Backend
- ✅ `api/image_comparison.py` - Módulo de lógica de comparación
- ✅ `api/views.py` - Nuevo endpoint `ImageComparisonView`
- ✅ `api/urls.py` - Nueva ruta `/api/images/compare/`

### Frontend
- ✅ `frontend/src/components/ImageComparison.vue` - Componente Vue
- ✅ `frontend/src/App.vue` - Integración en menú y router

## ✅ Paso 3: Migraciones (Si aplica)

Este proyecto **NO requiere migraciones** ya que no se agregaron nuevos modelos.

## ✅ Paso 4: Verificar Configuración de Django

Asegúrate que en `backend/settings.py` tengas:

```python
# MEDIA FILES
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# FILE UPLOAD
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
```

## ✅ Paso 5: Probar el Sistema

### Opción A: Prueba Manual desde navegador

1. Inicia el servidor Django:
```bash
python manage.py runserver
```

2. Inicia el servidor frontend (otra terminal):
```bash
cd frontend
npm run dev
```

3. Accede a http://localhost:5173 (o el puerto que uses)

4. Ve a "COMPARADOR DE IMÁGENES" en el menú lateral

5. Carga una imagen y prueba la comparación

### Opción B: Prueba Automatizada

```bash
python test_image_comparison.py
```

Esto creará:
- Usuario de prueba
- Llaves de prueba con imágenes
- Realizará una comparación de prueba

## 🔧 Configuración Avanzada

### Ajustar Umbral Predeterminado

En `frontend/src/components/ImageComparison.vue`, línea ~30:
```typescript
const threshold = ref(0.6); // Cambiar este valor (0-1)
```

### Ajustar Pesos de Comparación

En `api/image_comparison.py`, línea ~212:
```python
# Cambiar estos pesos (deben sumar 1.0)
combined_similarity = (orb_sim * 0.6 + hist_sim * 0.4)
```

- Más peso a características (ORB): Mejor para forma
- Más peso a color (Histograma): Mejor para tipo/material

### Límite de Tamaño de Archivo

En `frontend/src/components/ImageComparison.vue`, línea ~68:
```typescript
if (file.size > 10 * 1024 * 1024) { // 10MB
    showToast('La imagen es demasiado grande (máx 10MB)', 'error');
}
```

## 📋 Checklist de Verificación

- [ ] OpenCV está instalado (`pip show opencv-python`)
- [ ] El servidor Django inicia sin errores
- [ ] El servidor frontend compila sin errores
- [ ] Las imágenes de llaves están cargadas en la BD
- [ ] El endpoint `/api/images/compare/` responde correctamente
- [ ] El componente aparece en el menú lateral
- [ ] La comparación funciona con una imagen de prueba

## 🐛 Troubleshooting

### Error: "No module named 'cv2'"
```bash
pip install --upgrade opencv-python
```

### Error: "CORS error"
Verifica que `CORS_ALLOWED_ORIGINS` en `backend/settings.py` incluya el frontend.

### Error: "413 Payload Too Large"
Aumenta el límite en `backend/settings.py`:
```python
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800
```

### Error: "No se encuentra la imagen"
Verifica que:
1. Las llaves tengan imágenes cargadas
2. El servidor tenga acceso a la carpeta `media/`
3. Los permisos de archivo sean correctos

## 📱 Uso desde Dispositivos Móviles

La interfaz es responsive y funciona en:
- ✅ Desktop (navegadores modernos)
- ✅ Tablet (iPad, Android tablets)
- ✅ Móvil (iPhone, Android phones)

Se puede:
- Tomar foto directamente: `<input type="file" accept="image/*" capture>`
- O seleccionar de galería
- O arrastrar y soltar (desktop)

## 🔐 Consideraciones de Seguridad

- ✅ La validación ocurre en frontend y backend
- ✅ Solo usuarios autenticados pueden usar la comparación
- ✅ Las imágenes no se almacenan temporalmente en servidor
- ✅ Se valida tipo de archivo en backend
- ✅ Límite de tamaño de 10MB

## 📊 Rendimiento

### Tiempos típicos de comparación:

| Número de Llaves | Tiempo Estimado |
|------------------|-----------------|
| 10               | 0.5-1 segundo   |
| 50               | 2-3 segundos    |
| 100              | 4-6 segundos    |
| 500+             | 15-30 segundos  |

Para optimizar:
- Cargar solo imágenes necesarias
- Usar imágenes de menor resolución
- Ajustar el umbral de similitud más alto

## 📖 Recursos Adicionales

- OpenCV Documentation: https://docs.opencv.org/
- ORB Algorithm: https://ieeexplore.ieee.org/document/6126544
- Histogram Comparison: https://en.wikipedia.org/wiki/Histogram_matching

---

**Versión**: 1.0  
**Última actualización**: 29 de enero de 2026
