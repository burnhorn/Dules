<script lang="ts">
    import { scheduleApi } from "$lib/api";
    import type { ScheduleCreate, ScheduleType, Schedule } from "$lib/types";

    let { onclose, onsuccess, scheduleToEdit = null } = $props<{
        onclose: () => void,
        onsuccess: () => void,
        scheduleToEdit?: Schedule | null // 수정 모드와 생성 모드 구분값
    }>();

    let title = $derived(scheduleToEdit?.title ?? '');
    let description = $derived(scheduleToEdit?.description ??'');
    let type = $derived<ScheduleType>(scheduleToEdit?.type ?? 'TASK');
    
    function formatDateForInput(isoString: string | null | undefined) {
        if (!isoString) return '';
        const date = new Date(isoString);
        const kstDate = new Date(date.getTime() - (date.getTimezoneOffset() * 60000));
        return kstDate.toISOString().slice(0, 16);
    }

    let startAt = $derived(formatDateForInput(scheduleToEdit?.start_at));
    let endAt = $derived(formatDateForInput(scheduleToEdit?.end_at));
    let deadline = $derived(formatDateForInput(scheduleToEdit?.deadline));

    let isSubmitting = $state(false);

    async function handleDelete() {
        if (!scheduleToEdit || !scheduleToEdit.id) return;

        if (!confirm('정말 이 일정을 삭제하시겠습니까?')) return;

        try {
            await scheduleApi.delete(scheduleToEdit.id);
            alert('삭제되었습니다.');
            onsuccess();
            onclose();
        } catch (e) {
            console.error(e);
            alert('삭제에 실패했습니다.');
        }
    }

    async function handleSubmit(e: SubmitEvent) {
        e.preventDefault();
        isSubmitting = true;

        try {
            const payload: ScheduleCreate = {
                title,
                description: description || undefined,
                type,
                start_at: type === 'EVENT' && startAt ? new Date(startAt).toISOString() : undefined,
                end_at: type === 'EVENT' && endAt ? new Date(endAt).toISOString() : undefined,
                deadline: type === 'TASK' && deadline ? new Date(deadline).toISOString() : undefined
            };

            if (scheduleToEdit) {
                await scheduleApi.update(scheduleToEdit.id, payload);
                alert('일정이 수정되었습니다.');
            } else {
                await scheduleApi.create(payload as ScheduleCreate);
                alert('일정이 등록되었습니다.')
            }

            onsuccess();
            onclose();
        } catch (error) {
            alert(scheduleToEdit? '수정 실패' : '등록 실패');
            console.error(error);
        } finally {
            isSubmitting = false;
        }
    }
</script>

<!-- 모달 배경 -->
 <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white p-6 rounded-lg shadow-xl w-full max-w-md">
        <h2 class="text-xl font-bold mb-4">
            {scheduleToEdit ? '일정 수정': '새 일정 추가'}
        </h2>

        <form onsubmit={handleSubmit} class="space-y-4">
            <div>
                <label for="title" class="block text-sm font-medium text-gray-700">제목</label>
                <input
                    id="title"
                    type="text"
                    bind:value={title}
                    required
                    class="mt-1 block w-full border border-gray-300 rounded-md p-2" />
            </div>

            <div>
                <label for="type" class="block text-sm font-medium text-gray-700">유형</label>
                <select id="type" bind:value={type} class="mt-1 block w-full border border-gray-300 rounded-md p-2">
                    <option value="TASK">할 일 (Task)</option>
                    <option value="EVENT">이벤트 (Event)</option>
                </select>
            </div>
            
            <div>
                <label for="description" class="block text-sm font-medium text-gray-700">상세 내용</label>
                <textarea
                    id="description"
                    bind:value={description}
                    class="mt-1 block w-full border border-gray-300 rounded-md p-2"></textarea>
            </div>

            <!-- 조건부 렌더링: 타입에 따라 다른 입력창 보여주기 -->
            {#if type === 'EVENT'}
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label for="startAt" class="block text-sm font-medium text-gray-700">시작 시간</label>
                        <input 
                            id="startAt"
                            type="datetime-local" 
                            bind:value={startAt}
                            required
                            class="mt-1 block w-full border border-gray-300 rounded-md p-2"
                        />
                    </div>
                    <div>
                        <label for="endAt" class="block text-sm font-medium text-gray-700">종료 시간</label>
                        <input 
                            id="endAt"
                            type="datetime-local" 
                            bind:value={endAt}
                            required
                            class="mt-1 block w-full border border-gray-300 rounded-md p-2"
                        />
                    </div>
                </div>
            {:else}
                <div>
                    <label for="deadline" class="block text-sm font-medium text-gray-700">마감일</label>
                    <input 
                        id="deadline"
                        type="datetime-local" 
                        bind:value={deadline}
                        class="mt-1 block w-full border border-gray-300 rounded-md p-2"
                    />
                </div>
            {/if}

            <div>
                {#if scheduleToEdit}
                    <button 
                        type="button"
                        onclick={handleDelete}
                        class="px-4 py-2 text-red-500 bg-red-50 hover:bg-red-100 rounded-lg text-sm font-medium transition-colors"
                    >
                        삭제
                    </button>
                {/if}
            </div>

            <div class="flex justify-end gap-2 mt-6">
                <button
                    type="button"
                    onclick={onclose}
                    class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded"
                >
                취소
                </button>
                <button
                    type="submit"
                    disabled={isSubmitting}
                    class="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50"
                >
                    {isSubmitting ? '저장 중...' : '저장'}
                </button>
            </div>
        </form>
    </div>
 </div>