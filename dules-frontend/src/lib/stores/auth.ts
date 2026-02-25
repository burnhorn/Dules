import { writable } from 'svelte/store';
import { browser } from '$app/environment';

interface AuthState {
    isAuthenticated: boolean;
    token: string | null;
    userEmail: string | null;
}

const initialState: AuthState = {
    isAuthenticated: false,
    token: null,
    userEmail: null
};

const storedAuth = browser ? localStorage.getItem('auth') : null;
const initialData = storedAuth ? JSON.parse(storedAuth): initialState;

export const auth = writable<AuthState>(initialData);

if (browser) {
    auth.subscribe( (value ) => {
        // isAuthenticated: false의 초기값을 이용하여 로그아웃 상태 보장
        if (value.isAuthenticated) {
            localStorage.setItem('auth', JSON.stringify(value));
        } else {
            localStorage.removeItem('auth');
        }
    });
}


export const login = (token: string, email: string ) => {
    auth.set({
        isAuthenticated: true,
        token,
        userEmail: email
    });
};


export const logout = () => {
    auth.set(initialState);
}