
import api from './api';

export interface CheckoutHistoryItem {
    id: number;
    llave: number;
    llave_codigo: string;
    user: number;
    user_name: string;
    cantidad: number;
    fecha: string;
}

export default {
    getHistory(params?: { user?: number | string, fecha?: string }) {
        return api.get<CheckoutHistoryItem[]>('/historial/', { params });
    }
};
