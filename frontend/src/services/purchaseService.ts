import api from './api';

export interface PurchaseRecord {
    id: number;
    llave: number;
    llave_codigo: string;
    proveedor: number;
    proveedor_nombre: string;
    cantidad: number;
    precio_pago: number | string | null;
    fecha: string;
}

const purchaseService = {
    getPurchases(proveedor_id?: number | string | null, fecha?: string | null) {
        let url = '/compras/';
        const params = new URLSearchParams();
        if (proveedor_id) params.append('proveedor', String(proveedor_id));
        if (fecha) params.append('fecha', fecha);

        const queryString = params.toString();
        if (queryString) url += `?${queryString}`;

        return api.get(url);
    }
};

export default purchaseService;
