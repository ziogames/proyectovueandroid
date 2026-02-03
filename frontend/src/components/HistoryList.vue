<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import historyService, { type CheckoutHistoryItem } from '../services/historyService';
import userService, { type User } from '../services/userService';

const history = ref<CheckoutHistoryItem[]>([]);
const users = ref<User[]>([]);
const loading = ref(true);

const filters = ref({
    user: '' as string | number,
    fecha: ''
});

const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
};

const fetchHistory = async () => {
    loading.value = true;
    try {
        const params: any = {};
        if (filters.value.user) params.user = filters.value.user;
        if (filters.value.fecha) params.fecha = filters.value.fecha;
        
        const { data } = await historyService.getHistory(params);
        history.value = data;
    } catch (e) {
        console.error('Error fetching history', e);
    } finally {
        loading.value = false;
    }
};

const fetchUsers = async () => {
    try {
        const { data } = await userService.getUsers();
        users.value = data;
    } catch (e) {
        console.error('Error fetching users', e);
    }
};

const today = new Date().toISOString().split('T')[0] as string;
const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0] as string;

const setQuickDate = (date: string) => {
    filters.value.fecha = date;
};

const openDatePicker = (event: any) => {
    if (event.target.showPicker) {
        event.target.showPicker();
    }
};

const clearFilters = () => {
    filters.value = { user: '', fecha: '' };
};

watch(filters, () => {
    fetchHistory();
}, { deep: true });

onMounted(() => {
    fetchHistory();
    fetchUsers();
});
</script>

<template>
  <div class="space-y-10 animate-in fade-in transition-all duration-700">
    <!-- Filters Area -->
    <div class="glass-card card-animate rounded-[2.5rem] p-8 lg:p-10 relative overflow-hidden group">
        <!-- Decoration -->
        <div class="absolute top-0 right-0 w-32 h-32 bg-cyan-600/10 rounded-full blur-3xl group-hover:bg-cyan-600/20 transition-all duration-700"></div>

        <div class="relative">
            <div class="flex flex-col md:flex-row gap-8 items-end">
                <div class="flex-1 w-full md:w-auto space-y-3">
                    <label class="block text-xs font-black text-slate-500 uppercase tracking-widest ml-1 flex items-center">
                        <div class="w-1 h-3 bg-violet-500 rounded-full mr-2"></div>
                        Usuario Responsable
                    </label>
                    <select 
                        v-model="filters.user"
                        class="w-full bg-slate-900/50 border border-white/5 rounded-2x; px-5 py-4 text-white focus:outline-none focus:ring-2 focus:ring-violet-500/50 transition-all font-bold appearance-none glass-pill"
                    >
                        <option value="">Todos los registros</option>
                        <option v-for="user in users" :key="user.id" :value="user.id">
                            {{ user.first_name && user.last_name ? `${user.first_name} ${user.last_name}` : user.username }}
                        </option>
                    </select>
                </div>

                <div class="flex-[1.5] w-full md:w-auto space-y-3">
                    <div class="flex justify-between items-center ml-1">
                        <label class="block text-xs font-black text-slate-500 uppercase tracking-widest flex items-center">
                            <div class="w-1 h-3 bg-cyan-500 rounded-full mr-2"></div>
                            Periodo de Salida
                        </label>
                        <div class="flex gap-2">
                             <button @click="setQuickDate(today)" class="text-[9px] font-black uppercase px-2.5 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-all border border-white/5">Hoy</button>
                             <button @click="setQuickDate(yesterday)" class="text-[9px] font-black uppercase px-2.5 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-all border border-white/5">Ayer</button>
                        </div>
                    </div>
                    <input 
                        v-model="filters.fecha"
                        type="date"
                        :max="today"
                        @click="openDatePicker"
                        @keydown.prevent
                        class="w-full bg-slate-900/50 border border-white/5 rounded-2xl px-5 py-4 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500/50 transition-all cursor-pointer font-bold glass-pill"
                    />
                </div>

                <div class="flex-none pb-1">
                    <button 
                        @click="clearFilters"
                        class="px-6 py-4 rounded-2xl text-xs font-black uppercase tracking-widest text-slate-500 hover:text-rose-400 transition-all flex items-center group/btn active:scale-95"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2 opacity-50 group-hover/btn:opacity-100 transition-opacity" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                        Resetear
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- History Table Container -->
    <div class="glass-card card-animate rounded-[2.5rem] overflow-hidden border border-white/5">
        <div class="px-8 py-8 md:px-10 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
            <div>
                <h3 class="text-2xl font-black text-white flex items-center gap-3 tracking-tight">
                    Resumen de Operaciones
                    <span class="px-2 py-0.5 rounded-lg bg-violet-600/20 text-violet-400 text-[10px] font-black">{{ history.length }} MOVIMIENTOS</span>
                </h3>
            </div>
            <button @click="fetchHistory" class="w-12 h-12 flex items-center justify-center rounded-2xl glass-pill text-slate-400 hover:text-white transition-all hover:bg-white/10" title="Refrescar">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
            </button>
        </div>

        <div class="overflow-x-auto custom-scrollbar">
            <table class="w-full text-left border-collapse">
                <thead>
                    <tr class="text-slate-500 text-[10px] font-black uppercase tracking-[0.2em] border-b border-white/5">
                        <th class="px-10 py-6 font-black">Cronología</th>
                        <th class="px-10 py-6 font-black">Operador</th>
                        <th class="px-10 py-6 font-black">Referencia de Llave</th>
                        <th class="px-10 py-6 font-black text-right">Volumen</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-white/5">
                    <tr v-if="loading">
                        <td colspan="4" class="px-10 py-32 text-center text-slate-500">
                            <div class="flex flex-col items-center justify-center space-y-4">
                                <div class="flex space-x-2">
                                    <div class="w-3 h-3 bg-violet-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                                    <div class="w-3 h-3 bg-violet-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                                    <div class="w-3 h-3 bg-violet-500 rounded-full animate-bounce"></div>
                                </div>
                                <span class="text-sm font-bold tracking-widest uppercase">Sincronizando datos...</span>
                            </div>
                        </td>
                    </tr>
                    <tr v-else-if="history.length === 0" class="hover:bg-white/[0.02] transition-all">
                        <td colspan="4" class="px-10 py-32 text-center">
                            <div class="flex flex-col items-center justify-center opacity-30">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                                <p class="text-lg font-black uppercase tracking-widest">Sin coincidencias</p>
                            </div>
                        </td>
                    </tr>
                    <tr v-else v-for="item in history" :key="item.id" class="hover:bg-white/[0.02] transition-colors group">
                        <td class="px-10 py-6 whitespace-nowrap text-slate-400 font-bold text-sm">
                            <span class="group-hover:text-white transition-colors">{{ formatDate(item.fecha) }}</span>
                        </td>
                        <td class="px-10 py-6 whitespace-nowrap">
                            <div class="flex items-center">
                                <div class="h-10 w-10 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 flex items-center justify-center text-[10px] font-black text-violet-400 mr-4 border border-white/5 shadow-lg group-hover:scale-110 transition-transform">
                                    {{ item.user_name ? item.user_name.substring(0,2).toUpperCase() : '??' }}
                                </div>
                                <span class="text-sm font-black text-white group-hover:text-violet-400 transition-colors">{{ item.user_name || 'Desconocido' }}</span>
                            </div>
                        </td>
                        <td class="px-10 py-6 whitespace-nowrap">
                            <span class="px-4 py-1.5 rounded-xl bg-violet-600/10 text-violet-400 border border-violet-500/10 text-xs font-black tracking-widest group-hover:bg-violet-600/20 transition-all">
                                {{ item.llave_codigo }}
                            </span>
                        </td>
                        <td class="px-10 py-6 whitespace-nowrap text-right">
                            <span class="text-white font-black bg-slate-900/80 px-4 py-2 rounded-2xl border border-white/5 shadow-inner text-sm group-hover:bg-slate-900 group-hover:border-violet-500/20 transition-all">
                                {{ item.cantidad }}
                            </span>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
  </div>
</template>
