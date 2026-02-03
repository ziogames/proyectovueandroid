<script setup lang="ts">
import { ref, onMounted } from 'vue';
import ProveedorList from './components/ProveedorList.vue';
import LlaveList from './components/LlaveList.vue';
import DashboardCharts from './components/DashboardCharts.vue';
import AIChat from './components/AIChat.vue';
import CheckoutList from './components/CheckoutList.vue';
import ShoppingList from './components/ShoppingList.vue';
import HistoryList from './components/HistoryList.vue';
import ToastNotification from './components/ToastNotification.vue';
import SettingsModal from './components/SettingsModal.vue';
import Login from './components/Login.vue';
import PurchaseHistory from './components/PurchaseHistory.vue';
import ImageComparison from './components/ImageComparison.vue';
import { checkoutStore } from './services/checkoutStore';
import { computed } from 'vue';

import api from './services/api';
import llaveService, { type Llave } from './services/llaveService';

// Auth State
const isAuthenticated = ref(false);
const checkoutCount = computed(() => checkoutStore.items.length);
const userId = ref<number | null>(null);
const userName = ref('Usuario');
const userInitials = ref('US');
const isSuperAdmin = ref(false);
const lowStockKeys = ref<Llave[]>([]);
const allProveedores = ref<any[]>([]);
const userProfile = ref({ 
    min_stock_alert: 300, 
    theme_color: 'indigo',
    active_provider_color: 'indigo',
    preferred_provider: null,
    preferred_provider_name: null
});
const showSettings = ref(false);

const groupedLowStockKeys = computed(() => {
    const groups: Record<string, Llave[]> = {};
    lowStockKeys.value.forEach(k => {
        const name = k.proveedor_nombre || 'Proveedor Desconocido';
        if (!groups[name]) groups[name] = [];
        groups[name].push(k);
    });
    return groups;
});

import proveedorService from './services/proveedorService';

const fetchProviders = async () => {
    try {
        const { data } = await proveedorService.getProveedores();
        allProveedores.value = data;
    } catch (e) {
        console.error("Error fetching providers", e);
    }
};

const fetchUserInfo = async () => {
    try {
        const { data } = await api.get('/users/me/');
        userId.value = data.id;
        isSuperAdmin.value = data.is_superuser;
        if (data.first_name && data.last_name) {
            userName.value = `${data.first_name} ${data.last_name}`;
            userInitials.value = `${data.first_name[0]}${data.last_name[0]}`.toUpperCase();
        } else {
             userName.value = data.username;
             userInitials.value = data.username.substring(0,2).toUpperCase();
        }
        
        // Load profile if exists
        if (data.profile) {
            userProfile.value = {
                ...userProfile.value,
                ...data.profile,
                active_provider_color: data.profile.active_provider_color || 'indigo'
            };
        }
    } catch (e) {
        console.error("Error fetching user", e);
    }
};

const checkLowStock = async () => {
    try {
        const { data } = await llaveService.getLlaves(); // Fetch all keys for global alerts
        lowStockKeys.value = data.filter((k: Llave) => k.cantidad < userProfile.value.min_stock_alert);
    } catch (e) {
        console.error("Error checking stock", e);
    }
};

const updateProfile = async (newSettings: any) => {
    try {
        const { data } = await api.patch('/users/update_profile/', newSettings);
        userProfile.value = data;
        checkLowStock(); // Re-check with new threshold
        
        // Use a simple toast here or rely on the reactive update
        // We need 'toast' available here ideally. 
        // Since setup script, we don't have global app context easily without injection.
        // Assuming user will see visual feedback.
    } catch (e) {
        console.error("Error updating profile", e);
    }
};

const checkAuth = () => {
    const token = localStorage.getItem('access_token');
    isAuthenticated.value = !!token;
    if (isAuthenticated.value) {
        fetchUserInfo();
        checkLowStock();
        fetchProviders();
    }
};

const handleLogin = () => {
    isAuthenticated.value = true;
    fetchUserInfo();
    checkLowStock();
    fetchProviders();
};

const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    isAuthenticated.value = false;
    currentTab.value = 'proveedores';
    userName.value = 'Usuario';
    lowStockKeys.value = [];
    checkoutStore.clear();
};

onMounted(() => {
    checkAuth();
});

// Navigation State
const currentTab = ref('proveedores');
const isSidebarOpen = ref(false);

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value;
};

const getTitle = () => {
    console.log('Current Tab:', currentTab.value);
    switch(currentTab.value) {
        case 'proveedores': return 'Directorio de Proveedores';
        case 'llaves': return 'Inventario de Llaves';
        case 'informacion': return 'Estadísticas e Información';
        case 'ai': return 'Asistente Inteligente';
        case 'comparacion': return 'Comparador de Imágenes';
        case 'checkout': return 'Lista de Salida';
        case 'shopping': return 'Lista de Compra';
        case 'historial': return 'Historial de Salidas';
        case 'compras_historial': return 'Historial de Compras';
        default: return 'Dashboard';
    }
};

const getDescription = () => {
     switch(currentTab.value) {
        case 'proveedores': return 'Administra tus proveedores.';
        case 'llaves': return 'Gestiona el stock de tus llaves.';
        case 'informacion': return 'Visualiza el rendimiento de tu inventario.';
        case 'ai': return 'Consulta tu base de datos en lenguaje natural.';
        case 'comparacion': return 'Compara imágenes de llaves con tu base de datos.';
        case 'checkout': return 'Revisa y confirma las llaves a retirar del inventario.';
        case 'shopping': return 'Genera órdenes y recibe stock.';
        case 'historial': return 'Registro histórico de llaves retiradas del inventario.';
        case 'compras_historial': return 'Registro histórico de llaves adquiridas de proveedores.';
        default: return '';
    }
}
const getThemeStyles = computed(() => {
    // Definir mapa de colores si se usaran variables CSS, o confiar en clases si los subcomponentes las usaran.
    // Como estamos usando clases de Tailwind 'bg-indigo-600', cambiar esto dinamicamente requeriria safelisting o usar variables css.
    // La mejor opcion rapida es inyectar variables CSS que Tailwind pueda usar o sobreescribir colores.
    // Sin embargo, Tailwind v3 compila clases. No podemos simplemente concatenar 'text-'+color+... si no estan en safelist.
    // Opcion mejor: Usar Color CSS Vars.
    
    const colorMap: Record<string, string> = {
        indigo: '#4f46e5',
        red: '#dc2626',
        green: '#16a34a',
        blue: '#2563eb',
        purple: '#9333ea',
        pink: '#db2777'
    };
    
    // Podemos intentar sobreescribir --tw-text-opacity etc, pero es complejo.
    // Mejor enfoque: Hacer que los componentes usen una clase raiz y CSS variables.
    // O simplemente usar clases condicionales.
    // Dado que el proyecto ya tiene muchas clases hardcodeadas 'text-indigo-500', 
    // lo más efectivo sin refactorizar TODO es usar un replace global solo visualmente? No.
    // Vamos a usar variables CSS y un pequeño hack de estilo global si es posible, o 
    // simplemente definir que para ESTA feature, los elementos principales (header, sidebar buttons) cambien.
    
    return {
        '--theme-color': colorMap[userProfile.value.theme_color] || '#4f46e5'
    };
});
</script>


<template>
  <!-- Background Glows -->
  <div class="fixed inset-0 overflow-hidden pointer-events-none z-0 no-print">
    <div class="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-purple-600/10 rounded-full blur-[120px]"></div>
    <div class="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-cyan-600/10 rounded-full blur-[120px]"></div>
  </div>

  <ToastNotification class="no-print" />
  
  <SettingsModal 
    v-model="showSettings" 
    :current-alert="userProfile.min_stock_alert" 
    :current-color="userProfile.theme_color"
    :current-highlight-color="userProfile.active_provider_color"
    :current-provider="userProfile.preferred_provider"
    :providers="allProveedores"
    @save="updateProfile"
  />

  <!-- Login Screen -->
  <Login v-if="!isAuthenticated" @login-success="handleLogin" />

  <!-- Dashboard -->
  <div v-else class="flex h-screen text-white overflow-hidden relative z-10" :style="getThemeStyles">
    
    <!-- Mobile Header -->
    <div class="lg:hidden fixed top-4 left-4 right-4 h-16 glass-card rounded-2xl flex items-center justify-between px-4 z-50 no-print">
        <h1 class="text-xl font-bold tracking-tighter bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent">
            KEY<span class="text-white">MASTER</span>
        </h1>
        
        <!-- Mobile Header Actions -->
        <div class="flex items-center space-x-2">
            <!-- Settings Button -->
            <button @click="showSettings = true" class="w-10 h-10 flex items-center justify-center rounded-lg bg-slate-800/50 text-slate-400 hover:bg-slate-700 hover:text-white transition-all">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
            </button>

            <!-- Notifications/Alerts -->
            <div class="relative group" v-if="lowStockKeys.length > 0">
                <button class="w-10 h-10 flex items-center justify-center rounded-lg bg-amber-500/10 text-amber-500 hover:bg-amber-500/20 transition-all">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 animate-bounce" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                    </svg>
                </button>
                <!-- Simplified Dropdown for Mobile -->
                <div class="absolute right-0 top-full pt-2 w-72 hidden group-hover:block z-[100] animate-in fade-in slide-in-from-top-4">
                    <div class="bg-slate-800 border border-slate-700 rounded-2xl p-4 shadow-2xl">
                        <div class="flex justify-between items-center mb-3">
                            <h4 class="text-xs font-black uppercase tracking-widest text-amber-500">Alertas</h4>
                            <span class="px-2 py-0.5 rounded-lg bg-amber-500/20 text-amber-400 text-[10px] font-bold">{{ lowStockKeys.length }}</span>
                        </div>
                        <div class="space-y-2 max-h-[250px] overflow-y-auto pr-2 custom-scrollbar">
                            <div v-for="(keys, providerName) in groupedLowStockKeys" :key="providerName" class="space-y-1.5">
                                <p class="text-[9px] font-bold text-slate-500 uppercase tracking-widest">{{ providerName }}</p>
                                <div class="space-y-1">
                                    <div v-for="k in keys" :key="k.id" class="flex justify-between items-center p-2 rounded-lg bg-white/5 text-xs">
                                        <span class="font-bold">{{ k.cod_llave }}</span>
                                        <span class="px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-400 font-bold">{{ k.cantidad }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- User Profile Mini -->
            <div class="flex items-center space-x-1 px-2 border-l border-white/10 ml-1">
                <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-indigo-700 p-[1px] shadow-lg shadow-indigo-500/20">
                    <div class="w-full h-full rounded-md bg-slate-900 flex items-center justify-center font-bold text-[10px] text-white">
                        {{ userInitials }}
                    </div>
                </div>
            </div>
            
            <!-- Hamburger Menu -->
            <button @click="toggleSidebar" class="p-2 glass-pill rounded-lg text-gray-400 hover:text-white transition-all">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path v-if="!isSidebarOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                    <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
        </div>
    </div>

    <!-- Sidebar Overlay -->
    <Transition name="fade">
        <div v-if="isSidebarOpen" class="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-40" @click="isSidebarOpen = false"></div>
    </Transition>

    <!-- Sidebar -->
    <aside 
        :class="[
            'fixed lg:relative z-50 w-72 h-[calc(100vh-2rem)] m-4 glass-card rounded-3xl flex flex-col transition-all duration-500 ease-spring lg:translate-x-0 no-print',
            isSidebarOpen ? 'translate-x-0' : '-translate-x-[calc(100%+2rem)]'
        ]"
    >
      <div class="hidden lg:flex p-8 items-center justify-center">
        <h1 class="text-2xl font-black tracking-tighter bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent">
            KEY<span class="text-white">MASTER</span>
        </h1>
      </div>

      <nav class="flex-1 px-4 py-2 space-y-1.5 overflow-y-auto custom-scrollbar">
        <div class="px-4 mb-4">
            <p class="text-[10px] font-bold text-slate-500 uppercase tracking-[0.2em]">Gestión</p>
        </div>

        <button 
          v-for="item in [
            { id: 'proveedores', label: 'Proveedores', icon: 'M17 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0z' },
            { id: 'llaves', label: 'Inventario', icon: 'M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z' },
            { id: 'informacion', label: 'Analíticas', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' }
          ]"
          :key="item.id"
          @click="currentTab = item.id; isSidebarOpen = false"
          :class="[
            'w-full flex items-center px-4 py-3.5 rounded-2xl transition-all duration-300 group',
            currentTab === item.id 
              ? 'bg-gradient-to-r from-violet-600/20 to-cyan-600/20 text-white border border-white/10 shadow-[0_0_20px_rgba(139,92,246,0.15)]' 
              : 'text-slate-400 hover:bg-white/5 hover:text-white'
          ]"
        >
          <div :class="[
            'p-2 rounded-xl mr-3 transition-colors',
            currentTab === item.id ? 'bg-violet-500 text-white' : 'bg-slate-800 text-slate-400 group-hover:bg-slate-700'
          ]">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon" />
            </svg>
          </div>
          <span class="font-semibold text-sm">{{ item.label }}</span>
        </button>

        <div class="px-4 py-4 mt-4">
            <p class="text-[10px] font-bold text-slate-500 uppercase tracking-[0.2em]">Operaciones</p>
        </div>

        <button 
          @click="currentTab = 'checkout'; isSidebarOpen = false"
          :class="[
            'w-full flex items-center px-4 py-3.5 rounded-2xl transition-all duration-300 relative group',
            currentTab === 'checkout' 
              ? 'bg-gradient-to-r from-violet-600/20 to-cyan-600/20 text-white border border-white/10 shadow-[0_0_20px_rgba(139,92,246,0.15)]' 
              : 'text-slate-400 hover:bg-white/5 hover:text-white'
          ]"
        >
          <div :class="[
            'p-2 rounded-xl mr-3 transition-colors',
            currentTab === 'checkout' ? 'bg-cyan-500 text-white' : 'bg-slate-800 text-slate-400 group-hover:bg-slate-700'
          ]">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <span class="font-semibold text-sm">Lista de Salida</span>
          <span v-if="checkoutCount > 0" class="absolute right-4 bg-gradient-to-br from-pink-500 to-rose-600 text-white text-[10px] font-black px-2 py-0.5 rounded-lg shadow-lg">
            {{ checkoutCount }}
          </span>
        </button>

        <button 
          @click="currentTab = 'historial'; isSidebarOpen = false"
          :class="[
            'w-full flex items-center px-4 py-3.5 rounded-2xl transition-all duration-300 group',
            currentTab === 'historial' 
              ? 'bg-gradient-to-r from-violet-600/20 to-cyan-600/20 text-white border border-white/10' 
              : 'text-slate-400 hover:bg-white/5 hover:text-white'
          ]"
        >
          <div :class="[
            'p-2 rounded-xl mr-3 transition-colors',
            currentTab === 'historial' ? 'bg-slate-700 text-white' : 'bg-slate-800 text-slate-400 group-hover:bg-slate-700'
          ]">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <span class="font-semibold text-sm">Historial</span>
        </button>

        <button 
          @click="currentTab = 'compras_historial'; isSidebarOpen = false"
          :class="[
            'w-full flex items-center px-4 py-3.5 rounded-2xl transition-all duration-300 group',
            currentTab === 'compras_historial' 
              ? 'bg-gradient-to-r from-emerald-600/20 to-teal-600/20 text-white border border-white/10' 
              : 'text-slate-400 hover:bg-white/5 hover:text-white'
          ]"
        >
          <div :class="[
            'p-2 rounded-xl mr-3 transition-colors',
            currentTab === 'compras_historial' ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-slate-400 group-hover:bg-slate-700'
          ]">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 0 -2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
          </div>
          <span class="font-semibold text-sm">Historial de Compras</span>
        </button>

        <button 
          @click="currentTab = 'ai'; isSidebarOpen = false"
          :class="[
            'w-full flex items-center px-4 py-3.5 rounded-2xl transition-all duration-300 group overflow-hidden',
            currentTab === 'ai' 
              ? 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-xl scale-[1.02]' 
              : 'text-slate-400 hover:bg-indigo-600/10 hover:text-indigo-300'
          ]"
        >
          <div :class="[
            'p-2 rounded-xl mr-3 transition-colors',
            currentTab === 'ai' ? 'bg-white/20 text-white' : 'bg-indigo-900/40 text-indigo-400 group-hover:bg-indigo-900/60'
          ]">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
          </div>
          <span class="font-bold text-sm tracking-tight">INTELIGENCIA AI</span>
        </button>

        <button 
          @click="currentTab = 'comparacion'; isSidebarOpen = false"
          :class="[
            'w-full flex items-center px-4 py-3.5 rounded-2xl transition-all duration-300 group overflow-hidden',
            currentTab === 'comparacion' 
              ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-xl scale-[1.02]' 
              : 'text-slate-400 hover:bg-cyan-600/10 hover:text-cyan-300'
          ]"
        >
          <div :class="[
            'p-2 rounded-xl mr-3 transition-colors',
            currentTab === 'comparacion' ? 'bg-white/20 text-white' : 'bg-cyan-900/40 text-cyan-400 group-hover:bg-cyan-900/60'
          ]">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <span class="font-bold text-sm tracking-tight">Busqueda Inteligente</span>
        </button>
      </nav>
      
      <div class="p-6 border-t border-white/5">
        <button 
          @click="logout"
          class="w-full h-12 glass-pill rounded-2xl flex items-center justify-center text-rose-400 hover:bg-rose-500/10 hover:text-rose-300 transition-all font-bold text-sm"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          Salir
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 overflow-y-auto pt-28 lg:pt-8 px-4 lg:px-12 pb-12 w-full custom-scrollbar relative">
      <div class="max-w-[1400px] mx-auto">
        <header class="mb-12 flex flex-col md:flex-row justify-between items-start md:items-center gap-6 no-print">
            <div class="space-y-1">
                <nav class="flex text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">
                    <span class="hover:text-violet-400 transition-colors cursor-pointer">Panel</span>
                    <span class="mx-2 opacity-30">/</span>
                    <span class="text-violet-400">{{ getTitle() }}</span>
                </nav>
                <h2 class="text-4xl lg:text-5xl font-black text-white tracking-tighter">
                    {{ getTitle() }}
                </h2>
                <p class="text-slate-400 font-medium text-lg">{{ getDescription() }}</p>
            </div>

            <!-- Header Actions (Desktop Only) -->
            <div class="hidden lg:flex items-center space-x-4 glass-card p-2 rounded-[2rem] relative z-[60]">
                

                <!-- Settings Button -->
                <button @click="showSettings = true" class="w-12 h-12 flex items-center justify-center rounded-2xl bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white transition-all">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                </button>

                <!-- Notifications/Alerts -->
                <div class="relative group" v-if="lowStockKeys.length > 0">
                    <button class="w-12 h-12 flex items-center justify-center rounded-2xl bg-amber-500/10 text-amber-500 hover:bg-amber-500/20 transition-all">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 animate-bounce" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                        </svg>
                    </button>
                    <!-- Enhanced Dropdown -->
                    <div class="absolute right-0 top-full pt-4 w-96 hidden group-hover:block z-[100] animate-in fade-in slide-in-from-top-4">
                        <div class="bg-slate-800 border border-slate-700 rounded-3xl p-6 shadow-2xl">
                            <div class="flex justify-between items-center mb-6">
                                <h4 class="text-sm font-black uppercase tracking-widest text-amber-500">Alertas Críticas</h4>
                                <span class="px-2 py-0.5 rounded-lg bg-amber-500/20 text-amber-400 text-xs font-bold">{{ lowStockKeys.length }}</span>
                            </div>
                            <div class="space-y-6 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                                <div v-for="(keys, providerName) in groupedLowStockKeys" :key="providerName" class="space-y-3">
                                    <p class="text-[10px] font-black text-slate-500 uppercase tracking-widest border-b border-white/5 pb-2">{{ providerName }}</p>
                                    <div class="grid gap-2">
                                        <div v-for="k in keys" :key="k.id" class="flex justify-between items-center p-3 rounded-2xl bg-white/5 hover:bg-white/10 transition-all border border-white/5">
                                            <div class="flex items-center">
                                                <div class="w-8 h-8 rounded-lg bg-violet-600/20 flex items-center justify-center mr-3">
                                                    <span class="text-[10px] uppercase font-bold text-violet-400">KK</span>
                                                </div>
                                                <span class="font-bold text-sm">{{ k.cod_llave }}</span>
                                            </div>
                                            <span class="text-xs font-black px-2 py-1 rounded-lg bg-rose-500/20 text-rose-400 border border-rose-500/20">{{ k.cantidad }}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- User Profile -->
                <div class="flex items-center space-x-3 pr-2 pl-4 border-l border-white/10">
                    <div class="text-right hidden sm:block">
                        <p class="text-sm font-black text-white tracking-tight">{{ userName }}</p>
                        <p class="text-[10px] text-slate-500 font-bold uppercase tracking-wider">{{ isSuperAdmin ? 'Admin' : 'Personal' }}</p>
                    </div>
                    <div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-600 to-indigo-700 p-[2px] shadow-lg shadow-indigo-500/20">
                        <div class="w-full h-full rounded-[0.9rem] bg-slate-900 flex items-center justify-center font-black text-xs text-white">
                            {{ userInitials }}
                        </div>
                    </div>
                </div>
            </div>
        </header>

        <Transition name="view" mode="out-in">
            <ProveedorList 
                v-if="currentTab === 'proveedores'" 
                :is-admin="isSuperAdmin" 
                :preferred-provider="userProfile.preferred_provider"
                :highlight-color="userProfile.active_provider_color"
                :min-stock-alert="userProfile.min_stock_alert"
                @navigate-to-shopping="currentTab = 'shopping'" 
                @update-profile="updateProfile"
            />
            <LlaveList v-else-if="currentTab === 'llaves'" :is-admin="isSuperAdmin" :preferred-provider="userProfile.preferred_provider" />
            <DashboardCharts v-else-if="currentTab === 'informacion'" :currentUserId="userId" />
            <AIChat v-else-if="currentTab === 'ai'" />
            <ImageComparison v-else-if="currentTab === 'comparacion'" />
            <CheckoutList v-else-if="currentTab === 'checkout'" />
            <ShoppingList v-else-if="currentTab === 'shopping'" :preferred-provider="userProfile.preferred_provider" :min-stock-alert="userProfile.min_stock_alert" />
            <HistoryList v-else-if="currentTab === 'historial'" />
            <PurchaseHistory v-else-if="currentTab === 'compras_historial'" />
        </Transition>
      </div>
    </main>
  </div>
</template>

<style>
@media print {
    .no-print {
        display: none !important;
    }
    
    /* Force background white and text black for everything else in print */
    html, body {
        background-color: white !important;
        color: black !important;
    }
}
</style>


