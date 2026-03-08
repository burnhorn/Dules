import axios from "axios";
import { get } from 'svelte/store';
import { auth, login, logout } from '$lib/stores/auth';
import { goto } from "$app/navigation";
import type { Schedule, ScheduleCreate, ChatResponse} from '$lib/types';
import { PUBLIC_API_URL } from '$env/static/public';

// 설정 중앙 관리용
const client = axios.create({
    baseURL: `${PUBLIC_API_URL}/api/v1`,
    timeout: 30000,
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
    async error => {
        const originalRequest = error.config;

        if (error.response?.status == 401 && !originalRequest._retry){
            originalRequest._retry = true;

            try {
                const state = get(auth);
                const refreshToken = state.refreshToken;

                if (!refreshToken) {
                    throw new Error("Refresh Token 없음")
                }

                const { data } = await axios.post(`${PUBLIC_API_URL}/api/v1/auth/refresh`, {
                    refresh_token: refreshToken
                });

                login(data.access_token, data.refresh_token, state.userEmail || "")

                originalRequest.headers.Authorization = `Bearer ${data.access_token}`;

                return client(originalRequest)
            } catch (refreshError) {
                console.error("토큰 갱신 실패", refreshError);
                logout();
                goto('/login');
                return Promise.reject(refreshError)
            }
        }

        return Promise.reject(error);
    }
);

export const scheduleApi = {
    // 일정 목록 조회
    getAll: async (params?: { type?: string; exclude_type?: string }): Promise<Schedule[]> => {
        const queryString = params
            ? '?' + new URLSearchParams(params as Record<string, string>).toString()
            : '';

        const response = await client.get<Schedule[]>(`/schedules/${queryString}`);
        return response.data;
    },

    // 일정 생성
    create: async (data: ScheduleCreate): Promise<Schedule> => {
        const response = await client.post<Schedule>('/schedules/', data);
        return response.data;
    },

    // 이미지로 일정 생성
    uploadImage: async (file: File): Promise<Schedule[]> => {
        const formData = new FormData();
        formData.append('file', file);

        const response = await client.post<Schedule[]>('/schedules/image', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    // 일정 수정
    update: async (id: string, data: Partial<ScheduleCreate>) : Promise<Schedule> => {
        const response = await client.patch<Schedule>(`/schedules/${id}`, data);
        return response.data;
    },

    // 일정 삭제
    delete: async (id: string): Promise<void> => {
        await client.delete(`/schedules/${id}`)
    }
}

export const chatApi = {
    // 검색
    search: async (query: string): Promise<string[]> => {
        const response = await client.post<{ answer: string }>('/chat/', {
            message: query
        });

        const answerText = response.data.answer || "답변을 생성하지 못했습니다."

        return answerText.split('\n').filter(line => line.trim() !== '');
    },

    // // AI와 챗(업데이트 예정)
    // sendMessage: async (message: string): Promise<ChatResponse> => {
    //     const response = await client.post<ChatResponse>('/chat/sendMessage', { message });
    //     return response.data;
    // }
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

