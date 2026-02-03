"""
Módulo para comparar imágenes usando visión por computadora.
Utiliza OpenCV para extraer características y calcular similitud.
"""

# Intentar importar OpenCV, pero permitir ejecutar el servidor aunque no esté instalado.
try:
    import cv2
    HAVE_CV2 = True
except Exception:
    cv2 = None
    HAVE_CV2 = False

try:
    import numpy as np
    HAVE_NUMPY = True
except Exception:
    np = None
    HAVE_NUMPY = False

from PIL import Image, ImageChops, ImageFilter
import io
import logging

logger = logging.getLogger(__name__)

if not HAVE_NUMPY:
    logger.warning("NumPy (numpy) no está instalado. Muchas operaciones de imagen usarán implementaciones de respaldo menos eficientes.")
class ImageComparator:
    """Comparador de imágenes basado en características visuales."""
    
    def __init__(self, threshold=0.6):
        """
        Inicializa el comparador.
        
        Args:
            threshold: Umbral mínimo de similitud (0-1)
        """
        self.threshold = threshold
        if HAVE_CV2:
            # Componentes basados en OpenCV
            try:
                self.orb = cv2.ORB_create(nfeatures=500)
                self.bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            except Exception as e:
                logger.warning(f"OpenCV disponible pero no se pudieron crear los detectores: {e}")
                self.orb = None
                self.bf = None
        else:
            logger.warning("OpenCV (cv2) no está instalado. Las comparaciones por características ORB y algunos métodos avanzados no estarán disponibles. Se usará una versión de respaldo basada en Pillow y numpy.")
            self.orb = None
            self.bf = None
    
    def load_image_from_file(self, image_path):
        """Carga una imagen desde una ruta.
        Devuelve un objeto numpy.ndarray (BGR) si OpenCV está disponible, o un PIL.Image en caso contrario.
        """
        try:
            if HAVE_CV2 and HAVE_NUMPY:
                img = cv2.imread(str(image_path))
                if img is None:
                    raise ValueError(f"No se pudo cargar la imagen: {image_path}")
                return img
            # Fallback: usar Pillow
            pil = Image.open(str(image_path)).convert('RGB')
            return pil
        except Exception as e:
            logger.error(f"Error al cargar imagen: {e}")
            return None
    
    def load_image_from_bytes(self, image_bytes):
        """Carga una imagen desde bytes.
        Devuelve numpy.ndarray (BGR) si OpenCV está disponible, o PIL.Image en caso contrario.
        """
        try:
            if HAVE_NUMPY and HAVE_CV2:
                nparr = np.frombuffer(image_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if img is None:
                    raise ValueError("No se pudo decodificar la imagen")
                return img
            # Fallback: usar Pillow
            pil = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            return pil
        except Exception as e:
            logger.error(f"Error al cargar imagen desde bytes: {e}")
            return None
    
    def preprocess_image(self, img):
        """Preprocesa la imagen para comparación.
        Retorna una imagen en escala de grises. Puede devolver numpy.ndarray o PIL.Image según disponibilidad.
        """
        try:
            if HAVE_CV2 and HAVE_NUMPY and isinstance(img, np.ndarray):
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                gray = cv2.resize(gray, (300, 300))
                return gray
            # Fallback: manejar PIL.Image u objetos bytes
            if isinstance(img, Image.Image):
                pil = img.convert('L').resize((300, 300))
            else:
                pil = Image.open(io.BytesIO(img)).convert('L').resize((300, 300))
            if HAVE_NUMPY:
                return np.array(pil)
            return pil
        except Exception as e:
            logger.error(f"Error en preprocess_image: {e}")
            return None
    
    def extract_features(self, img):
        """Extrae características (keypoints y descriptores) de la imagen."""
        try:
            gray = self.preprocess_image(img)
            # Sólo extraer con ORB si está disponible y la imagen está en formato numpy
            if self.orb is not None and HAVE_NUMPY and isinstance(gray, np.ndarray):
                kp, des = self.orb.detectAndCompute(gray, None)
                return kp, des, gray
            # No hay soporte ORB: devolver None para kp/des y la imagen preprocesada
            return None, None, gray
        except Exception as e:
            logger.error(f"Error al extraer características: {e}")
            return None, None, None
    
    def calculate_similarity_orb(self, img1, img2):
        """
        Calcula similitud entre dos imágenes usando ORB.
        Retorna un valor entre 0 y 1.
        """
        try:
            kp1, des1, _ = self.extract_features(img1)
            kp2, des2, _ = self.extract_features(img2)
            
            if des1 is None or des2 is None or len(kp1) == 0 or len(kp2) == 0:
                return 0.0
            
            # Emparejar características
            matches = self.bf.match(des1, des2)
            
            if len(matches) == 0:
                return 0.0
            
            # Ordenar por distancia
            matches = sorted(matches, key=lambda x: x.distance)
            
            # Calcular similitud basada en matches
            # Usar los mejores matches y sus distancias
            good_matches = [m for m in matches[:50] if m.distance < 100]
            
            if len(good_matches) == 0:
                return 0.0
            
            # Similitud inversamente proporcional a la distancia promedio
            avg_distance = sum([m.distance for m in good_matches]) / len(good_matches)
            similarity = max(0, 1 - (avg_distance / 100))
            
            return float(similarity)
        
        except Exception as e:
            logger.error(f"Error al calcular similitud ORB: {e}")
            return 0.0
    
    def calculate_histogram_similarity(self, img1, img2):
        """
        Calcula similitud usando histogramas de color.
        Usa OpenCV si está disponible; si no, usa Pillow + numpy.
        """
        try:
            # Si OpenCV está disponible y las imágenes están en formato numpy (BGR), usarlo
            if HAVE_CV2 and isinstance(img1, (np.ndarray,)) and isinstance(img2, (np.ndarray,)):
                img1_resized = cv2.resize(img1, (300, 300))
                img2_resized = cv2.resize(img2, (300, 300))
                similarity = 0
                for i in range(3):  # BGR
                    hist1 = cv2.calcHist([img1_resized], [i], None, [256], [0, 256])
                    hist2 = cv2.calcHist([img2_resized], [i], None, [256], [0, 256])
                    hist1 = cv2.normalize(hist1, hist1).flatten()
                    hist2 = cv2.normalize(hist2, hist2).flatten()
                    similarity += cv2.compareHist(hist1, hist2, cv2.HISTCMP_BHATTACHARYYA)
                avg_similarity = similarity / 3
                return float(max(0, 1 - avg_similarity))
            else:
                # Fallback: usar Pillow y numpy para histogramas RGB
                def to_rgb_array(img):
                    if isinstance(img, np.ndarray):
                        # Assume BGR -> convert to RGB
                        arr = img.copy()
                        if arr.ndim == 3 and arr.shape[2] == 3:
                            arr = arr[:, :, ::-1]
                        return arr
                    elif isinstance(img, Image.Image):
                        return np.array(img.convert('RGB'))
                    else:
                        # bytes
                        return np.array(Image.open(io.BytesIO(img)).convert('RGB'))

                    a1 = to_rgb_array(img1)
                a2 = to_rgb_array(img2)

                # Resize to 300x300 using PIL for consistency
                if HAVE_NUMPY and isinstance(a1, np.ndarray):
                    p1 = Image.fromarray(a1).resize((300, 300))
                    p2 = Image.fromarray(a2).resize((300, 300))
                    a1 = np.array(p1)
                    a2 = np.array(p2)

                    sim_channels = []
                    for c in range(3):
                        h1, _ = np.histogram(a1[:, :, c].ravel(), bins=256, range=(0, 255), density=True)
                        h2, _ = np.histogram(a2[:, :, c].ravel(), bins=256, range=(0, 255), density=True)
                        score = np.sum(np.minimum(h1, h2))
                        sim_channels.append(score)
                    return float(np.mean(sim_channels))
                else:
                    # Sin numpy: usar histogramas de Pillow
                    p1 = Image.fromarray(a1) if isinstance(a1, np.ndarray) and HAVE_NUMPY else Image.fromarray(a1) if isinstance(a1, np.ndarray) else Image.fromarray(np.array(Image.fromarray(a1))) if HAVE_NUMPY else Image.fromarray(a1) if isinstance(a1, Image.Image) else Image.fromarray(np.array(Image.open(io.BytesIO(a1))))
                    p1 = p1.resize((300,300))
                    p2 = Image.fromarray(a2) if isinstance(a2, np.ndarray) else (a2 if isinstance(a2, Image.Image) else Image.open(io.BytesIO(a2)))
                    p2 = p2.resize((300,300))
                    h1 = p1.histogram()
                    h2 = p2.histogram()
                    # h1/h2 length 768 (256 per channel). Compute per-channel similarity
                    sims = []
                    for c in range(3):
                        s1 = h1[c*256:(c+1)*256]
                        s2 = h2[c*256:(c+1)*256]
                        # convert to floats and normalize
                        tot1 = sum(s1) or 1
                        tot2 = sum(s2) or 1
                        s = sum(min(a,b) for a,b in zip(s1,s2)) / min(tot1, tot2)
                        sims.append(s)
                    return float(sum(sims)/len(sims))
        except Exception as e:
            logger.error(f"Error al calcular similitud de histogramas: {e}")
            return 0.0
    
    def calculate_edge_similarity(self, img1, img2):
        """
        Calcula similitud basada en bordes detectados.
        Usa Canny si CV2 está disponible; si no, usa un detector simple con numpy.
        """
        try:
            def to_gray_array(img):
                if HAVE_CV2 and isinstance(img, np.ndarray):
                    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                elif isinstance(img, np.ndarray):
                    # Assume RGB
                    return np.dot(img[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)
                elif isinstance(img, Image.Image):
                    return np.array(img.convert('L'))
                else:
                    return np.array(Image.open(io.BytesIO(img)).convert('L'))

            g1 = to_gray_array(img1)
            g2 = to_gray_array(img2)

            # Resize to fixed size
            p1 = Image.fromarray(g1).resize((300, 300))
            p2 = Image.fromarray(g2).resize((300, 300))
            g1 = np.array(p1)
            g2 = np.array(p2)

            if HAVE_CV2 and HAVE_NUMPY:
                edges1 = cv2.Canny(g1, 50, 150)
                edges2 = cv2.Canny(g2, 50, 150)
            else:
                # If numpy is available, use sobel or simple diff; otherwise use PIL filters
                if HAVE_NUMPY:
                    sx = np.array([[1,0,-1],[2,0,-2],[1,0,-1]])
                    sy = sx.T
                    def sobel(img):
                        try:
                            from scipy.signal import convolve2d
                            gx = convolve2d(img, sx, mode='same', boundary='symm')
                            gy = convolve2d(img, sy, mode='same', boundary='symm')
                            mag = np.hypot(gx, gy)
                            mag = (mag / np.max(mag) * 255).astype(np.uint8)
                            return mag
                        except Exception:
                            # scipy not available: approximate with diffs
                            return (np.abs(np.diff(img.astype(int), axis=0)).clip(0,255)).astype(np.uint8)
                    edges1 = sobel(g1)
                    edges2 = sobel(g2)
                    # ensure same shape
                    if edges1.shape != edges2.shape:
                        min0 = min(edges1.shape[0], edges2.shape[0])
                        min1 = min(edges1.shape[1], edges2.shape[1])
                        edges1 = edges1[:min0,:min1]
                        edges2 = edges2[:min0,:min1]
                else:
                    # Pure Pillow fallback: use FIND_EDGES and ImageChops.difference
                    p1 = Image.fromarray(g1) if isinstance(g1, np.ndarray) and HAVE_NUMPY else (g1 if isinstance(g1, Image.Image) else Image.fromarray(np.array(Image.open(io.BytesIO(g1)))))
                    p2 = Image.fromarray(g2) if isinstance(g2, np.ndarray) and HAVE_NUMPY else (g2 if isinstance(g2, Image.Image) else Image.fromarray(np.array(Image.open(io.BytesIO(g2)))))
                    e1 = p1.filter(ImageFilter.FIND_EDGES).convert('L')
                    e2 = p2.filter(ImageFilter.FIND_EDGES).convert('L')
                    diff_img = ImageChops.difference(e1, e2)
                    # convert to array-like via histogram
                    hist = diff_img.histogram()
                    sum_diff = sum(hist)
                    max_possible = 255 * diff_img.size[0] * diff_img.size[1]
                    # Create pseudo-edges arrays by using difference intensity map
                    edges1 = np.array(e1) if HAVE_NUMPY else e1
                    edges2 = np.array(e2) if HAVE_NUMPY else e2
                    # If numpy available, reduce to numeric arrays for later steps; else keep PIL images
                    if HAVE_NUMPY:
                        pass
                    else:
                        # Use hist-based similarity later
                        pass
            # Ensure same shape
            if edges1.shape != edges2.shape:
                min0 = min(edges1.shape[0], edges2.shape[0])
                min1 = min(edges1.shape[1], edges2.shape[1])
                edges1 = edges1[:min0,:min1]
                edges2 = edges2[:min0,:min1]

            diff = np.abs(edges1.astype(int) - edges2.astype(int))
            similarity = 1.0 - (np.sum(diff) / (diff.size * 255))
            return float(max(0, similarity))
        except Exception as e:
            logger.error(f"Error al calcular similitud de bordes: {e}")
            return 0.0
    
    def compare_images(self, img1, img2):
        """
        Compara dos imágenes y retorna una similitud combinada.
        Se enfoca principalmente en formas y líneas (ORB + Edges) en lugar de color.
        """
        try:
            # Combinar tres métodos para obtener mejor resultado
            orb_sim = self.calculate_similarity_orb(img1, img2)
            edge_sim = self.calculate_edge_similarity(img1, img2)
            hist_sim = self.calculate_histogram_similarity(img1, img2)
            
            # 60% ORB (características) + 30% Bordes (líneas y formas) + 10% color
            combined_similarity = (orb_sim * 0.6 + edge_sim * 0.3 + hist_sim * 0.1)
            
            return {
                'similarity': float(combined_similarity),
                'orb_similarity': float(orb_sim),
                'edge_similarity': float(edge_sim),
                'histogram_similarity': float(hist_sim),
                'is_match': combined_similarity >= self.threshold
            }
        except Exception as e:
            logger.error(f"Error al comparar imágenes: {e}")
            return {
                'similarity': 0.0,
                'orb_similarity': 0.0,
                'edge_similarity': 0.0,
                'histogram_similarity': 0.0,
                'is_match': False,
                'error': str(e)
            }

def compare_with_database(uploaded_image_bytes, database_images, threshold=0.6):
    """
    Compara una imagen cargada con múltiples imágenes de la base de datos.
    
    Args:
        uploaded_image_bytes: Bytes de la imagen cargada
        database_images: Lista de diccionarios con información de imágenes
        threshold: Umbral mínimo de similitud
    
    Returns:
        Diccionario con lista de resultados ordenada por similitud
    """
    try:
        comparator = ImageComparator(threshold=threshold)
        
        # Cargar imagen cargada
        uploaded_img = comparator.load_image_from_bytes(uploaded_image_bytes)
        if uploaded_img is None:
            return {'error': 'No se pudo procesar la imagen cargada', 'results': []}
        
        results = []
        
        for item in database_images:
            try:
                item_id = item['id']
                item_name = item['name']
                item_path = item['path']
                item_image_url = item.get('image_url')
                
                # Cargar imagen de base de datos
                if isinstance(item_path, str):
                    db_img = comparator.load_image_from_file(item_path)
                else:
                    db_img = comparator.load_image_from_bytes(item_path)
                
                if db_img is None:
                    continue
                
                # Comparar
                comparison = comparator.compare_images(uploaded_img, db_img)
                
                result = {
                    'id': item_id,
                    'name': item_name,
                    'path': str(item_path),
                    'image_url': item_image_url,
                    'proveedor': item.get('proveedor'),
                    'cantidad': item.get('cantidad'),
                    'precio_compra': item.get('precio_compra'),
                    **comparison
                }
                results.append(result)
            
            except Exception as e:
                logger.error(f"Error comparando con item {item.get('id')}: {e}")
                continue
        
        # Ordenar por similitud descendente
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        return {
            'results': results,
            'total': len(results),
            'matches': len([r for r in results if r['is_match']])
        }
    
    except Exception as e:
        logger.error(f"Error en compare_with_database: {e}")
        return {'error': str(e), 'results': []}
