import { reactive, watch } from 'vue';

export interface CheckoutItem {
    id: number;
    cod_llave: string;
    cantidad: number;
    stock_actual: number;
}

const STORAGE_KEY = 'checkout_items';

const saved = localStorage.getItem(STORAGE_KEY);
let initialItems: CheckoutItem[] = [];
try {
    initialItems = saved ? JSON.parse(saved) : [];
} catch (e) {
    console.error('Error parsing checkout items', e);
    initialItems = [];
}

export const checkoutStore = reactive({
    items: initialItems,

    addItem(llave: any) {
        const stockActual = Number(llave.cantidad) || 0;
        const existing = this.items.find((i: CheckoutItem) => i.id === llave.id);
        if (existing) {
            existing.cantidad++;
            existing.stock_actual = stockActual; // Update stock with latest value
        } else {
            this.items.push({
                id: llave.id,
                cod_llave: llave.cod_llave,
                cantidad: 1,
                stock_actual: stockActual
            });
        }
    },

    removeItem(id: number) {
        this.items = this.items.filter((i: CheckoutItem) => i.id !== id);
    },

    updateQuantity(id: number, cantidad: number) {
        const item = this.items.find((i: CheckoutItem) => i.id === id);
        if (item) {
            item.cantidad = cantidad;
        }
    },

    clear() {
        this.items = [];
    }
});

watch(() => checkoutStore.items, (newItems) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newItems));
}, { deep: true });
