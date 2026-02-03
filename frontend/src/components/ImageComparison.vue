<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import api from '../services/api';
import { useToast } from '../composables/useToast';

const { show: showToast } = useToast();

// Estado
const uploadedImage = ref<File | null>(null);
const uploadedImagePreview = ref<string | null>(null);
const isComparing = ref(false);
const comparisonResults = ref<any>(null);
const threshold = ref(0.6);
const dragActive = ref(false);
const selectedResult = ref<any>(null);
const isMobile = ref(window.innerWidth < 768);
const cameraInput = ref<HTMLInputElement | null>(null);
const fileInput = ref<HTMLInputElement | null>(null);

// Filtrado y threshold local para "coincidencias altas"
const HIGH_MATCH_THRESHOLD = 0.8;
const showHighMatchesOnly = ref(true);

// Tipos disponibles (coincide con backend)
const tipoOptions = [
    { value: 'all', label: 'Todos' },
    { value: 'house', label: 'Casa' },
    { value: 'car', label: 'Auto' },
    { value: 'menga', label: 'Menga Canal' }
];
const selectedTipo = ref('all');

const filteredResults = computed(() => {
    if (!comparisonResults.value?.results) return [];
    return comparisonResults.value.results.filter((r: any) => {
        if (showHighMatchesOnly.value) return (r.similarity ?? 0) >= HIGH_MATCH_THRESHOLD;
        return true;
    });
});

// Computed
const matchCount = computed(() => {
    if (!comparisonResults.value?.results) return 0;
    return comparisonResults.value.results.filter((r: any) => r.is_match).length;
});

const hasResults = computed(() => comparisonResults.value?.results && comparisonResults.value.results.length > 0);

// Métodos
const handleFileSelect = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    
    const file = files[0] as File;
    
    // Validar tipo
    if (!['image/jpeg', 'image/png', 'image/bmp', 'image/tiff'].includes(file.type)) {
        showToast('Formato no válido. Use JPG, PNG, BMP o TIFF', 'error');
        return;
    }
    
    // Validar tamaño (máx 10MB)
    if (file.size > 10 * 1024 * 1024) {
        showToast('La imagen es demasiado grande (máx 10MB)', 'error');
        return;
    }
    
    uploadedImage.value = file;
    
    // Crear preview
    const reader = new FileReader();
    reader.onload = (e) => {
        uploadedImagePreview.value = e.target?.result as string;
    };
    reader.readAsDataURL(file);
};

const handleDragEnter = (e: DragEvent) => {
    e.preventDefault();
    dragActive.value = true;
};

const handleDragLeave = (e: DragEvent) => {
    e.preventDefault();
    dragActive.value = false;
};

const handleDrop = (e: DragEvent) => {
    e.preventDefault();
    dragActive.value = false;
    
    if (e.dataTransfer?.files) {
        handleFileSelect(e.dataTransfer.files);
    }
};

const clearImage = () => {
    uploadedImage.value = null;
    uploadedImagePreview.value = null;
    comparisonResults.value = null;
    selectedResult.value = null;
};

const compareImages = async () => {
    if (!uploadedImage.value) {
        showToast('Por favor selecciona una imagen', 'info');
        return;
    }
    
    if (threshold.value < 0 || threshold.value > 1) {
        showToast('El umbral debe estar entre 0 y 1', 'error');
        return;
    }
    
    isComparing.value = true;
    
    try {
        const formData = new FormData();
        formData.append('uploaded_image', uploadedImage.value);
        formData.append('threshold', threshold.value.toString());
        
        // Enviar tipo si se seleccionó uno específico
        if (selectedTipo.value && selectedTipo.value !== 'all') {
            formData.append('tipo', selectedTipo.value);
        }

        const { data } = await api.post('/images/compare/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        
        // Normalizar URLs de imagen: si `image_url` es relativa, prefijar con host del backend
        if (data && Array.isArray(data.results)) {
            const apiRoot = (api.defaults.baseURL || '').replace(/\/api\/?$/, '');
            data.results = data.results.map((r: any) => {
                if (r.image_url && !/^https?:\/\//i.test(r.image_url)) {
                    r.image_url = `${apiRoot}${r.image_url}`;
                }
                return r;
            });
        }

        comparisonResults.value = data;
        selectedResult.value = null;

        if (data.error) {
            showToast(data.error, 'info');
        } else if (data.matches > 0) {
            // Añadir contexto si se aplicó un filtro de tipo
            const tipoLabel = data.filtered_tipo ? (tipoOptions.find(o => o.value === data.filtered_tipo)?.label || data.filtered_tipo) : null;
            showToast(`¡Se encontraron ${data.matches} coincidencias!${tipoLabel ? ' (Tipo: ' + tipoLabel + ')' : ''}`, 'success');
        } else {
            showToast('No se encontraron coincidencias', 'info');
        }
    } catch (error: any) {
        console.error('Error:', error);
        showToast('Error al comparar imágenes: ' + (error.response?.data?.error || error.message), 'error');
    } finally {
        isComparing.value = false;
    }
};

const selectResult = (result: any) => {
    selectedResult.value = selectedResult.value?.id === result.id ? null : result;
};

const handleImageError = (event: Event) => {
    const img = event.target as HTMLImageElement;
    console.warn('Error cargando imagen:', img.src);
};

const getMatchColor = (similarity: number): string => {
    if (similarity >= 0.8) return 'from-green-500 to-emerald-600';
    if (similarity >= 0.6) return 'from-yellow-500 to-amber-600';
    if (similarity >= 0.4) return 'from-orange-500 to-red-600';
    return 'from-red-500 to-rose-600';
};

const displayedCount = computed(() => filteredResults.value.length);

// Abrir selector de archivos / cámara
const openFile = () => {
  try {
    (fileInput.value as HTMLInputElement | null)?.click();
  } catch (e) {
    console.error('openFile error', e);
  }
};

const openCamera = () => {
  try {
    (cameraInput.value as HTMLInputElement | null)?.click();
  } catch (e) {
    console.error('openCamera error', e);
  }
};

// Detectar cambios de tamaño de pantalla
onMounted(() => {
    window.addEventListener('resize', () => {
        isMobile.value = window.innerWidth < 768;
    });
});
</script>

<template>
  <div class="space-y-6">
    <!-- Información -->
    <div class="bg-gradient-to-r from-cyan-500/10 to-blue-500/10 border border-cyan-500/20 rounded-3xl p-6">
      <div class="flex items-start gap-3">
        <div class="w-12 h-12 rounded-xl bg-cyan-500/20 flex items-center justify-center flex-shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        <div class="flex-1">
          <h3 class="text-cyan-300 font-bold text-lg">Comparador de Imágenes</h3>
          <p class="text-slate-400 text-sm mt-1">Carga una imagen de una llave para encontrar coincidencias exactas en tu base de datos. El sistema analizará características visuales y color, mostrando las llaves similares con sus imágenes.</p>
          <div class="mt-3 flex items-center gap-3">
            <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Filtrar por tipo</label>
            <select v-model="selectedTipo" class="h-9 bg-slate-900/50 border border-white/5 rounded-lg px-3 text-white text-sm">
              <option v-for="opt in tipoOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
            <p v-if="selectedTipo !== 'all'" class="text-[11px] text-slate-400 ml-3">Mostrando solo <span class="font-bold text-white">{{ tipoOptions.find(o => o.value === selectedTipo)?.label }}</span></p>
          </div>        </div>
      </div>
    </div>

    <!-- Zona de carga -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
      <!-- Área de arrastrar y preview -->
      <div class="space-y-3 md:space-y-4">
        <div 
          @dragenter="handleDragEnter"
          @dragleave="handleDragLeave"
          @drop="handleDrop"
          :class="[
            'relative border-2 border-dashed rounded-3xl p-4 md:p-8 transition-all',
            dragActive 
              ? 'border-cyan-400 bg-cyan-500/10' 
              : uploadedImagePreview 
                ? 'border-green-500/50 bg-green-500/5' 
                : 'border-slate-600 bg-slate-800/50'
          ]"
        >
          <input
            ref="fileInput"
            id="fileInput"
            type="file"
            accept="image/*"
            class="hidden"
            @change="(e) => handleFileSelect((e.target as HTMLInputElement).files)"
          />

          <div v-if="uploadedImagePreview" class="text-center">
            <img :src="uploadedImagePreview" alt="Preview" class="w-full h-36 md:h-48 object-contain rounded-2xl mb-3 md:mb-4">
            <p class="text-green-400 font-semibold text-xs md:text-sm">✓ Imagen cargada correctamente</p>
          </div>

          <div v-else class="text-center py-3 md:py-4">
            <div class="w-12 md:w-16 h-12 md:h-16 bg-gradient-to-br from-slate-700 to-slate-800 rounded-2xl flex items-center justify-center mx-auto mb-3 md:mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 md:h-8 w-6 md:w-8 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <p class="text-slate-400 font-semibold mb-2 text-xs md:text-base">Arrastra una imagen aquí</p>
            <p class="text-slate-500 text-xs">JPG, PNG, BMP o TIFF (máx 10MB)</p>
          </div>
        </div>

        <!-- Botones de acción -->
        <div class="flex flex-col sm:flex-row gap-2 md:gap-3">
          <input
            ref="cameraInput"
            id="cameraInput"
            type="file"
            accept="image/*"
            capture="environment"
            class="hidden"
            @change="(e) => handleFileSelect((e.target as HTMLInputElement).files)"
          />

          <button
            v-if="isMobile"
            @click="openCamera"
            class="flex-1 px-3 md:px-4 py-2 md:py-3 rounded-2xl font-semibold text-xs md:text-sm flex items-center justify-center gap-2 transition-all bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:shadow-lg hover:shadow-purple-500/50 active:scale-95"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 md:h-5 w-4 md:w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span class="hidden sm:inline">Cámara</span>
          </button>

          <button
            @click="openFile"
            class="flex-1 px-3 md:px-4 py-2 md:py-3 rounded-2xl font-semibold text-xs md:text-sm flex items-center justify-center gap-2 transition-all bg-gradient-to-r from-cyan-600 to-blue-600 text-white hover:shadow-lg hover:shadow-cyan-500/50 active:scale-95"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 md:h-5 w-4 md:w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span class="hidden sm:inline">Buscar en mi PC</span>
            <span class="sm:hidden">Galería</span>
          </button>

          <button
            v-if="uploadedImage"
            @click="clearImage"
            class="px-3 md:px-4 py-2 md:py-3 rounded-2xl font-semibold text-xs md:text-sm flex items-center justify-center gap-2 transition-all bg-red-500/20 text-red-300 hover:bg-red-500/30 active:scale-95"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 md:h-5 w-4 md:w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <span class="hidden sm:inline">Limpiar</span>
          </button>
        </div>
      </div>

      <!-- Opciones de comparación -->
      <div class="space-y-4">
        <div class="bg-slate-800/50 border border-slate-700 rounded-2xl p-3 md:p-4">
          <label class="block text-xs md:text-sm font-semibold text-slate-300 mb-3">
            Umbral de similitud
          </label>
          <div class="flex items-center gap-2 md:gap-3">
            <input
              v-model.number="threshold"
              type="range"
              min="0"
              max="1"
              step="0.05"
              class="flex-1 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
            />
            <span class="bg-cyan-500/20 text-cyan-300 px-2 md:px-3 py-1 rounded-lg font-bold text-xs md:text-sm w-14 md:w-16 text-center">
              {{ ((threshold ?? 0) * 100).toFixed(0) }}%
            </span>
          </div>
          <p class="text-xs text-slate-500 mt-2">Valores más bajos = más resultados, valores más altos = solo coincidencias cercanas</p>
        </div>

        <button
          @click="compareImages"
          :disabled="!uploadedImage || isComparing"
          :class="[
            'w-full h-10 md:h-12 rounded-2xl font-bold flex items-center justify-center gap-2 transition-all active:scale-95 text-xs md:text-sm',
            !uploadedImage || isComparing
              ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white hover:shadow-lg hover:shadow-cyan-500/50'
          ]"
        >
          <svg v-if="!isComparing" xmlns="http://www.w3.org/2000/svg" class="h-4 md:h-5 w-4 md:w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
          </svg>
          <svg v-else class="animate-spin h-4 md:h-5 w-4 md:w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ isComparing ? 'Comparando...' : 'Comparar Imágenes' }}
        </button>

        <div v-if="comparisonResults?.error" class="bg-red-500/10 border border-red-500/50 rounded-2xl p-3 md:p-4">
          <p class="text-red-300 text-xs md:text-sm">{{ comparisonResults.error }}</p>
        </div>
      </div>
    </div>

    <!-- Resultados -->
    <div v-if="hasResults" class="space-y-3 md:space-y-4">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 sm:gap-4">
        <div class="flex items-center gap-3">
          <h3 class="text-lg md:text-xl font-bold text-white">
            Resultados de coincidencia (Mostrados: {{ displayedCount }} / Totales: {{ comparisonResults.total }})
          </h3>
          <label class="inline-flex items-center text-xs text-slate-400 ml-2">
            <input type="checkbox" class="form-checkbox mr-2" v-model="showHighMatchesOnly" />
            <span>Mostrar solo coincidencias altas (>= 80%)</span>
          </label>
        </div>
        <span v-if="matchCount > 0" class="px-3 py-1 bg-gradient-to-r from-green-500/20 to-emerald-600/20 text-green-300 rounded-lg text-xs md:text-sm font-bold w-fit">
          {{ matchCount }} coincidencia{{ matchCount !== 1 ? 's' : '' }}
        </span>
      </div>

      <!-- Vista en galería para resultados (móvil) -->
      <div class="md:hidden">
        <!-- Carrusel de miniaturas en móvil -->
        <div class="flex overflow-x-auto gap-2 pb-2 snap-x snap-mandatory">
          <div
            v-for="result in filteredResults"
            :key="result.id"
            @click="selectResult(result)"
            :class="[
              'flex-shrink-0 w-24 h-24 rounded-xl border-2 transition-all snap-start cursor-pointer',
              selectedResult?.id === result.id
                ? 'border-cyan-400 ring-2 ring-cyan-500/50'
                : result.is_match
                ? 'border-green-500/50 hover:border-green-400'
                : 'border-slate-600 hover:border-slate-500'
            ]"
          >
            <img 
              v-if="result.image_url" 
              :src="result.image_url" 
              :alt="result.name" 
              class="w-full h-full object-cover rounded-[9px]"
              @error="handleImageError"
            >
            <div v-else class="w-full h-full flex items-center justify-center bg-slate-700 rounded-[9px]">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Vista en grilla para desktop -->
      <div class="hidden md:grid md:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-3">
        <div
          v-for="result in filteredResults"
          :key="result.id"
          @click="selectResult(result)"
          :class="[
            'border rounded-lg overflow-hidden transition-all cursor-pointer hover:shadow-lg',
            selectedResult?.id === result.id
              ? 'border-cyan-400 ring-2 ring-cyan-500/50 bg-slate-800'
              : result.is_match
              ? 'border-green-500/30 bg-slate-800/50 hover:border-green-400'
              : 'border-slate-700 bg-slate-800/30'
          ]"
        >
          <!-- Imagen de la llave -->
          <div class="w-full bg-slate-900 overflow-hidden" style="aspect-ratio: 1">
            <img 
              v-if="result.image_url" 
              :src="result.image_url" 
              :alt="result.name" 
              class="w-full h-full object-cover hover:scale-105 transition-transform"
              @error="handleImageError"
            >
            <div v-else class="w-full h-full flex items-center justify-center bg-slate-700">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
          <!-- Información -->
          <div class="p-2">
            <h4 class="font-bold text-white text-xs truncate mb-0.5">{{ result.name }}</h4>
            <p class="text-[10px] text-slate-400 mb-1 truncate">{{ result.proveedor }}</p>
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-bold text-cyan-300">{{ (result.similarity * 100).toFixed(1) }}%</span>
              <div v-if="result.is_match" class="flex items-center gap-0.5">
                <div :class="`w-1.5 h-1.5 rounded-full bg-gradient-to-br ${getMatchColor(result.similarity)}`"></div>
                <span class="text-[9px] font-semibold text-green-300">✓</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Detalles del resultado seleccionado -->
      <div v-if="selectedResult" class="space-y-3 md:space-y-4">
        <div class="border border-slate-700 rounded-2xl p-3 md:p-4 bg-slate-800 space-y-4">
          <h4 class="text-sm md:text-base font-bold text-white">Detalles de coincidencia</h4>
          
          <!-- Galería de imágenes comparativas -->
          <div class="space-y-3">
            <p class="text-xs md:text-sm font-semibold text-slate-300">Comparación Visual</p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-4">
              <!-- Imagen de búsqueda -->
              <div class="flex flex-col items-center">
                <div class="w-full bg-slate-700/30 rounded-xl p-3 md:p-4 border border-slate-600/50">
                  <img 
                    v-if="uploadedImagePreview" 
                    :src="uploadedImagePreview" 
                    alt="Imagen de búsqueda" 
                    class="w-full h-32 md:h-48 object-contain rounded-lg"
                  >
                  <div v-else class="w-full h-32 md:h-48 flex items-center justify-center bg-slate-800/50 rounded-lg">
                    <p class="text-slate-500 text-xs">Sin imagen</p>
                  </div>
                </div>
                <p class="text-xs font-semibold text-slate-400 mt-2">Tu llave</p>
              </div>

              <!-- Imagen de resultado -->
              <div class="flex flex-col items-center">
                <div class="w-full bg-slate-700/30 rounded-xl p-3 md:p-4 border border-slate-600/50">
                  <img 
                    v-if="selectedResult.image_url" 
                    :src="selectedResult.image_url" 
                    alt="Llave similar" 
                    class="w-full h-32 md:h-48 object-contain rounded-lg"
                    @error="handleImageError"
                  >
                  <div v-else class="w-full h-32 md:h-48 flex items-center justify-center bg-slate-800/50 rounded-lg">
                    <p class="text-slate-500 text-xs">Sin imagen</p>
                  </div>
                </div>
                <p class="text-xs font-semibold text-slate-400 mt-2">Llave similar</p>
              </div>
            </div>

            <!-- Indicador visual de similitud -->
            <div class="flex items-center justify-center gap-2">
              <div class="flex-1 h-0.5 bg-gradient-to-r from-cyan-500/50 to-transparent"></div>
              <span :class="[
                'px-3 py-1 rounded-full text-xs font-bold',
                selectedResult.similarity >= 0.8 
                  ? 'bg-green-500/20 text-green-300'
                  : selectedResult.similarity >= 0.6
                  ? 'bg-yellow-500/20 text-yellow-300'
                  : 'bg-orange-500/20 text-orange-300'
              ]">
                {{ (selectedResult.similarity * 100).toFixed(1) }}% similar
              </span>
              <div class="flex-1 h-0.5 bg-gradient-to-l from-cyan-500/50 to-transparent"></div>
            </div>
          </div>

          <!-- Información técnica -->
          <div class="grid grid-cols-2 md:grid-cols-3 gap-2 md:gap-3 text-xs">
            <div class="bg-slate-700/50 rounded-lg p-2">
              <p class="text-slate-500 font-semibold mb-1">ID de Llave</p>
              <p class="text-white font-mono text-[9px]">{{ selectedResult.id }}</p>
            </div>
            <div class="bg-slate-700/50 rounded-lg p-2">
              <p class="text-slate-500 font-semibold mb-1">Proveedor</p>
              <p class="text-white text-[9px] truncate">{{ selectedResult.proveedor }}</p>
            </div>
            <div class="bg-slate-700/50 rounded-lg p-2">
              <p class="text-slate-500 font-semibold mb-1">Stock</p>
              <p class="text-white text-[9px]">{{ selectedResult.cantidad }} un.</p>
            </div>
          </div>

          <!-- Barras de similitud detalladas -->
          <div class="space-y-2 pt-2 border-t border-slate-700">
            <div>
              <div class="flex justify-between items-center mb-1">
                <p class="text-xs font-semibold text-slate-400">Similitud General</p>
                <span class="text-xs font-bold text-white">{{ (((selectedResult.similarity ?? 0) * 100).toFixed(1)) }}%</span>
              </div>
              <div class="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full transition-all duration-300"
                  :class="`bg-gradient-to-r ${getMatchColor(selectedResult.similarity)}`"
                  :style="{ width: `${selectedResult.similarity * 100}%` }"
                ></div>
              </div>
            </div>

            <div class="grid grid-cols-2 md:grid-cols-3 gap-2 text-xs">
              <div>
                <div class="flex justify-between mb-1">
                  <span class="text-slate-400">Características</span>
                  <span class="text-slate-300 font-semibold">{{ (((selectedResult.orb_similarity ?? 0) * 100).toFixed(0)) }}%</span>
                </div>
                <div class="w-full h-1.5 bg-slate-700 rounded-full overflow-hidden">
                  <div class="h-full bg-violet-500 rounded-full" :style="{ width: `${selectedResult.orb_similarity * 100}%` }"></div>
                </div>
              </div>
              <div>
                <div class="flex justify-between mb-1">
                  <span class="text-slate-400">Líneas</span>
                  <span class="text-slate-300 font-semibold">{{ (((selectedResult.edge_similarity ?? 0) * 100).toFixed(0)) }}%</span>
                </div>
                <div class="w-full h-1.5 bg-slate-700 rounded-full overflow-hidden">
                  <div class="h-full bg-amber-500 rounded-full" :style="{ width: `${selectedResult.edge_similarity * 100}%` }"></div>
                </div>
              </div>
              <div>
                <div class="flex justify-between mb-1">
                  <span class="text-slate-400">Color</span>
                  <span class="text-slate-300 font-semibold">{{ (((selectedResult.histogram_similarity ?? 0) * 100).toFixed(0)) }}%</span>
                </div>
                <div class="w-full h-1.5 bg-slate-700 rounded-full overflow-hidden">
                  <div class="h-full bg-cyan-500 rounded-full" :style="{ width: `${selectedResult.histogram_similarity * 100}%` }"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Sin resultados -->
    <div v-else-if="comparisonResults && !comparisonResults.error" class="text-center py-8 md:py-12">
      <div class="w-12 md:w-16 h-12 md:h-16 bg-slate-800 rounded-2xl flex items-center justify-center mx-auto mb-3 md:mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 md:h-8 w-6 md:w-8 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
      </div>
      <p class="text-slate-400 font-semibold mb-1 text-sm md:text-base">No se encontraron coincidencias</p>
      <p class="text-slate-500 text-xs md:text-sm">Intenta con un umbral más bajo o carga una imagen diferente</p>
    </div>
  </div>
</template>

<style scoped>
.expand-enter-active, .expand-leave-active {
  transition: all 0.3s ease;
}

.expand-enter-from, .expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.expand-enter-to, .expand-leave-from {
  opacity: 1;
  max-height: 500px;
}
</style>
