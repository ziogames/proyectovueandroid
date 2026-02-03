<script setup lang="ts">
import { ref, onMounted } from 'vue';
import llaveService, { type Llave } from '../services/llaveService';
import proveedorService, { type Proveedor } from '../services/proveedorService';
import { checkoutStore } from '../services/checkoutStore';
import { useToast } from '../composables/useToast';

const props = defineProps<{ 
    isAdmin: boolean;
    preferredProvider?: number | string | null;
}>();
const toast = useToast();
const llaves = ref<Llave[]>([]);
const proveedores = ref<Proveedor[]>([]);
const form = ref({
    cod_llave: '',
    cantidad: 0,
    proveedor: props.preferredProvider || '' as string | number,
    img: null as File | null
});

import { watch } from 'vue';
watch(() => props.preferredProvider, (newVal) => {
    form.value.proveedor = newVal || '';
    loadData();
});

const loadData = async () => {
    try {
        const [llavesRes, provRes] = await Promise.all([
            llaveService.getLlaves(props.preferredProvider),
            proveedorService.getProveedores()
        ]);
        llaves.value = llavesRes.data;
        proveedores.value = provRes.data;
    } catch (error) {
        console.error("Error cargando datos", error);
    }
};

const handleFileUpload = (event: Event) => {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files[0]) {
        form.value.img = target.files[0];
    }
};

const submitForm = async () => {
    try {
        const formData = new FormData();
        formData.append('cod_llave', form.value.cod_llave);
        formData.append('cantidad', form.value.cantidad.toString());
        formData.append('proveedor', form.value.proveedor.toString());
        if (form.value.img) {
            formData.append('img', form.value.img);
        }

        await llaveService.createLlave(formData);
        
        toast.success(`Llave ${form.value.cod_llave} creada exitosamente`);
        
        // Reset
        form.value = { cod_llave: '', cantidad: 0, proveedor: props.preferredProvider || '', img: null };
        const fileInput = document.getElementById('file-upload') as HTMLInputElement;
        if(fileInput) fileInput.value = '';
        
        await loadData();
    } catch (error: any) {
        console.error("Error creando llave", error);
        
        // Manejar error de código duplicado
        if (error.response?.status === 400 && error.response?.data?.cod_llave) {
            const errorMessage = error.response.data.cod_llave[0];
            toast.error(errorMessage);
        } else if (error.response?.data?.detail) {
            toast.error(error.response.data.detail);
        } else {
            toast.error('Error al crear la llave. Por favor intenta nuevamente.');
        }
    }
};

const getProveedorName = (id: number) => {
    const prov = proveedores.value.find(p => p.id === id);
    return prov ? prov.nombre : 'Desconocido';
};

const addToCheckout = (llave: Llave) => {
    checkoutStore.addItem(llave);
    toast.success(`Llave ${llave.cod_llave} añadida a lista de salida`);
};

onMounted(() => {
    loadData();
});
</script>


<template>
  <div class="space-y-12">
    <!-- Form Card -->
    <div v-if="isAdmin" class="glass-card card-animate rounded-[2.5rem] p-8 lg:p-10 relative overflow-hidden group">
        <!-- Decoration -->
        <div class="absolute top-0 right-0 w-32 h-32 bg-violet-600/10 rounded-full blur-3xl group-hover:bg-violet-600/20 transition-all duration-700"></div>
        
        <div class="relative">
            <h3 class="text-2xl font-black text-white mb-8 flex items-center tracking-tight">
                <div class="p-3 bg-violet-600/20 rounded-2xl mr-4 border border-violet-500/20">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-violet-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z" clip-rule="evenodd" />
                    </svg>
                </div>
                Nueva Entrada de Inventario
            </h3>

            <form @submit.prevent="submitForm" class="grid grid-cols-1 md:grid-cols-4 gap-8 items-end">
                <div class="md:col-span-1 space-y-2">
                    <label class="block text-xs font-black text-slate-500 uppercase tracking-widest ml-1">Referencia / Código</label>
                    <input v-model="form.cod_llave" required class="w-full bg-slate-900/50 border border-white/5 rounded-2xl px-5 py-4 text-white focus:outline-none focus:ring-2 focus:ring-violet-500/50 transition-all placeholder:text-slate-600 font-bold" placeholder="EJ: KEY-X-101" />
                </div>
                
                <div class="md:col-span-1 space-y-2">
                    <label class="block text-xs font-black text-slate-500 uppercase tracking-widest ml-1">Unidades Initiales</label>
                    <input v-model.number="form.cantidad" type="number" required class="w-full bg-slate-900/50 border border-white/5 rounded-2xl px-5 py-4 text-white focus:outline-none focus:ring-2 focus:ring-violet-500/50 transition-all font-bold" />
                </div>

                <div class="md:col-span-1 space-y-2">
                    <label class="block text-xs font-black text-slate-500 uppercase tracking-widest ml-1">Proveedor Asignado</label>
                    <div class="w-full bg-slate-900/30 border border-white/5 rounded-2xl px-5 py-4 text-slate-400 flex items-center font-bold">
                        <span v-if="preferredProvider" class="text-white">
                            {{ getProveedorName(Number(preferredProvider)) }}
                        </span>
                        <span v-else class="text-xs text-amber-500/70 italic">
                            Requiere config. previa
                        </span>
                    </div>
                </div>

                <div class="md:col-span-1 space-y-2">
                    <label class="block text-xs font-black text-slate-500 uppercase tracking-widest ml-1">Fotografía (Opcional)</label>
                    <div class="relative group/file">
                        <input id="file-upload" type="file" @change="handleFileUpload" accept="image/*" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"/>
                        <div class="w-full bg-slate-900/50 border border-dashed border-white/10 rounded-2xl px-5 py-3.5 text-center text-slate-400 group-hover/file:border-violet-500/30 transition-all flex items-center justify-center">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            <span class="text-sm font-bold truncate">{{ form.img ? form.img.name : 'Subir imagen...' }}</span>
                        </div>
                    </div>
                </div>

                <div class="md:col-span-4 pt-4">
                    <button 
                        type="submit" 
                        :disabled="!preferredProvider"
                        :class="[
                            'w-full md:w-auto px-10 py-4 rounded-2xl font-black text-sm uppercase tracking-widest shadow-xl transition-all duration-300 flex items-center justify-center',
                            !preferredProvider 
                                ? 'bg-slate-800 text-slate-500 cursor-not-allowed opacity-50' 
                                : 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white hover:scale-[1.02] hover:shadow-violet-600/20 active:scale-[0.98]'
                        ]"
                    >
                        Confirmar Registro de Llave
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- Inventory Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-8">
        <div v-for="llave in llaves" :key="llave.id" class="glass-card card-animate rounded-[2rem] overflow-hidden flex flex-col group hover:ring-2 hover:ring-violet-500/20 transition-all duration-500">
            <div class="relative h-56 bg-slate-950/50 overflow-hidden">
                <img v-if="llave.img" :src="llave.img" alt="Llave" class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" />
                <div v-else class="w-full h-full flex items-center justify-center bg-slate-900/80">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-slate-800" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                    </svg>
                </div>
                
                <!-- Stock Badge -->
                <div class="absolute top-4 right-4 flex items-center">
                    <div :class="[
                        'px-3 py-1.5 rounded-xl font-black text-xs backdrop-blur-md border shadow-lg',
                        llave.cantidad < 5 ? 'bg-rose-500/20 text-rose-400 border-rose-500/30' : 'bg-slate-900/60 text-white border-white/10'
                    ]">
                        {{ llave.cantidad }} UNIDADES
                    </div>
                </div>

                <!-- Hover Overlay -->
                <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
            </div>
            
            <div class="p-6 flex flex-col flex-1 relative">
                <div class="flex-1">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-[10px] font-black text-violet-400 uppercase tracking-widest">Master Key</span>
                        <div v-if="llave.cantidad < 5" class="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></div>
                    </div>
                    <h4 class="text-2xl font-black text-white mb-2 tracking-tight group-hover:text-violet-300 transition-colors">{{ llave.cod_llave }}</h4>
                    <p class="text-sm font-bold text-slate-500 flex items-center mb-1">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                        </svg>
                        {{ getProveedorName(llave.proveedor) }}
                    </p>
                    <p class="text-xs font-black text-emerald-400 mb-6 flex items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        S/ {{ Number(llave.precio_compra || 0.90).toFixed(2) }}
                    </p>
                </div>
                
                <button 
                    @click="addToCheckout(llave)" 
                    class="w-full glass-pill rounded-2xl h-14 font-black text-xs uppercase tracking-widest transition-all duration-300 flex items-center justify-center hover:bg-violet-600 hover:text-white hover:border-violet-500 group/btn"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2 text-violet-400 group-hover/btn:text-white transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M12 4v16m8-8H4" />
                    </svg>
                    Añadir a Salida
                </button>
            </div>
        </div>
    </div>

    <!-- Empty State -->
    <div v-if="llaves.length === 0" class="glass-card card-animate rounded-[2.5rem] p-20 text-center flex flex-col items-center justify-center">
        <div class="w-24 h-24 rounded-3xl bg-slate-900 border border-white/5 flex items-center justify-center mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-slate-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
        </div>
        <h3 class="text-2xl font-black text-white mb-2">Inventario Vacío</h3>
        <p class="text-slate-500 font-bold">No se encontraron llaves asociadas a este proveedor.</p>
    </div>
  </div>


</template>
