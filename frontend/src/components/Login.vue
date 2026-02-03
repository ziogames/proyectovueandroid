<script setup lang="ts">
import { ref } from 'vue';
import api from '../services/api';

const username = ref('');
const password = ref('');
const error = ref('');
const emit = defineEmits(['login-success']);

const login = async () => {
    try {
        const response = await api.post('token/', {
            username: username.value,
            password: password.value
        });
        
        // Guardar tokens
        localStorage.setItem('access_token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);
        
        // Configurar el header por defecto para futuras peticiones (opcional, si usamos interceptor esto es redundante pero seguro)
        api.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`;
        
        emit('login-success');
    } catch (err) {
        error.value = 'Credenciales inválidas o error en el servidor.';
        console.error(err);
    }
};
</script>

<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-900 px-4">
    <div class="w-full max-w-md bg-gray-800 rounded-xl shadow-2xl border border-gray-700 overflow-hidden">
      <!-- Header -->
      <div class="bg-gray-800 p-8 text-center border-b border-gray-700">
        <h1 class="text-3xl font-bold text-indigo-500 tracking-wider">KEY<span class="text-white">MASTER</span></h1>
        <p class="text-gray-400 mt-2">Inicia sesión para acceder</p>
      </div>

      <!-- Form -->
      <div class="p-8">
        <form @submit.prevent="login" class="space-y-6">
            <div v-if="error" class="bg-red-900/50 border border-red-500 text-red-200 text-sm p-3 rounded">
                {{ error }}
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-400 mb-2">Usuario</label>
                <div class="relative">
                    <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-400">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
                        </svg>
                    </span>
                    <input v-model="username" type="text" required class="w-full bg-gray-900 border border-gray-700 rounded-lg pl-10 pr-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition" placeholder="Ingresa tu usuario" />
                </div>
            </div>

            <div>
                 <label class="block text-sm font-medium text-gray-400 mb-2">Contraseña</label>
                 <div class="relative">
                    <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-400">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
                        </svg>
                    </span>
                    <input v-model="password" type="password" required class="w-full bg-gray-900 border border-gray-700 rounded-lg pl-10 pr-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 transition" placeholder="••••••••" />
                </div>
            </div>

            <button type="submit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-4 rounded-lg shadow-lg transition duration-200">
                Entrar
            </button>
        </form>
      </div>
      
      <div class="bg-gray-750 p-4 text-center text-xs text-gray-500 border-t border-gray-700">
        &copy; 2026 Antigravity System
      </div>
    </div>
  </div>
</template>
