<script setup lang="ts">
import { ref } from 'vue';
import api from '../services/api';

interface Message {
    id: number;
    text: string;
    isUser: boolean;
    data?: any[]; // Tabla de resultados opcional
}

const messages = ref<Message[]>([
    { id: 1, text: '¡Hola! Soy tu asistente SQL. Pregúntame sobre tus llaves o proveedores.', isUser: false }
]);
const input = ref('');
const loading = ref(false);

const sendMessage = async () => {
    if (!input.value.trim()) return;

    // Agregar mensaje usuario
    const userMsg = { id: Date.now(), text: input.value, isUser: true };
    messages.value.push(userMsg);
    
    const question = input.value;
    input.value = '';
    loading.value = true;

    try {
        const response = await api.post('ai/ask/', { question });
        
        if (response.data.error) {
             messages.value.push({ 
                id: Date.now() + 1, 
                text: `Error: ${response.data.error}`, 
                isUser: false 
            });
        } else {
            // Mensaje del bot con resultados
            const resultText = `He encontrado ${response.data.count} resultados para tu consulta.`;
            messages.value.push({ 
                id: Date.now() + 1, 
                text: resultText, 
                isUser: false,
                data: response.data.results
            });
        }

    } catch (error) {
        messages.value.push({ 
            id: Date.now() + 1, 
            text: 'Hubo un error al conectar con el asistente.', 
            isUser: false 
        });
        console.error(error);
    } finally {
        loading.value = false;
        // Scroll to bottom (simple implementation)
        setTimeout(() => {
            const container = document.getElementById('chat-container');
            if(container) container.scrollTop = container.scrollHeight;
        }, 100);
    }
};
</script>

<template>
  <div class="flex flex-col h-full glass-card rounded-[2.5rem] overflow-hidden border border-white/5 shadow-2xl animate-in slide-in-from-right-8 duration-700">
    <!-- Header Chat -->
    <div class="p-6 md:p-8 bg-white/[0.02] border-b border-white/5 flex items-center justify-between">
        <div class="flex items-center">
            <div class="h-12 w-12 rounded-2xl bg-gradient-to-r from-violet-500 to-indigo-500 flex items-center justify-center mr-5 shadow-lg shadow-indigo-500/20">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" clip-rule="evenodd" />
                </svg>
            </div>
            <div>
                <h3 class="text-xl font-black text-white tracking-tight leading-none mb-1">Cortex AI</h3>
                <p class="text-[10px] font-black text-emerald-400 uppercase tracking-widest flex items-center">
                    <span class="w-1.5 h-1.5 bg-emerald-500 rounded-full mr-2 animate-pulse"></span>
                    Sincronizado
                </p>
            </div>
        </div>
        <div class="flex space-x-2">
             <div class="w-2 h-2 rounded-full bg-white/10"></div>
             <div class="w-2 h-2 rounded-full bg-white/10"></div>
             <div class="w-2 h-2 rounded-full bg-white/10"></div>
        </div>
    </div>

    <!-- Messages Area -->
    <div id="chat-container" class="flex-1 p-6 md:p-8 overflow-y-auto space-y-8 custom-scrollbar bg-white/[0.01]">
        <div 
            v-for="msg in messages" 
            :key="msg.id"
            :class="['flex', msg.isUser ? 'justify-end' : 'justify-start', 'animate-in fade-in slide-in-from-bottom-2 duration-500']"
        >
            <div 
                :class="[
                    'max-w-[90%] md:max-w-[80%] rounded-[2rem] px-6 py-5',
                    msg.isUser 
                        ? 'bg-gradient-to-br from-indigo-600 to-violet-600 text-white rounded-tr-sm shadow-xl shadow-indigo-600/10' 
                        : 'glass-card text-slate-200 rounded-tl-sm border border-white/5'
                ]"
            >
                <div class="text-sm font-bold leading-relaxed">{{ msg.text }}</div>
                
                <!-- Tabla de Resultados -->
                <div v-if="msg.data && msg.data.length > 0" class="mt-6 overflow-x-auto rounded-3xl border border-white/5 bg-slate-950/50 shadow-inner">
                    <table class="w-full text-[10px] text-left">
                        <thead>
                            <tr class="text-slate-500 uppercase font-black tracking-widest border-b border-white/10 bg-white/[0.02]">
                                <th v-for="(_val, key) in (msg.data && msg.data.length > 0 ? msg.data[0] : {})" :key="key" class="px-6 py-4">{{ key }}</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-white/5">
                            <tr v-for="(row, idx) in msg.data" :key="idx" class="hover:bg-white/[0.02] transition-colors">
                                <td v-for="(val, key) in row" :key="key" class="px-6 py-4 font-bold text-slate-300">{{ val }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        <div v-if="loading" class="flex justify-start">
             <div class="glass-card rounded-[1.5rem] px-5 py-4 border border-white/10 flex items-center space-x-2">
                <span class="w-2 h-2 bg-indigo-500 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                <span class="w-2 h-2 bg-indigo-500 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                <span class="w-2 h-2 bg-indigo-500 rounded-full animate-bounce"></span>
             </div>
        </div>
    </div>

    <!-- Input Area -->
    <div class="p-6 md:p-8 bg-white/[0.02] border-t border-white/5">
        <form @submit.prevent="sendMessage" class="flex gap-4">
            <input 
                v-model="input" 
                :disabled="loading"
                placeholder="Pregunta algo sobre el inventario..." 
                class="flex-1 bg-slate-900 border border-white/5 rounded-2xl px-6 py-5 text-white font-bold focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all placeholder:text-slate-600 shadow-inner"
            />
            <button 
                type="submit" 
                :disabled="loading || !input.trim()"
                class="w-16 h-16 bg-gradient-to-br from-indigo-600 to-violet-600 hover:scale-105 active:scale-95 disabled:opacity-30 disabled:grayscale text-white rounded-2xl flex items-center justify-center transition-all shadow-xl shadow-indigo-600/20"
            >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
            </button>
        </form>
    </div>
  </div>
</template>
