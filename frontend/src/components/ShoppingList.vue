<script setup lang="ts">
import { computed, ref, onMounted } from 'vue';
import { shoppingStore, type ShoppingItem } from '../services/shoppingStore';
import llaveService, { type Llave } from '../services/llaveService';
import { useToast } from '../composables/useToast';

const props = defineProps<{ 
    preferredProvider?: number | string | null;
    minStockAlert?: number;
}>();

const toast = useToast();
const minAlert = computed(() => props.minStockAlert || 300);

import { watch } from 'vue';
watch(() => props.preferredProvider, async (newVal) => {
    try {
        const { data } = await llaveService.getLlaves(newVal);
        allKeys.value = data;
        // Refresh stock for items already in list
        data.forEach((llave: any) => {
            const item = Array.isArray(shoppingStore.items) ? shoppingStore.items.find((i: any) => i.id === llave.id) : undefined;
            if (item) item.stock_actual = llave.cantidad;
        });
        // Automatic scan when provider changes
        autoFill(true);
    } catch (e) {
        console.error("Error reloading keys", e);
    }
});

const groupedItems = computed(() => {
    const groups: Record<string, ShoppingItem[]> = {};
    shoppingStore.items.forEach(item => {
        // Filter by preferred provider if set
        if (props.preferredProvider && item.proveedor_id != props.preferredProvider) {
            return;
        }
        
        const provName = item.proveedor_nombre || 'Sin Proveedor';
        if (!groups[provName]) {
            groups[provName] = [];
        }
        groups[provName].push(item);
    });
    return groups;
});

const totalItems = computed(() => shoppingStore.items.length);

const updateQuantity = (id: number, event: Event) => {
    const value = parseInt((event.target as HTMLInputElement).value);
    if (value > 0) {
        shoppingStore.updateQuantity(id, value);
    }
};

const removeFromList = (id: number) => {
    shoppingStore.removeItem(id);
    toast.info('Item eliminado de la lista de compra');
};

const autoFill = async (silent = false) => {
    try {
        // Obtenemos llaves filtradas por el proveedor actual si existe
        const { data } = await llaveService.getLlaves(props.preferredProvider);
        let count = 0;
        data.forEach((llave: any) => {
            if (llave.cantidad < minAlert.value) {
                // Pass minAlert.value as targetStock to ensure it uses the user-defined threshold
                shoppingStore.addItem(llave, 0, minAlert.value); 
                count++;
            }
        });
        
        if (!silent) {
            if (count > 0) {
                toast.success(`${count} llaves con stock bajo agregadas a la lista.`);
            } else {
                toast.info('No se encontraron llaves con stock bajo para este criterio.');
            }
        }
    } catch (e) {
        console.error(e);
        if (!silent) toast.error('Error al obtener llaves para auto-relleno');
    }
};

const allKeys = ref<Llave[]>([]);
const showAddModal = ref(false);
const selectedProviderId = ref<number | null>(null);
const selectedProviderName = ref('');
const keyToAdd = ref<number | null>(null);
const qtyToAdd = ref(1);

// Helper: find key safely (handles cases where allKeys may be undefined or not an array)
const findKey = (id: number | null | undefined): Llave | undefined => {
    if (!id) return undefined;
    const list = Array.isArray(allKeys.value) ? allKeys.value : [];
    return list.find(k => k.id === id);
};

const availableKeysForProvider = computed(() => {
    const list = Array.isArray(allKeys.value) ? allKeys.value : [];
    if (!selectedProviderId.value) return list;
    return list.filter(k => k.proveedor === selectedProviderId.value);
});

const openGlobalAddModal = () => {
    selectedProviderId.value = null;
    selectedProviderName.value = 'General (Selecciona una llave)';
    keyToAdd.value = null;
    qtyToAdd.value = 1;
    showAddModal.value = true;
};

const addItemManual = () => {
    if (!keyToAdd.value) return;
    const key = findKey(keyToAdd.value);
    if (key) {
        shoppingStore.addItem({
            ...key,
            proveedor_nombre: key.proveedor_nombre || selectedProviderName.value
        }, qtyToAdd.value);
        toast.success('Item agregado manualmente');
        showAddModal.value = false;
    }
};

onMounted(async () => {
    try {
        const { data } = await llaveService.getLlaves(props.preferredProvider);
        allKeys.value = data;
        // Refresh stock for items already in list
        data.forEach((llave: any) => {
            const item = Array.isArray(shoppingStore.items) ? shoppingStore.items.find((i: any) => i.id === llave.id) : undefined;
            if (item) item.stock_actual = llave.cantidad;
        });
        // Automatic scan on mount
        autoFill(true);
    } catch (e) {
        console.error("Error loading keys", e);
    }
});

const receiveOrder = async (providerName: string) => {
    if (!confirm(`¿Confirmar recepción de pedido para ${providerName}? Esto aumentará el stock.`)) return;
    
    const itemsToProcess = groupedItems.value[providerName] || [];
    const payload = itemsToProcess.map(i => ({ id: i.id, cantidad: i.cantidad }));
    
    try {
        await llaveService.bulkIncrement(payload);
        toast.success(`Stock actualizado para ${providerName}`);
        
        // Remove processed items
        itemsToProcess.forEach(i => shoppingStore.removeItem(i.id));
    } catch (e) {
        console.error(e);
        toast.error('Error al recibir el pedido');
    }
};


const printableOrder = ref<{
    provider: string;
    items: ShoppingItem[];
    date: string;
    total: number;
    totalCost: number;
} | null>(null);

const printProviderOrder = (providerName: string) => {
    const items = groupedItems.value[providerName] || [];
    const total = items.reduce((acc, item) => acc + item.cantidad, 0);
    const totalCost = items.reduce((acc, item) => acc + (item.cantidad * (item.precio_compra || 0.90)), 0);
    
    printableOrder.value = {
        provider: providerName,
        items: items,
        date: new Date().toLocaleString('es-ES', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }),
        total: total,
        totalCost: totalCost
    };

    // Esperar a que el DOM se actualice y luego imprimir
    setTimeout(() => {
        window.print();
    }, 100);
};

</script>


<template>
    <div class="space-y-12 animate-in fade-in transition-all duration-700">
        <!-- Header Actions -->
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 no-print">
            <div class="space-y-1">
                <h2 class="text-3xl font-black text-white tracking-tight flex items-center">
                    <div class="p-2.5 bg-emerald-500/20 rounded-xl mr-4 border border-emerald-500/20 shadow-[0_0_20px_rgba(16,185,129,0.1)]">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                        </svg>
                    </div>
                    Reabastecimiento Planificado
                </h2>
                <p class="text-slate-500 font-bold ml-14">Gestión Inteligente de Adquisiciones</p>
            </div>

             <div class="flex gap-4 ml-14 md:ml-0 w-full md:w-auto">
                 <button @click="autoFill()" class="flex-1 md:flex-none glass-card bg-amber-600/10 hover:bg-amber-600 hover:text-white px-6 py-4 rounded-2xl flex items-center justify-center transition-all duration-300 font-black text-xs uppercase tracking-widest text-amber-500 group">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2 group-hover:scale-125 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Scanner Stock Bajo
                </button>
                <button @click="openGlobalAddModal" class="flex-1 md:flex-none glass-card bg-indigo-600/10 hover:bg-indigo-600 hover:text-white px-6 py-4 rounded-2xl flex items-center justify-center transition-all duration-300 font-black text-xs uppercase tracking-widest text-indigo-500 group">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                    Integración Manual
                </button>
            </div>
        </div>

        <!-- Empty State -->
        <div v-if="totalItems === 0" class="glass-card rounded-[2.5rem] p-24 text-center flex flex-col items-center justify-center border border-white/5 bg-white/[0.01]">
            <div class="w-32 h-32 rounded-[2rem] bg-slate-900 border border-white/5 flex items-center justify-center mb-10 shadow-inner group">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-14 w-14 text-slate-800 group-hover:text-amber-500/20 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
            </div>
            <h3 class="text-2xl font-black text-white mb-3 tracking-tight lowercase first-letter:uppercase">Lista de Reabastecimiento Vacía</h3>
            <p class="text-slate-500 font-bold max-w-md mx-auto leading-relaxed">Activa el scanner automático para detectar productos por debajo de la alerta de seguridad.</p>
        </div>

        <!-- Grouped Items -->
        <div v-else class="space-y-10">
            <div v-for="(items, providerName) in groupedItems" :key="providerName" class="glass-card rounded-[2.5rem] overflow-hidden border border-white/5">
                <div class="bg-white/[0.02] px-8 py-8 md:px-10 border-b border-white/5 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                    <div class="space-y-1">
                        <p class="text-[10px] font-black text-indigo-400 uppercase tracking-widest">Proveedor Asociado</p>
                        <h3 class="text-2xl font-black text-white tracking-tighter">
                            {{ providerName }}
                        </h3>
                    </div>
                    
                    <div class="flex items-center gap-4 w-full md:w-auto no-print">
                        <button @click="printProviderOrder(String(providerName))" class="flex-1 md:flex-none h-12 px-6 rounded-2xl glass-pill text-[10px] font-black uppercase tracking-widest text-slate-400 hover:text-white transition-all hover:bg-white/10 flex items-center justify-center border border-white/5">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                            </svg>
                            Imprimir
                        </button>

                        <button @click="receiveOrder(String(providerName))" class="flex-1 md:flex-none h-12 px-8 bg-emerald-600 hover:bg-emerald-500 rounded-2xl font-black text-[10px] uppercase tracking-widest text-white shadow-lg shadow-emerald-600/20 active:scale-95 transition-all flex items-center justify-center">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                            </svg>
                            Finalizar Recepción
                        </button>
                    </div>
                </div>
                
                <div class="overflow-x-auto custom-scrollbar">
                    <table class="w-full text-left border-collapse">
                         <thead>
                            <tr class="text-slate-500 text-[10px] font-black uppercase tracking-[0.2em] border-b border-white/5">
                                <th class="px-10 py-6 font-black w-[40%]">Referencia</th>
                                <th class="px-10 py-6 font-black text-center">Unidades</th>
                                <th class="px-10 py-6 font-black text-center">Stock Actual</th>
                                <th class="px-10 py-6 font-black text-center">Precio</th>
                                <th class="px-10 py-6 font-black text-center">Subtotal</th>
                                <th class="px-10 py-6 font-black text-right no-print">Acciones</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-white/5">
                             <tr v-for="item in items" :key="item.id" class="hover:bg-white/[0.02] transition-colors group">
                                <td class="px-10 py-6 whitespace-nowrap">
                                    <div class="flex items-center">
                                        <div class="h-10 w-10 rounded-2xl bg-slate-900 border border-white/5 flex items-center justify-center text-[10px] font-black text-emerald-400 mr-4 shadow-inner">
                                            ORD
                                        </div>
                                        <div>
                                            <p class="text-sm font-black text-white group-hover:text-emerald-400 transition-colors tracking-tight">{{ item.cod_llave }}</p>
                                            <p class="text-[9px] font-black text-slate-500 uppercase tracking-widest">Incr. de Inventario</p>
                                        </div>
                                    </div>
                                </td>
                                <td class="px-10 py-6">
                                     <div class="flex justify-center">
                                         <input 
                                            type="number" 
                                            min="1" 
                                            :value="item.cantidad" 
                                            @input="updateQuantity(item.id, $event)"
                                            class="w-24 h-12 bg-slate-950/80 border border-white/5 rounded-2xl text-center font-black text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all shadow-inner"
                                        />
                                     </div>
                                </td>
                                <td class="px-10 py-6 text-center text-slate-400 font-bold">
                                    {{ item.stock_actual ?? 0 }}
                                </td>
                                <td class="px-10 py-6 text-center text-slate-400 font-bold">
                                    S/ {{ Number(item.precio_compra || 0.90).toFixed(2) }}
                                </td>
                                <td class="px-10 py-6 text-center text-emerald-400 font-black">
                                    S/ {{ (item.cantidad * (item.precio_compra || 0.90)).toFixed(2) }}
                                </td>
                                <td class="px-10 py-6 text-right no-print">
                                    <button @click="removeFromList(item.id)" class="w-10 h-10 flex items-center justify-center rounded-xl bg-rose-500/10 text-rose-500 hover:bg-rose-500 hover:text-white transition-all border border-rose-500/10 active:scale-90">
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                        </svg>
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>

                    <!-- Totals Summary Section -->
                    <div class="px-10 py-8 bg-white/5 flex justify-between items-center rounded-b-3xl border-t border-white/5">
                        <div class="flex gap-12">
                            <div>
                                <p class="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Total Unidades</p>
                                <p class="text-2xl font-black text-white">{{ items.reduce((acc, i) => acc + i.cantidad, 0) }}</p>
                            </div>
                            <div>
                                <p class="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Inversión Estimada</p>
                                <p class="text-2xl font-black text-emerald-400">
                                    S/ {{ items.reduce((acc, i) => acc + (i.cantidad * (i.precio_compra || 0.90)), 0).toFixed(2) }}
                                </p>
                            </div>
                        </div>
                        <div class="text-right">
                            <p class="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Estado de Orden</p>
                            <span class="px-3 py-1 bg-amber-500/20 text-amber-500 rounded-lg text-[10px] font-black uppercase">Pendiente de Recepción</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Manual Add Modal -->
        <Transition name="fade">
            <div v-if="showAddModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4 md:p-6 bg-slate-950/90 backdrop-blur-md">
                <div class="glass-card rounded-3xl p-8 md:p-12 w-full max-w-2xl border border-white/10 shadow-[0_30px_60px_-15px_rgba(0,0,0,0.5)] animate-in slide-in-from-bottom-8 duration-500 max-h-[90vh] overflow-y-auto custom-scrollbar">
                    <div class="flex items-center justify-between mb-2">
                        <h3 class="text-4xl font-black text-white tracking-tight">Agregar Item Manual</h3>
                        <button @click="showAddModal = false" class="w-10 h-10 rounded-xl hover:bg-white/10 flex items-center justify-center transition-all">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-slate-400 hover:text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                    <p class="text-slate-400 font-bold mb-1 tracking-wide">Proveedor: <span class="text-indigo-400 font-black">{{ selectedProviderName }}</span></p>
                    
                    <div class="mt-8 space-y-8">
                        <div class="space-y-4">
                            <label class="block text-sm font-black text-slate-400 uppercase tracking-widest">Seleccionar Referencia de Llave</label>
                            <select v-model="keyToAdd" class="w-full h-16 bg-slate-900/60 border border-white/10 rounded-2xl px-6 text-white font-bold focus:outline-none focus:ring-2 focus:ring-indigo-500/50 appearance-none glass-pill text-base placeholder:text-slate-600 hover:border-white/20 transition-all">
                                <option :value="null" disabled selected class="bg-slate-950">📦 Desplegar catálogo de referencias...</option>
                                <option v-for="k in availableKeysForProvider" :key="k.id" :value="k.id" class="bg-slate-950">
                                    {{ k.cod_llave }} ({{ k.proveedor_nombre }}) — Stock actual: {{ k.cantidad }}
                                </option>
                            </select>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div class="space-y-4">
                                <label class="block text-sm font-black text-slate-400 uppercase tracking-widest">Cantidad a Adquirir</label>
                                <div class="relative">
                                    <input type="number" v-model.number="qtyToAdd" min="1" max="9999" class="w-full h-16 bg-slate-900/60 border border-white/10 rounded-2xl px-6 text-white font-black focus:outline-none focus:ring-2 focus:ring-indigo-500/50 glass-pill text-2xl hover:border-white/20 transition-all" placeholder="0">
                                    <span class="absolute right-6 top-1/2 transform -translate-y-1/2 text-slate-500 text-sm font-bold">unidades</span>
                                </div>
                            </div>

                            <div class="space-y-4">
                                <label class="block text-sm font-black text-slate-400 uppercase tracking-widest">Precio Unitario Estimado</label>
                                <div class="h-16 bg-slate-900/60 border border-white/10 rounded-2xl px-6 flex items-center text-white font-black text-lg">
                                    <span class="text-slate-500">S/</span>
                                    <span class="ml-2 text-2xl text-emerald-400">{{ keyToAdd ? Number(findKey(keyToAdd)?.precio_compra || 0.90).toFixed(2) : '0.00' }}</span>
                                </div>
                            </div>
                        </div>

                        <div v-if="keyToAdd" class="bg-indigo-600/10 border border-indigo-500/30 rounded-2xl p-6">
                            <p class="text-sm font-bold text-slate-300 mb-2">Costo Total Estimado:</p>
                            <p class="text-4xl font-black text-indigo-400">
                                S/ {{ (qtyToAdd * Number(findKey(keyToAdd)?.precio_compra || 0.90)).toFixed(2) }}
                            </p>
                        </div>
                    </div>

                    <div class="mt-12 flex flex-col sm:flex-row justify-end gap-4 border-t border-white/5 pt-8">
                        <button @click="showAddModal = false" class="h-14 px-8 rounded-2xl text-sm font-black uppercase tracking-widest text-slate-400 hover:text-white hover:bg-white/10 transition-all active:scale-95">
                            Descartar
                        </button>
                        <button 
                            @click="addItemManual" 
                            class="h-14 px-10 bg-gradient-to-r from-indigo-600 to-violet-600 rounded-2xl font-black text-sm uppercase tracking-widest text-white shadow-xl hover:shadow-indigo-600/30 hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                            </svg>
                            Integrar a la Lista
                        </button>
                    </div>
                </div>
            </div>
        </Transition>

        <!-- Hidden Printable Layout -->
        <div v-if="printableOrder" class="hidden-print-layout fixed inset-0 bg-white text-black p-12 z-[-1] opacity-0 pointer-events-none print:z-[1000] print:opacity-100 print:relative print:block">
            <div class="border-b-2 border-black pb-8 mb-8 flex justify-between items-start">
                <div>
                    <h1 class="text-3xl font-black uppercase tracking-tighter mb-1">Orden de Reabastecimiento</h1>
                    <p class="text-xl font-bold text-gray-800">Proveedor: {{ printableOrder.provider }}</p>
                </div>
                <div class="text-right">
                    <p class="text-sm font-bold uppercase tracking-widest text-gray-500">Fecha y Hora de Emisión</p>
                    <p class="text-lg font-black">{{ printableOrder.date }}</p>
                </div>
            </div>

            <table class="w-full mb-12">
                <thead>
                    <tr class="border-b-2 border-black text-left">
                        <th class="py-4 font-black uppercase text-sm">Referencia (Código)</th>
                        <th class="py-4 font-black uppercase text-sm text-center">Cantidad</th>
                        <th class="py-4 font-black uppercase text-sm text-center">Precio Unit.</th>
                        <th class="py-4 font-black uppercase text-sm text-right">Subtotal</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="item in printableOrder.items" :key="item.id" class="border-b border-gray-200">
                        <td class="py-4 font-bold text-lg cursor-default break-all pr-4">{{ item.cod_llave }}</td>
                        <td class="py-4 font-black text-xl text-center cursor-default whitespace-nowrap">{{ item.cantidad }}</td>
                        <td class="py-4 font-bold text-lg text-center cursor-default">S/ {{ Number(item.precio_compra || 0.90).toFixed(2) }}</td>
                        <td class="py-4 font-black text-xl text-right cursor-default">S/ {{ (item.cantidad * (item.precio_compra || 0.90)).toFixed(2) }}</td>
                    </tr>
                </tbody>
            </table>

            <div class="flex justify-end pt-8 border-t-2 border-black gap-12">
                <div class="text-right">
                    <p class="text-sm font-bold uppercase tracking-widest text-gray-500">Total Unidades</p>
                    <p class="text-2xl font-black">{{ printableOrder.total }}</p>
                </div>
                <div class="text-right">
                    <p class="text-sm font-bold uppercase tracking-widest text-gray-500">Monto Total de Orden</p>
                    <p class="text-4xl font-black text-black">S/ {{ printableOrder.totalCost.toFixed(2) }}</p>
                </div>
            </div>

            <div class="mt-24 text-center border-t border-gray-100 pt-8">
                <p class="text-[10px] font-bold uppercase tracking-[0.5em] text-gray-300 italic">Generado por KeyMaster Advanced Inventory Systems</p>
            </div>
        </div>
    </div>
</template>

<style scoped>
@media print {
    @page {
        margin: 15mm;
        size: portrait;
    }
    /* Hide specific global UI elements */
    header, aside, .sidebar, .top-nav, .no-print {
        display: none !important;
    }
    
    /* Ensure the main container doesn't have backgrounds/shadows that look bad in print */
    main, .glass-card, .bg-slate-950 {
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    body * {
        visibility: hidden;
    }
    
    .hidden-print-layout, 
    .hidden-print-layout * {
        visibility: visible;
        display: block !important;
    }
    
    .hidden-print-layout {
        position: fixed !important;
        left: 0 !important;
        top: 0 !important;
        width: 100% !important;
        display: block !important;
        z-index: 9999 !important;
        background: white !important;
    }
    
    /* Specific overrides for table layout in print */
    .hidden-print-layout table {
        display: table !important;
    }
    .hidden-print-layout thead {
        display: table-header-group !important;
    }
    .hidden-print-layout tbody {
        display: table-row-group !important;
    }
    .hidden-print-layout tr {
        display: table-row !important;
    }
    .hidden-print-layout th,
    .hidden-print-layout td {
        display: table-cell !important;
    }

    /* Hide scrollbars during print */
    ::-webkit-scrollbar {
        display: none;
    }
}

/* Enhance select styling subtly */
select {
    background-image: linear-gradient(to right, transparent 0%, transparent calc(100% - 1.5rem), rgba(99,102,241,0.3) calc(100% - 1.5rem), rgba(99,102,241,0.3) 100%);
}

select:hover {
    border-color: rgba(99,102,241,0.4) !important;
    background-image: linear-gradient(to right, transparent 0%, transparent calc(100% - 1.5rem), rgba(99,102,241,0.5) calc(100% - 1.5rem), rgba(99,102,241,0.5) 100%);
}

select:focus {
    background-image: linear-gradient(to right, transparent 0%, transparent calc(100% - 1.5rem), rgba(99,102,241,0.6) calc(100% - 1.5rem), rgba(99,102,241,0.6) 100%);
}
</style>
