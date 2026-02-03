import api from './api';

export interface Proveedor {
    id?: number;
    nombre: string;
    direccion: string;
    telefono: string;
    correo: string;
}

export default {
    getProveedores() {
        return api.get<Proveedor[]>('proveedores/');
    },
    createProveedor(proveedor: Proveedor) {
        return api.post<Proveedor>('proveedores/', proveedor);
    },
    // Agrega más métodos si es necesario (update, delete)
};
