import { reactive } from 'vue';

interface Toast {
    id: number;
    message: string;
    type: 'success' | 'error' | 'info';
}

const state = reactive({
    toasts: [] as Toast[]
});

let nextId = 1;

export function useToast() {
    const show = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
        const id = nextId++;
        const toast: Toast = { id, message, type };
        state.toasts.push(toast);

        setTimeout(() => {
            const index = state.toasts.findIndex(t => t.id === id);
            if (index !== -1) {
                state.toasts.splice(index, 1);
            }
        }, 3000); // Desaparece en 3 segundos
    };

    const remove = (id: number) => {
        const index = state.toasts.findIndex(t => t.id === id);
        if (index !== -1) {
            state.toasts.splice(index, 1);
        }
    }

    return {
        toasts: state.toasts,
        show,
        remove,
        success: (msg: string) => show(msg, 'success'),
        error: (msg: string) => show(msg, 'error'),
        info: (msg: string) => show(msg, 'info'),
    };
}
