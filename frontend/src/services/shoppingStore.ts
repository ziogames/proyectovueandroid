import { reactive, watch } from 'vue';

const STORAGE_KEY = 'shopping_list_items';

export interface ShoppingItem {
    id: number;
    cod_llave: string;
    cantidad: number;
    proveedor_id: number;
    proveedor_nombre: string;
    precio_compra: number;
    stock_actual: number;
}

// Leer localStorage de forma segura y garantizar que siempre sea un array
let _parsed: any = [];
try {
    _parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
} catch (e) {
    console.warn('shoppingStore: contenido de localStorage inválido, reiniciando a []', e);
    _parsed = [];
}
const initialItems: ShoppingItem[] = Array.isArray(_parsed) ? _parsed : [];

export const shoppingStore = reactive({
    items: initialItems,

    addItem(llave: any, cantidad: number = 0, targetStock: number = 300) {
        // Asegurar que items sea un array
        if (!Array.isArray(this.items)) this.items = [];
        const stockActual = Number(llave.cantidad) || 0;
        // Cantidad sugerida: diferencia para llegar al targetStock, o lo que pida el usuario
        // Si cantidad es 0 (auto-fill), calculamos: max(0, targetStock - llave.cantidad)
        let qtyToAdd = cantidad;
        if (cantidad === 0) {
            qtyToAdd = Math.max(0, targetStock - llave.cantidad);
            if (qtyToAdd === 0) return; // No agregar si ya tiene suficiente
        }

        const existing = this.items.find((i: ShoppingItem) => i.id === llave.id);
        if (existing) {
            // Always update current stock
            existing.stock_actual = stockActual;

            // Si ya existe, actualizamos cantidad si viene de auto-fill (para asegurar stock base) o sumamos
            if (cantidad === 0) {
                existing.cantidad = Math.max(existing.cantidad, qtyToAdd);
            } else {
                existing.cantidad += qtyToAdd;
            }
        } else {
            this.items.push({
                id: llave.id,
                cod_llave: llave.cod_llave,
                cantidad: qtyToAdd,
                proveedor_id: llave.proveedor,
                proveedor_nombre: llave.proveedor_nombre || 'Desconocido',
                precio_compra: Number(llave.precio_compra) || 0.90,
                stock_actual: stockActual
            });
        }
    },

    removeItem(id: number) {
        if (!Array.isArray(this.items)) this.items = [];
        this.items = this.items.filter((i: ShoppingItem) => i.id !== id);
    },

    updateQuantity(id: number, cantidad: number) {
        if (!Array.isArray(this.items)) return;
        const item = this.items.find((i: ShoppingItem) => i.id === id);
        if (item) {
            item.cantidad = cantidad;
        }
    },

    clear() {
        this.items = [];
    }
});

// Watch for changes and save to localStorage de forma segura
watch(() => shoppingStore.items, (newItems) => {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(Array.isArray(newItems) ? newItems : []));
    } catch (e) {
        console.warn('shoppingStore: no se pudo persistir items en localStorage', e);
    }
}, { deep: true });
