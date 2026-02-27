import axios from "axios";
import { get } from 'svelte/store';
import { auth, logout } from '$lib/stores/auth';
import { goto } from "$app/navigation";
import type { Schedule, ScheduleCreate, ChatResponse} from '$lib/types';
import { PUBLIC_API_URL } from '$env/static/public';

// 설정 중앙 관리용
const client = axios.create({
    baseURL: `${PUBLIC_API_URL}/api/v1`,
    headers: {
        'Content-Type': 'application/json'
    },
})

// Request Intercepter
client.interceptors.request.use((config) => {
    const state = get(auth);

    if (state.token) {
        config.headers.Authorization = `Bearer ${state.token}`;
    }
    return config;
});

// Access token 만료에 따른 재발급을 위한 로그인 화면 처리
client.interceptors.response.use(
    response => response,
    error => {
        if (error.response?.status === 401) {
            logout();
            goto('/login');
        }
        return Promise.reject(error);
    }
)

// [임시] 개발용 Mock 유저 ID
const TEST_USER_ID = "00000000-0000-0000-0000-000000000001";

export const scheduleApi = {
    // 일정 목록 조회
    getAll: async (): Promise<Schedule[]> => {
        const response = await client.get<Schedule[]>('/schedules/');
        return response.data;
    },

    // 일정 생성
    create: async (data: ScheduleCreate): Promise<Schedule> => {
        const response = await client.post<Schedule>('/schedules/', data);
        return response.data;
    },

    // 이미지로 일정 생성
    uploadImage: async (file: File): Promise<Schedule> => {
        const formData = new FormData();
        formData.append('file', file);

        const response = await client.post<Schedule>('/schedules/image', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    // 검색
    search: async (query: string): Promise<string[]> => {
        const response = await client.get<string[]>('/schedules/search', {
            params: { query }
        });
        return response.data;
    }
}

export const chatApi = {
    sendMessage: async (message: string): Promise<ChatResponse> => {
        const response = await client.post<ChatResponse>('/chat/', { message });
        return response.data;
    }
}

export const authApi = {
    login: async (formData: FormData) => {
        const response = await client.post('/auth/login', formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        return response.data;
    },

    signup: async (data: any) => {
        const response = await client.post('/auth/signup', data);
        return response.data;
    },

    logout: async () => {
        await client.post('/auth/logout');
    }
};

