import { scheduleApi } from "$lib/api";
import type { Schedule } from "$lib/types";

class ScheduleStore {
    schedules = $state<Schedule[]>([]);
    memos = $state<Schedule[]>([]);

    loading = $state(true);
    error = $state('');

    async load() {
        this.loading = true;
        try {
            const data = await scheduleApi.getAll({ exclude_type: 'MEMO' });
            
            this.schedules = data.sort((a, b) => {
                const timeA = a.created_at ? new Date(a.created_at).getTime() : 0;
                const timeB = b.created_at ? new Date(b.created_at).getTime() : 0;
                return timeB - timeA;
            });
            this.error = '';
        } catch (e) {
            this.error = '데이터를 불러오는데 실패했습니다.';
            console.error(e);
        } finally {
            this.loading = false;
        }
    }

    async loadMemos() {
        this.loading = true;
        try {
            const data = await scheduleApi.getAll({ type: 'MEMO' });
            
            this.schedules = data.sort((a, b) => {
                const timeA = a.created_at ? new Date(a.created_at).getTime() : 0;
                const timeB = b.created_at ? new Date(b.created_at).getTime() : 0;
                return timeB - timeA;
            });
            this.error = '';
        } catch (e) {
            this.error = '메모를 불러오는데 실패했습니다.';
            console.error(e);
        } finally {
            this.loading = false;
        }
    }
}

export const scheduleStore = new ScheduleStore();