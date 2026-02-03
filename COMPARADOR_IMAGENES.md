# Comparador de Imágenes - Documentación

## 📸 ¿Qué es?

El **Comparador de Imágenes** es una nueva funcionalidad de tu aplicación KEYMASTER que te permite:

1. **Cargar una imagen** de una llave
2. **Comparar automáticamente** esa imagen con todas las llaves en tu base de datos
3. **Obtener coincidencias** ordenadas por similitud
4. **Identificar** la llave exacta o similar que buscas

## 🚀 Cómo usar

### Acceso

1. En el panel izquierdo, bajo "INTELIGENCIA AI", encontrarás el nuevo botón **"COMPARADOR DE IMÁGENES"**
2. Haz clic en él para abrir la interfaz de comparación

### Pasos para comparar

1. **Carga una imagen**
   - Arrastra y suelta una imagen al área de carga, o
   - Haz clic en la zona de arrastrar para seleccionar un archivo

2. **Ajusta el umbral de similitud** (opcional)
   - Valores más bajos = más resultados (detecta similitudes leves)
   - Valores más altos = solo coincidencias cercanas
   - Rango: 0% a 100% (por defecto: 60%)

3. **Haz clic en "Comparar Imágenes"**
   - El sistema analizará la imagen cargada
   - Comparará con todas las imágenes de llaves en la BD

4. **Revisa los resultados**
   - Verás todas las coincidencias ordenadas por similitud
   - Cada resultado muestra:
     - Código de la llave
     - Proveedor
     - Stock disponible
     - Precio de compra
     - Porcentaje de similitud

## 📊 Cómo funciona

El comparador utiliza **dos métodos de análisis**:

### 1. Análisis de Características (60% del peso)
- Utiliza el algoritmo **ORB** (Oriented FAST and Rotated BRIEF)
- Detecta puntos característicos en la imagen
- Empareja estos puntos con la imagen de base de datos
- Mejor para identif icar la forma y estructura de la llave

### 2. Análisis de Color (40% del peso)
- Compara histogramas de color (RGB)
- Calcula similitud entre distribuciones de color
- Mejor para identificar llaves del mismo tipo/material

**Resultado Final** = Promedio ponderado de ambos métodos

## 🎯 Interpretación de Resultados

| Similitud | Significado | Acción Recomendada |
|-----------|-------------|-------------------|
| 80-100%   | Muy probable coincidencia | Confía en el resultado |
| 60-79%    | Probable coincidencia | Verifica manualmente |
| 40-59%    | Similitud moderada | Considerar otras opciones |
| < 40%     | Baja similitud | Probablemente no es la misma llave |

## 💡 Consejos para mejores resultados

✅ **Hacer:**
- Usar imágenes claras y bien iluminadas
- Capturar toda la llave en la imagen
- Usar fondos simples o uniformes
- Comparar llaves similares en tipo

❌ **Evitar:**
- Imágenes borrosas o con poco contraste
- Ángulos muy extremos
- Imágenes con sombras o reflejos
- Comparar llaves muy diferentes en diseño

## 📁 Requisitos

**La base de datos debe tener:**
- Imágenes de llaves cargadas en cada registro
- Imágenes en formatos: JPG, PNG, BMP o TIFF
- Resolución mínima: 100x100 píxeles
- Tamaño máximo por imagen: 10MB

## 🔧 Información Técnica

### Backend (Python/Django)
- **Ubicación**: `api/views.py` - Endpoint `POST /api/images/compare/`
- **Módulo**: `api/image_comparison.py`
- **Librerías**: OpenCV (cv2), NumPy, PIL/Pillow

### Frontend (Vue 3)
- **Componente**: `frontend/src/components/ImageComparison.vue`
- **API Integration**: `frontend/src/services/api.ts`
- **Notificaciones**: Toast notifications integradas

## 🐛 Solución de Problemas

### "No se pudo procesar la imagen"
- Verifica que sea un archivo de imagen válido (JPG, PNG, BMP, TIFF)
- Intenta con una imagen diferente
- Asegúrate que la imagen no esté corrupta

### "No hay imágenes de llaves disponibles"
- Asegúrate de haber cargado imágenes en tus registros de llaves
- Ve a Inventario de Llaves y agrega imágenes a las llaves

### Resultados inesperados
- Intenta ajustar el umbral de similitud
- Usa una imagen de mejor calidad
- Asegúrate de que la llave que buscas esté en la BD

## 📈 Casos de Uso

1. **Identificar una llave desconocida**
   - Toma una foto de una llave y el sistema la identifica

2. **Verificar duplicados**
   - Detecta si dos imágenes son de la misma llave

3. **Control de calidad**
   - Verifica si las llaves recibidas coinciden con las órdenes

4. **Organización de inventario**
   - Agrupa llaves similares automáticamente

## 📞 Soporte

Para reportar bugs o sugerencias, verifica:
1. Que todas las imágenes tengan buena calidad
2. Que el servidor esté ejecutándose correctamente
3. Los logs en la consola del navegador (F12 → Console)

---

**Versión**: 1.0  
**Fecha**: 29 de enero de 2026  
**Desarrollador**: Sistema KEYMASTER
