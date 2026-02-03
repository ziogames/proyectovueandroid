import api from './api';

export interface Llave {
    id?: number;
    cod_llave: string;
    cantidad: number;
    img: string | null; // La imagen vendrá como URL o null
    proveedor: number; // ID del proveedor
    proveedor_nombre?: string;
    precio_compra: number | string;
    tipo?: string;
    tipo_display?: string;
}

export default {
    getLlaves(providerId?: number | string | null, tipo?: string | null) {
        const params: string[] = [];
        if (providerId) params.push(`proveedor=${providerId}`);
        if (tipo) params.push(`tipo=${encodeURIComponent(tipo)}`);
        const query = params.length ? `?${params.join('&')}` : '';
        const url = `llaves/${query}`;
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
