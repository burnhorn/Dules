export type ScheduleType = 'EVENT' | 'TASK' | 'MEMO';

export interface Schedule {
    id: string; // UUID
    user_id: string,
    title: string,
    description?: string | null;
    type: ScheduleType;
    start_at?: string | null; // ISO Date String
    end_at?: string | null;
    deadline?: string | null;
    created_at: string;
    updated_at?: string | null;
}

export interface ScheduleCreate {
    title: string;
    description?: string;
    type: ScheduleType;
    start_at?: string;
    end_at?: string;
    deadline?: string;
}

export interface ApiResponse<T> {
    success: boolean;
    code: string;
    message?: string;
    content?: T;
}

export interface ChatResponse{
    answer: string;
}