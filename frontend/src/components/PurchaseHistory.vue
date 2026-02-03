<script setup lang="ts">
import { ref, onMounted } from 'vue';
import purchaseService, { type PurchaseRecord } from '../services/purchaseService';
import proveedorService, { type Proveedor } from '../services/proveedorService';

const purchases = ref<PurchaseRecord[]>([]);
const proveedores = ref<Proveedor[]>([]);
const loading = ref(true);

const filterUser = ref('');
const filterDate = ref('');

const loadData = async () => {
    loading.value = true;
    try {
        const [purchResponse, provResponse] = await Promise.all([
            purchaseService.getPurchases(filterUser.value, filterDate.value),
            proveedorService.getProveedores()
        ]);
        purchases.value = purchResponse.data;
        proveedores.value = provResponse.data;
    } catch (e) {
        console.error("Error loading purchase history", e);
    } finally {
        loading.value = false;
    }
};

onMounted(loadData);

const formatDate = (dateStr: string) => {
    const d = new Date(dateStr);
    return d.toLocaleString('es-ES', { 
        day: '2-digit', 
        month: 'short', 
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};
</script>

<template>
    <div class="space-y-12 animate-in fade-in transition-all duration-700">
        <!-- summary Stats -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 no-print">
            <div class="glass-card card-animate rounded-3xl p-8 flex items-center bg-gradient-to-br from-emerald-600/10 to-teal-600/10 border border-emerald-500/20 animate-float">
                <div class="w-14 h-14 rounded-2xl bg-emerald-500/20 flex items-center justify-center mr-6">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                </div>
                <div>
                    <p class="text-[10px] font-black text-emerald-500/60 uppercase tracking-[0.2em] mb-1">Inversión Total Acumulada</p>
                    <h4 class="text-3xl font-black text-white">S/ {{ purchases.reduce((acc, p) => acc + (p.cantidad * Number(p.precio_pago || 0)), 0).toFixed(2) }}</h4>
                </div>
            </div>

            <div class="glass-card card-animate rounded-3xl p-8 flex items-center bg-gradient-to-br from-indigo-600/10 to-violet-600/10 border border-indigo-500/20 animate-float">
                <div class="w-14 h-14 rounded-2xl bg-indigo-500/20 flex items-center justify-center mr-6">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                    </svg>
                </div>
                <div>
                    <p class="text-[10px] font-black text-indigo-500/60 uppercase tracking-[0.2em] mb-1">Registros de Compra</p>
                    <h4 class="text-3xl font-black text-white">{{ purchases.length }}</h4>
                </div>
            </div>
        </div>

        <!-- Filters -->
        <div class="flex flex-col md:flex-row gap-6">
            <div class="flex-1 space-y-2">
                <label class="block text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] ml-1">Filtrar por Proveedor</label>
                <div class="relative group">
                    <select 
                        v-model="filterUser" 
                        @change="loadData"
                        class="w-full h-14 bg-slate-900/50 border border-white/5 rounded-2xl px-6 text-white font-black focus:outline-none focus:ring-2 focus:ring-emerald-500/50 appearance-none glass-pill transition-all"
                    >
                        <option value="">Todos los proveedores</option>
                        <option v-for="p in proveedores" :key="p.id" :value="p.id">{{ p.nombre }}</option>
                    </select>
                    <div class="absolute right-6 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M19 9l-7 7-7-7" />
                        </svg>
                    </div>
                </div>
            </div>

            <div class="flex-1 space-y-2">
                <label class="block text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] ml-1">Filtrar por Fecha</label>
                <input 
                    type="date" 
                    v-model="filterDate" 
                    @change="loadData"
                    class="w-full h-14 bg-slate-900/50 border border-white/5 rounded-2xl px-6 text-white font-black focus:outline-none focus:ring-2 focus:ring-emerald-500/50 glass-pill transition-all [color-scheme:dark]"
                />
            </div>
        </div>

        <!-- Table Container -->
        <div class="glass-card card-animate rounded-[2.5rem] overflow-hidden border border-white/5 shadow-2xl relative">
            <div v-if="loading" class="absolute inset-0 bg-slate-950/40 backdrop-blur-sm z-10 flex items-center justify-center">
                <div class="flex flex-col items-center">
                    <div class="w-12 h-12 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin mb-4"></div>
                    <p class="text-xs font-black text-emerald-500 uppercase tracking-widest">Sincronizando Historial...</p>
                </div>
            </div>

            <div class="overflow-x-auto custom-scrollbar">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="text-slate-500 text-[10px] font-black uppercase tracking-[0.2em] border-b border-white/5 bg-white/[0.02]">
                            <th class="px-10 py-7 font-black">Referencia de Llave</th>
                            <th class="px-10 py-7 font-black text-center">Proveedor</th>
                            <th class="px-10 py-7 font-black text-center">Cantidad</th>
                            <th class="px-10 py-7 font-black text-center">Precio Pagado</th>
                            <th class="px-10 py-7 font-black text-center">Inversión</th>
                            <th class="px-10 py-7 font-black text-right">Fecha</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-white/5 font-bold">
                        <tr v-for="item in purchases" :key="item.id" class="hover:bg-white/[0.02] transition-colors group">
                            <td class="px-10 py-6 whitespace-nowrap">
                                <div class="flex items-center">
                                    <div class="h-10 w-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mr-4 group-hover:scale-110 transition-transform">
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                                        </svg>
                                    </div>
                                    <div>
                                        <p class="text-sm font-black text-white group-hover:text-emerald-400 transition-colors">{{ item.llave_codigo }}</p>
                                        <p class="text-[9px] text-slate-500 uppercase tracking-widest">Código Interno</p>
                                    </div>
                                </div>
                            </td>
                            <td class="px-10 py-6 text-center">
                                <span class="bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-4 py-2 rounded-xl text-xs font-black uppercase tracking-widest whitespace-nowrap">
                                    {{ item.proveedor_nombre }}
                                </span>
                            </td>
                            <td class="px-10 py-6 text-center whitespace-nowrap">
                                <span class="text-lg font-black text-white">+{{ item.cantidad }}</span>
                                <span class="text-[10px] text-emerald-500 ml-1 font-black">UNID</span>
                            </td>
                            <td class="px-10 py-6 text-center text-slate-400">
                                S/ {{ Number(item.precio_pago || 0).toFixed(2) }}
                            </td>
                            <td class="px-10 py-6 text-center text-emerald-400 font-black">
                                S/ {{ (item.cantidad * Number(item.precio_pago || 0)).toFixed(2) }}
                            </td>
                            <td class="px-10 py-6 text-right font-medium text-slate-400 text-sm">
                                {{ formatDate(item.fecha) }}
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Empty State -->
            <div v-if="purchases.length === 0 && !loading" class="p-24 text-center">
                <div class="w-24 h-24 rounded-3xl bg-slate-900 border border-white/5 flex items-center justify-center mb-8 mx-auto shadow-inner card-animate">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-slate-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0a2 2 0 01-2 2H6a2 2 0 01-2-2m16 0l-8 5-8-5" />
                    </svg>
                </div>
                <h3 class="text-2xl font-black text-white mb-2 tracking-tight">Sin Historial de Compras</h3>
                <p class="text-slate-500 font-bold max-w-xs mx-auto text-sm">No se encontraron registros de ingreso para los criterios seleccionados.</p>
            </div>
        </div>
    </div>
</template>
