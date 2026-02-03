<script setup lang="ts">
import { computed, ref } from 'vue';
import { checkoutStore } from '../services/checkoutStore';
import llaveService, { type Llave } from '../services/llaveService';
import { onMounted } from 'vue';
import { useToast } from '../composables/useToast';

const toast = useToast();
const items = computed(() => checkoutStore.items);

// Modal state
const showConfirmModal = ref(false);
const isProcessing = ref(false);
const processResult = ref<{ success: boolean; message: string } | null>(null);
const showResultModal = ref(false);

const removeFromList = (id: number) => {
    checkoutStore.removeItem(id);
};

const updateQuantity = (id: number, event: Event) => {
    const val = parseInt((event.target as HTMLInputElement).value);
    if (val > 0) {
        checkoutStore.updateQuantity(id, val);
    }
};

onMounted(async () => {
    try {
        const { data } = await llaveService.getLlaves();
        // Refresh stock for items already in checkout list
        data.forEach((llave: Llave) => {
            const item = checkoutStore.items.find((i: any) => i.id === llave.id);
            if (item) item.stock_actual = llave.cantidad;
        });
    } catch (e) {
        console.error("Error reloading stock for checkout", e);
    }
});

const openConfirmModal = () => {
    if (items.value.length === 0) return;
    showConfirmModal.value = true;
};

const cancelProcess = () => {
    showConfirmModal.value = false;
};

const confirmProcess = async () => {
    showConfirmModal.value = false;
    isProcessing.value = true;

    try {
        await llaveService.bulkDecrement(items.value);
        processResult.value = {
            success: true,
            message: 'Inventario actualizado correctamente. Las llaves han sido retiradas del sistema.'
        };
        checkoutStore.clear();
    } catch (error) {
        console.error('Error procesando salida', error);
        processResult.value = {
            success: false,
            message: 'Hubo un error al procesar la salida. Por favor, revisa la consola o intenta de nuevo.'
        };
    } finally {
        isProcessing.value = false;
        showResultModal.value = true;
    }
};

const closeResultModal = () => {
    showResultModal.value = false;
    processResult.value = null;
};
</script>


<template>
  <div class="max-w-4xl mx-auto space-y-10 animate-in fade-in transition-all duration-700">
    <div class="glass-card rounded-[2.5rem] p-10 relative overflow-hidden group">
        <!-- Decoration -->
        <div class="absolute top-0 right-0 w-32 h-32 bg-rose-600/10 rounded-full blur-3xl group-hover:bg-rose-600/20 transition-all duration-700"></div>

        <div class="relative">
            <h2 class="text-3xl font-black text-white mb-10 flex items-center tracking-tight">
                <div class="p-3 bg-rose-600/20 rounded-2xl mr-4 border border-rose-500/20">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                </div>
                Revisión de Salida
            </h2>

            <!-- Empty State -->
            <div v-if="items.length === 0" class="text-center py-20">
                <div class="w-24 h-24 rounded-3xl bg-slate-900 border border-white/5 flex items-center justify-center mx-auto mb-8 shadow-inner">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-slate-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                    </svg>
                </div>
                <h3 class="text-xl font-black text-white mb-2 uppercase tracking-widest">Lista Vacía</h3>
                <p class="text-slate-500 font-bold mb-8">No has seleccionado llaves para retirar todavía.</p>
                <div class="h-1 w-20 bg-slate-800 mx-auto rounded-full"></div>
            </div>

            <!-- Items List -->
            <div v-else class="space-y-4">
                <div v-for="item in items" :key="item.id" 
                    class="glass-card rounded-[2rem] p-6 flex flex-col sm:flex-row items-center justify-between gap-6 border border-white/5 hover:bg-white/[0.04] transition-all group/item"
                >
                    <div class="flex items-center space-x-6">
                        <div class="h-14 w-14 rounded-2xl bg-slate-900 flex items-center justify-center border border-white/5 shadow-inner">
                            <span class="text-xs font-black text-rose-400">KEY</span>
                        </div>
                        <div>
                            <h4 class="text-xl font-black text-white group-hover:text-rose-400 transition-colors uppercase tracking-widest leading-none mb-1">
                                {{ item.cod_llave }}
                            </h4>
                            <p class="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Referencia Única</p>
                        </div>
                    </div>

                    <div class="flex flex-col items-center sm:items-start">
                        <p class="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1">Stock en Almacén</p>
                        <span class="text-sm font-black text-slate-300">
                             {{ item.stock_actual ?? 0 }} UNIDADES
                        </span>
                    </div>

                    <div class="flex items-center space-x-6">
                        <div class="flex flex-col items-end mr-4">
                            <label class="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-2">Cantidad</label>
                            <input 
                                type="number" 
                                min="1" 
                                :value="item.cantidad" 
                                @input="updateQuantity(item.id, $event)"
                                class="w-24 h-12 bg-slate-950/80 border border-white/5 rounded-2xl text-center font-black text-white focus:outline-none focus:ring-2 focus:ring-rose-500/50 transition-all shadow-inner"
                            />
                        </div>
                        
                        <button @click="removeFromList(item.id)" class="w-12 h-12 flex items-center justify-center rounded-2xl bg-rose-500/10 text-rose-500 hover:bg-rose-500 hover:text-white transition-all border border-rose-500/20 active:scale-95">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                        </button>
                    </div>
                </div>

                <!-- Footer Summary & Action -->
                <div class="mt-20 pt-10 border-t border-white/5">
                    <div class="flex flex-col sm:flex-row justify-between items-center gap-8">
                        <div class="text-center sm:text-left">
                            <p class="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] mb-1">Total de Referencias</p>
                            <p class="text-4xl font-black text-white tracking-tighter">{{ items.length }} <span class="text-sm font-bold text-slate-600 uppercase tracking-widest ml-2">Tipos de llave</span></p>
                        </div>
                        
                        <button 
                            @click="openConfirmModal" 
                            class="w-full sm:w-auto px-12 py-5 bg-gradient-to-r from-rose-600 to-orange-600 rounded-3xl font-black text-sm uppercase tracking-widest text-white shadow-[0_10px_30px_rgba(225,29,72,0.3)] hover:scale-[1.02] active:scale-[0.98] transition-all duration-300 flex items-center justify-center"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                            </svg>
                            Confirmar Procesamiento
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal de Confirmación -->
    <div v-if="showConfirmModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="bg-gradient-to-br from-slate-800 to-slate-900 rounded-3xl border border-white/10 shadow-2xl max-w-md w-full animate-in zoom-in-95 duration-200">
            <!-- Header -->
            <div class="p-8 border-b border-white/10 bg-gradient-to-r from-rose-600/10 to-orange-600/10">
                <div class="flex items-center gap-3">
                    <div class="w-12 h-12 rounded-xl bg-rose-600/20 border border-rose-500/30 flex items-center justify-center">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    </div>
                    <div>
                        <h3 class="text-xl font-black text-white">Confirmar Procesamiento</h3>
                        <p class="text-xs text-slate-400 mt-1">Acción permanente en el inventario</p>
                    </div>
                </div>
            </div>

            <!-- Body -->
            <div class="p-8 space-y-4">
                <p class="text-slate-300 text-sm leading-relaxed">
                    Se descontarán <span class="font-black text-rose-400">{{ items.length }} tipo(s) de llave</span> del inventario de forma <span class="font-black text-amber-400">permanente</span>.
                </p>
                
                <div class="bg-slate-900/50 border border-amber-500/20 rounded-xl p-4">
                    <p class="text-xs font-bold text-amber-400 uppercase tracking-widest mb-2">⚠️ Advertencia</p>
                    <p class="text-xs text-slate-300">Esta acción no se puede deshacer. Asegúrate de que los datos sean correctos.</p>
                </div>

                <div class="max-h-40 overflow-y-auto space-y-2 bg-slate-900/30 rounded-xl p-3">
                    <div v-for="item in items" :key="item.id" class="flex justify-between items-center text-xs p-2 bg-slate-800/50 rounded-lg">
                        <span class="font-bold text-white">{{ item.cod_llave }}</span>
                        <span class="text-slate-400">{{ item.cantidad }} un.</span>
                    </div>
                </div>
            </div>

            <!-- Footer -->
            <div class="p-6 border-t border-white/10 bg-slate-900/50 flex gap-3 rounded-b-3xl">
                <button 
                    @click="cancelProcess"
                    class="flex-1 px-4 py-3 rounded-xl font-bold text-sm uppercase tracking-widest text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 transition-all active:scale-95"
                >
                    Cancelar
                </button>
                <button 
                    @click="confirmProcess"
                    :disabled="isProcessing"
                    class="flex-1 px-4 py-3 rounded-xl font-bold text-sm uppercase tracking-widest text-white bg-gradient-to-r from-rose-600 to-orange-600 hover:shadow-lg hover:shadow-rose-600/50 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                    <svg v-if="isProcessing" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ isProcessing ? 'Procesando...' : 'Confirmar' }}
                </button>
            </div>
        </div>
    </div>

    <!-- Modal de Resultado -->
    <div v-if="showResultModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div :class="[
            'rounded-3xl border shadow-2xl max-w-md w-full animate-in zoom-in-95 duration-200 bg-gradient-to-br',
            processResult?.success 
                ? 'from-slate-800 to-slate-900 border-emerald-500/20' 
                : 'from-slate-800 to-slate-900 border-red-500/20'
        ]">
            <!-- Header -->
            <div :class="[
                'p-8 border-b flex items-center gap-3',
                processResult?.success 
                    ? 'border-emerald-500/20 bg-gradient-to-r from-emerald-600/10 to-green-600/10' 
                    : 'border-red-500/20 bg-gradient-to-r from-red-600/10 to-orange-600/10'
            ]">
                <div :class="[
                    'w-12 h-12 rounded-xl border flex items-center justify-center',
                    processResult?.success 
                        ? 'bg-emerald-600/20 border-emerald-500/30' 
                        : 'bg-red-600/20 border-red-500/30'
                ]">
                    <svg v-if="processResult?.success" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4v2m0 4v2M8.228 9c-.549-1.165-2.03-2-3.772-2C2.343 7 1 8.343 1 10c0 1.4 1.278 2.575 3.006 2.907.542.104.994.54.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                </div>
                <div>
                    <h3 :class="['text-xl font-black', processResult?.success ? 'text-emerald-400' : 'text-red-400']">
                        {{ processResult?.success ? '¡Éxito!' : 'Error' }}
                    </h3>
                    <p class="text-xs text-slate-400 mt-1">{{ processResult?.message }}</p>
                </div>
            </div>

            <!-- Body -->
            <div class="p-8">
                <p class="text-sm text-slate-300 text-center">
                    {{ processResult?.success 
                        ? 'El inventario ha sido actualizado exitosamente en el sistema.'
                        : 'Por favor, intenta nuevamente o contacta con soporte.'
                    }}
                </p>
            </div>

            <!-- Footer -->
            <div class="p-6 border-t border-white/10 bg-slate-900/50 rounded-b-3xl">
                <button 
                    @click="closeResultModal"
                    :class="[
                        'w-full px-4 py-3 rounded-xl font-bold text-sm uppercase tracking-widest transition-all active:scale-95',
                        processResult?.success 
                            ? 'bg-gradient-to-r from-emerald-600 to-green-600 text-white hover:shadow-lg hover:shadow-emerald-600/50' 
                            : 'bg-gradient-to-r from-red-600 to-orange-600 text-white hover:shadow-lg hover:shadow-red-600/50'
                    ]"
                >
                    {{ processResult?.success ? 'Continuar' : 'Aceptar' }}
                </button>
            </div>
        </div>
    </div>
  </div>
</template>