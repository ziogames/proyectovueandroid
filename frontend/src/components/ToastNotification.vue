<script setup lang="ts">
import { useToast } from '../composables/useToast';

const { toasts, remove } = useToast();

const getBgColor = (type: string) => {
    switch (type) {
        case 'success': return 'bg-green-600';
        case 'error': return 'bg-red-600';
        case 'info': return 'bg-blue-600';
        default: return 'bg-gray-700';
    }
};

const getIcon = (type: string) => {
    switch(type) {
        case 'success': 
            return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />`;
        case 'error':
            return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />`;
        default:
            return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />`;
    }
};
</script>

<template>
    <div class="fixed bottom-4 right-4 z-50 flex flex-col space-y-4 pointer-events-none max-w-[calc(100vw-2rem)]">
        <TransitionGroup name="toast">
            <div 
                v-for="toast in toasts" 
                :key="toast.id" 
                class="pointer-events-auto flex items-center w-full overflow-hidden bg-gray-800 rounded-lg shadow-xl border border-gray-700 ring-1 ring-black ring-opacity-5 transform transition-all duration-300 ease-in-out min-w-[400px] max-w-[800px]"
            >
                <div :class="`flex-shrink-0 w-2 h-full absolute left-0 top-0 bottom-0 ${getBgColor(toast.type)}`"></div>
                <div class="p-4 flex items-center w-full pl-6">
                     <div class="flex-shrink-0">
                        <svg class="h-6 w-6 text-white" :class="{'text-green-400': toast.type === 'success', 'text-red-400': toast.type === 'error', 'text-blue-400': toast.type === 'info'}" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" v-html="getIcon(toast.type)">
                        </svg>
                    </div>
                    <div class="ml-3 w-0 flex-1 pt-0.5">
                        <p class="text-sm font-medium text-white">
                            {{ toast.message }}
                        </p>
                    </div>
                    <div class="ml-4 flex-shrink-0 flex">
                        <button @click="remove(toast.id)" class="bg-transparent rounded-md inline-flex text-gray-400 hover:text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                            <span class="sr-only">Cerrar</span>
                            <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        </TransitionGroup>
    </div>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from {
  transform: translateX(100%);
  opacity: 0;
}
.toast-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>
