<script setup lang="ts">
import { ref, onMounted } from 'vue';
import proveedorService, { type Proveedor } from '../services/proveedorService';
import llaveService from '../services/llaveService';
import { shoppingStore } from '../services/shoppingStore';
import { useToast } from '../composables/useToast';

const toast = useToast();

const props = defineProps<{ 
  isAdmin: boolean;
  preferredProvider?: number | null;
  minStockAlert?: number;
  highlightColor?: string;
}>();
const emit = defineEmits(['navigate-to-shopping', 'update-profile']);

const getHighlightClass = (provId?: number) => {
    // Use loose equality to handle possible string/number mismatch from API
    if (!provId || provId != props.preferredProvider) return 'border-white/5 bg-slate-900/40';
    
    const color = props.highlightColor || 'indigo';
    const colorMap: Record<string, string> = {
        indigo: '!bg-indigo-600/20 !border-indigo-500/50 shadow-[0_0_40px_rgba(99,102,241,0.3)]',
        red: '!bg-red-600/20 !border-red-500/50 shadow-[0_0_40px_rgba(239,68,68,0.3)]',
        green: '!bg-green-600/20 !border-green-500/50 shadow-[0_0_40px_rgba(34,197,94,0.3)]',
        blue: '!bg-blue-600/20 !border-blue-500/50 shadow-[0_0_40px_rgba(59,130,246,0.3)]',
        purple: '!bg-purple-600/20 !border-purple-500/50 shadow-[0_0_40px_rgba(168,85,247,0.3)]',
        pink: '!bg-pink-600/20 !border-pink-500/50 shadow-[0_0_40px_rgba(236,72,153,0.3)]'
    };
    return colorMap[color] || '!bg-indigo-600/20 !border-indigo-500/50';
};

const proveedores = ref<Proveedor[]>([]);
const form = ref<Proveedor>({
  nombre: '',
  direccion: '',
  telefono: '',
  correo: ''
});

const loadProveedores = async () => {
    try {
        const response = await proveedorService.getProveedores();
        proveedores.value = response.data;
    } catch (error) {
        console.error("Error al cargar proveedores", error);
    }
};

const submitForm = async () => {
    try {
        await proveedorService.createProveedor(form.value);
        form.value = { nombre: '', direccion: '', telefono: '', correo: '' };
        await loadProveedores();
    } catch (error) {
        console.error("Error al crear proveedor", error);
    }
};

onMounted(() => {
    loadProveedores();
});

// Modal state for setting preferred provider
const showPreferredModal = ref(false);
const selectedProviderForModal = ref<Proveedor | null>(null);

const handleSetPreferred = (proveedor: Proveedor) => {
    selectedProviderForModal.value = proveedor;
    showPreferredModal.value = true;
};

const confirmSetPreferred = () => {
    if (selectedProviderForModal.value?.id) {
        emit('update-profile', { preferred_provider: selectedProviderForModal.value.id });
        toast.success(`${selectedProviderForModal.value.nombre} establecido como proveedor predeterminado`);
    }
    showPreferredModal.value = false;
    selectedProviderForModal.value = null;
};

const cancelSetPreferred = () => {
    showPreferredModal.value = false;
    selectedProviderForModal.value = null;
};

const generateOrderForProvider = async (proveedor: Proveedor) => {
    try {
        if (!proveedor.id) return;
        const { data } = await llaveService.getLlaves();
        // Filter keys for this provider
        const providerKeys = data.filter((k: any) => k.proveedor === proveedor.id);
        
        const threshold = props.minStockAlert || 300;
        
        // Warning if provider is not the preferred one
        if (props.preferredProvider && proveedor.id !== props.preferredProvider) {
            handleSetPreferred(proveedor);
            return;
        }

        let count = 0;
        providerKeys.forEach((k: any) => {
             // Logic: Add if low stock based on personalized threshold
             shoppingStore.addItem({
                ...k, 
                proveedor_nombre: proveedor.nombre
             }, 0, threshold);
             
             if (k.cantidad < threshold) count++;
        });

        if (count > 0) {
            toast.success(`Orden generada para ${proveedor.nombre} con ${count} items.`);
        } else {
            toast.info(`El stock de ${proveedor.nombre} está completo.`);
        }
        
        emit('navigate-to-shopping');
    } catch (e) {
        console.error(e);
        toast.error('Error generando orden');
    }
};
</script>


<template>
  <div class="space-y-12 animate-in fade-in transition-all duration-700">
    <!-- Form Card -->
    <div v-if="isAdmin" class="glass-card rounded-[2.5rem] p-8 lg:p-10 relative overflow-hidden group">
        <!-- Decoration -->
        <div class="absolute top-0 right-0 w-32 h-32 bg-indigo-600/10 rounded-full blur-3xl group-hover:bg-indigo-600/20 transition-all duration-700"></div>
        
        <div class="relative">
            <h3 class="text-2xl font-black text-white mb-8 flex items-center tracking-tight">
                <div class="p-3 bg-indigo-600/20 rounded-2xl mr-4 border border-indigo-500/20">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-indigo-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
                    </svg>
                </div>
                Alta de Nuevo Proveedor
            </h3>

            <form @submit.prevent="submitForm" class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div class="col-span-1 md:col-span-2 space-y-2">
                    <label class="block text-xs font-black text-slate-500 uppercase tracking-widest ml-1">Razón Social / Nombre</label>
                    <input 
                        v-model="form.nombre" 
                        required 
                        placeholder="Ej. Suministros Industriales S.A." 
                        class="w-full bg-slate-900/50 border border-white/5 rounded-2xl px-5 py-4 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all font-bold placeholder:text-slate-600"
                    />
                </div>
                <div class="col-span-1 md:col-span-2 space-y-2">
                    <label class="block text-xs font-black text-slate-500 uppercase tracking-widest ml-1">Dirección de Operaciones</label>
                    <input 
                        v-model="form.direccion" 
                        required 
                        placeholder="Ej. Av. Central 456, Parque Industrial" 
                        class="w-full bg-slate-900/50 border border-white/5 rounded-2xl px-5 py-4 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all font-bold placeholder:text-slate-600"
                    />
                </div>
                <div class="space-y-2">
                    <label class="block text-xs font-black text-slate-500 uppercase tracking-widest ml-1">Contacto Telefónico</label>
                    <input 
                        v-model="form.telefono" 
                        required 
                        placeholder="+51 987 654 321" 
                        class="w-full bg-slate-900/50 border border-white/5 rounded-2xl px-5 py-4 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all font-bold placeholder:text-slate-600"
                    />
                </div>
                <div class="space-y-2">
                    <label class="block text-xs font-black text-slate-500 uppercase tracking-widest ml-1">Correo Corporativo</label>
                    <input 
                        v-model="form.correo" 
                        type="email" 
                        required 
                        placeholder="ventas@proveedor.com" 
                        class="w-full bg-slate-900/50 border border-white/5 rounded-2xl px-5 py-4 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all font-bold placeholder:text-slate-600"
                    />
                </div>
                <div class="col-span-1 md:col-span-2 pt-4">
                    <button type="submit" class="w-full md:w-auto px-10 py-4 bg-gradient-to-r from-indigo-600 to-violet-600 rounded-2xl font-black text-sm uppercase tracking-widest text-white shadow-xl hover:scale-[1.02] hover:shadow-indigo-600/20 active:scale-[0.98] transition-all duration-300">
                        Registrar Proveedor
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- Provider Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
        <div v-for="prov in proveedores" :key="prov.id" 
            :class="[
                'glass-card rounded-[2.5rem] p-8 flex flex-col group transition-all duration-500 hover:translate-y-[-4px] border',
                getHighlightClass(prov.id),
                prov.id == props.preferredProvider ? 'ring-2' : 'hover:ring-2 hover:ring-white/10'
            ]"
        >
            <div class="flex items-start justify-between mb-8">
                <div class="h-16 w-16 rounded-[1.5rem] bg-gradient-to-br from-indigo-500/20 to-violet-500/20 flex items-center justify-center text-xl font-black text-indigo-400 border border-indigo-500/20 border-white/5 shadow-lg group-hover:scale-110 transition-transform">
                    {{ prov.nombre.substring(0,2).toUpperCase() }}
                </div>
                <div class="flex space-x-2">
                    <button @click="generateOrderForProvider(prov)" class="h-12 px-6 rounded-2xl bg-white/5 hover:bg-indigo-600 text-[10px] font-black uppercase tracking-widest text-slate-300 hover:text-white transition-all border border-white/5">
                        Pedido Automático
                    </button>
                </div>
            </div>

            <h4 class="text-2xl font-black text-white mb-6 tracking-tight group-hover:text-indigo-400 transition-colors">{{ prov.nombre }}</h4>
            
            <div class="space-y-4 mb-8 flex-1">
                <div class="flex items-center text-slate-400 group-hover:text-slate-300 transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    <span class="text-sm font-bold">{{ prov.direccion }}</span>
                </div>
                <div class="flex items-center text-slate-400 group-hover:text-slate-300 transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                    </svg>
                    <span class="text-sm font-bold">{{ prov.telefono }}</span>
                </div>
                <div class="flex items-center text-slate-400 group-hover:text-slate-300 transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    <span class="text-sm font-bold truncate">{{ prov.correo }}</span>
                </div>
            </div>

            <div class="pt-6 border-t border-white/5 flex justify-between items-center">
                <span class="text-[10px] font-black text-slate-600 uppercase tracking-widest">ID: {{ prov.id }}</span>
                <button class="text-slate-500 hover:text-indigo-400 transition-colors p-2 rounded-xl hover:bg-white/5">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                    </svg>
                </button>
            </div>
        </div>
    </div>

    <!-- Empty State -->
    <div v-if="proveedores.length === 0" class="glass-card rounded-[2.5rem] p-20 text-center flex flex-col items-center justify-center">
        <div class="w-24 h-24 rounded-3xl bg-slate-900 border border-white/5 flex items-center justify-center mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-slate-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
        </div>
        <h3 class="text-2xl font-black text-white mb-2">Directorio Vacío</h3>
        <p class="text-slate-500 font-bold">No se han registrado proveedores en el sistema.</p>
    </div>

    <!-- Set Preferred Provider Modal -->
    <Transition name="fade">
        <div v-if="showPreferredModal && selectedProviderForModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-950/90 backdrop-blur-md">
            <div class="glass-card rounded-3xl p-10 w-full max-w-2xl border border-white/10 shadow-2xl animate-in slide-in-from-bottom-4 duration-300">
                <!-- Header -->
                <div class="flex items-center justify-between mb-8">
                    <div class="flex items-center space-x-4">
                        <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-600/30 to-violet-600/30 border border-indigo-500/50 flex items-center justify-center">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                            </svg>
                        </div>
                        <div>
                            <p class="text-xs font-black text-slate-400 uppercase tracking-widest">Proveedor Predeterminado</p>
                            <p class="text-2xl font-black text-white">{{ selectedProviderForModal.nombre }}</p>
                        </div>
                    </div>
                    <button @click="cancelSetPreferred" class="w-10 h-10 rounded-xl hover:bg-white/10 flex items-center justify-center transition-all">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-slate-400 hover:text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                <!-- Content -->
                <div class="space-y-6 mb-8">
                    <p class="text-base text-slate-300 leading-relaxed">
                        ¿Deseas establecer a <span class="font-black text-indigo-400">{{ selectedProviderForModal.nombre }}</span> como tu proveedor predeterminado?
                    </p>
                    
                    <!-- Provider Details -->
                    <div class="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-4">
                        <div class="flex items-start space-x-3">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-slate-500 mt-1 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                            </svg>
                            <div>
                                <p class="text-xs font-black text-slate-500 uppercase tracking-widest">Ubicación</p>
                                <p class="text-sm font-bold text-slate-300">{{ selectedProviderForModal.direccion }}</p>
                            </div>
                        </div>
                        <div class="flex items-start space-x-3">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-slate-500 mt-1 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                            </svg>
                            <div>
                                <p class="text-xs font-black text-slate-500 uppercase tracking-widest">Teléfono</p>
                                <p class="text-sm font-bold text-slate-300">{{ selectedProviderForModal.telefono }}</p>
                            </div>
                        </div>
                        <div class="flex items-start space-x-3">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-slate-500 mt-1 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                            </svg>
                            <div>
                                <p class="text-xs font-black text-slate-500 uppercase tracking-widest">Correo</p>
                                <p class="text-sm font-bold text-slate-300 truncate">{{ selectedProviderForModal.correo }}</p>
                            </div>
                        </div>
                    </div>

                    <p class="text-xs text-slate-500 italic">Esta acción cambiará tu proveedor predeterminado para generar órdenes automáticas.</p>
                </div>

                <!-- Actions -->
                <div class="flex flex-col sm:flex-row gap-4 border-t border-white/5 pt-8">
                    <button @click="cancelSetPreferred" class="h-12 px-6 rounded-2xl text-sm font-black uppercase tracking-widest text-slate-400 hover:text-white hover:bg-white/10 transition-all active:scale-95 flex-1">
                        Mantener Actual
                    </button>
                    <button 
                        @click="confirmSetPreferred" 
                        class="h-12 px-8 bg-gradient-to-r from-indigo-600 to-violet-600 rounded-2xl font-black text-sm uppercase tracking-widest text-white shadow-lg hover:shadow-indigo-600/30 hover:scale-[1.02] active:scale-95 transition-all flex items-center justify-center flex-1"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                        </svg>
                        Establecer como Predeterminado
                    </button>
                </div>
            </div>
        </div>
    </Transition>
  </div>
</template>
