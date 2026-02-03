import api from './api';

export interface Llave {
    id?: number;
    cod_llave: string;
    cantidad: number;
    img: string | null; // La imagen vendrá como URL o null
    proveedor: number; // ID del proveedor
    proveedor_nombre?: string;
    precio_compra: number | string;
}

export default {
    getLlaves(providerId?: number | string | null) {
        const url = providerId ? `llaves/?proveedor=${providerId}` : 'llaves/';
        return api.get<Llave[]>(url);
    },
    createLlave(data: FormData) {
        // Usamos FormData para subir imágenes
        return api.post<Llave>('llaves/', data, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
    },
    bulkDecrement(items: { id: number; cantidad: number }[]) {
        return api.post('/llaves/bulk_decrement/', { items });
    },
    bulkIncrement(items: { id: number; cantidad: number }[]) {
        return api.post('/historial/bulk_increment/', { items });
    }
};
