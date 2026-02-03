<script setup lang="ts">
import { ref, watch } from 'vue';

const props = defineProps<{
    modelValue: boolean;
    currentAlert: number;
    currentColor: string;
    currentProvider: number | string | null;
    currentHighlightColor: string;
    providers: any[];
}>();

const emit = defineEmits(['update:modelValue', 'save']);

const form = ref({
    min_stock_alert: props.currentAlert,
    theme_color: props.currentColor,
    active_provider_color: props.currentHighlightColor,
    preferred_provider: props.currentProvider
});

watch(() => props.modelValue, (isOpen) => {
    if (isOpen) {
        form.value = {
            min_stock_alert: props.currentAlert,
            theme_color: props.currentColor,
            active_provider_color: props.currentHighlightColor,
            preferred_provider: props.currentProvider
        };
    }
});

const colors = [
    { name: 'Indigo', value: 'indigo', class: 'bg-indigo-600' },
    { name: 'Rojo', value: 'red', class: 'bg-red-600' },
    { name: 'Verde', value: 'green', class: 'bg-green-600' },
    { name: 'Azul', value: 'blue', class: 'bg-blue-600' },
    { name: 'Morado', value: 'purple', class: 'bg-purple-600' },
    { name: 'Rosa', value: 'pink', class: 'bg-pink-600' },
];

const close = () => {
    emit('update:modelValue', false);
};

const save = () => {
    emit('save', { ...form.value });
    close();
};
</script>

<template>
     <Transition name="fade">
         <div v-if="modelValue" class="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-slate-950/90 backdrop-blur-md">
            <!-- Backdrop Overlay (redundant but for click-to-close) -->
            <div class="absolute inset-0" @click="close"></div>

            <div class="glass-card rounded-[2.5rem] p-10 w-full max-w-xl border border-white/10 shadow-[0_30px_60px_-15px_rgba(0,0,0,0.5)] animate-in zoom-in-95 duration-300 relative">
                <div class="flex items-center mb-10">
                    <div class="p-3 bg-indigo-600/20 rounded-2xl mr-4 border border-indigo-500/20">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                    </div>
                    <div>
                        <h3 class="text-3xl font-black text-white tracking-tight leading-none mb-1">Preferencia</h3>
                        <p class="text-[10px] font-black text-slate-500 uppercase tracking-widest">Personalización del Espacio</p>
                    </div>
                </div>

                <div class="space-y-8">
                    <div class="space-y-4">
                        <div class="flex justify-between items-center ml-1">
                            <label class="block text-xs font-black text-slate-500 uppercase tracking-widest flex items-center">
                                <div class="w-1 h-3 bg-indigo-500 rounded-full mr-2"></div>
                                Alerta de Stock Mínimo
                            </label>
                            <span class="text-[10px] font-black text-indigo-400 bg-indigo-400/10 px-2 py-0.5 rounded-lg border border-indigo-400/10">CRÍTICO</span>
                        </div>
                        <input 
                            type="number" 
                            v-model="form.min_stock_alert"
                            class="w-full h-16 bg-slate-900 border border-white/5 rounded-2xl px-6 py-2 text-white font-black focus:outline-none focus:ring-2 focus:ring-indigo-500/50 glass-pill shadow-inner"
                        />
                    </div>

                    <div class="space-y-4">
                        <label class="block text-xs font-black text-slate-500 uppercase tracking-widest ml-1 flex items-center">
                            <div class="w-1 h-3 bg-cyan-500 rounded-full mr-2"></div>
                            Proveedor Predeterminado
                        </label>
                        <select 
                            v-model="form.preferred_provider"
                            class="w-full h-16 bg-slate-900 border border-white/5 rounded-2xl px-6 py-2 text-white font-black focus:outline-none focus:ring-2 focus:ring-cyan-500/50 appearance-none glass-pill"
                        >
                            <option :value="null">Todos los Proveedores</option>
                            <option v-for="p in providers" :key="p.id" :value="p.id">{{ p.nombre }}</option>
                        </select>
                    </div>

                    <div class="space-y-4">
                        <label class="block text-xs font-black text-slate-500 uppercase tracking-widest ml-1 flex items-center">
                            <div class="w-1 h-3 bg-violet-500 rounded-full mr-2"></div>
                            Identidad Visual
                        </label>
                        <div class="grid grid-cols-6 gap-4 p-4 bg-slate-900/50 rounded-[2rem] border border-white/5">
                            <button 
                                v-for="color in colors" 
                                :key="color.value"
                                @click="form.theme_color = color.value"
                                :class="[
                                    color.class,
                                    'h-10 w-10 rounded-2xl focus:outline-none ring-2 ring-offset-4 ring-offset-slate-950 transition-all hover:scale-110 shadow-lg',
                                    form.theme_color === color.value ? 'ring-white scale-110' : 'ring-transparent'
                                ]"
                                :title="'Tema: ' + color.name"
                            ></button>
                        </div>
                    </div>

                    <div class="space-y-4">
                        <label class="block text-xs font-black text-slate-500 uppercase tracking-widest ml-1 flex items-center">
                            <div class="w-1 h-3 bg-amber-500 rounded-full mr-2"></div>
                            Color de Realce (Proveedor Activo)
                        </label>
                        <div class="grid grid-cols-6 gap-4 p-4 bg-slate-900/50 rounded-[2rem] border border-white/5">
                            <button 
                                v-for="color in colors" 
                                :key="'highlight-' + color.value"
                                @click="form.active_provider_color = color.value"
                                :class="[
                                    color.class,
                                    'h-10 w-10 rounded-2xl focus:outline-none ring-2 ring-offset-4 ring-offset-slate-950 transition-all hover:scale-110 shadow-lg',
                                    form.active_provider_color === color.value ? 'ring-white scale-110' : 'ring-transparent'
                                ]"
                                :title="'Realce: ' + color.name"
                            ></button>
                        </div>
                    </div>
                </div>

                <div class="mt-12 flex flex-col sm:flex-row justify-end gap-4 border-t border-white/5 pt-10">
                    <button type="button" @click="close" class="px-8 py-4 rounded-2xl text-xs font-black uppercase tracking-widest text-slate-500 hover:text-white transition-all active:scale-95">
                        Ignorar
                    </button>
                    <button type="button" @click="save" class="px-10 py-4 bg-indigo-600 hover:bg-indigo-500 rounded-2xl font-black text-xs uppercase tracking-widest text-white shadow-xl hover:scale-[1.02] active:scale-[0.98] transition-all">
                        Aplicar Cambios
                    </button>
                </div>
            </div>
        </div>
     </Transition>
</template>
