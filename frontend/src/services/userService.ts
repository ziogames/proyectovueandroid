import api from './api';

export interface User {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
}

export default {
    getUsers() {
        return api.get<User[]>('/users/');
    }
};
