import axios from "axios";
import type { Schedule, ScheduleCreate, ChatResponse} from '$lib/types';
import { form } from "$app/server";

// 설정 중앙 관리용
const client = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    headers: {
        'Content-Type': 'application/json'
    },
})

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
                'content-Type': 'multipart/form-data',
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

