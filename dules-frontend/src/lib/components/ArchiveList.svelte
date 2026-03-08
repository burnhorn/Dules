<script lang="ts">
    import { onMount } from 'svelte';
    import { scheduleApi } from "$lib/api";

    let memos = $state<any[]>([]);
    let isLoading = $state(true);

    async function loadMemos() {
        isLoading = true;
        try {
            memos = await scheduleApi.getAll({ type: 'MEMO' });
        } catch (e) {
            console.error("메모 로드 실패:", e)
        } finally {
            isLoading = false;
        }
    }

    onMount(() => {
        loadMemos();
    });

    function formatDate(dateString: string) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' });
    }
</script>

<div class="p-4 space-y-4 pb-24">
    <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-800">보관함</h2>
        <button onclick={loadMemos} class="text-sm text-indigo-600 hover:text-indigo-800">
            새로고침
        </button>
    </div>

    {#if isLoading}
        <div class="text-center text-gray-500 py-10 animate-pulse">
            메모를 불러오는 중입니다...
        </div>
    {:else if memos.length === 0}
        <div class="text-center py-12 bg-gray-50 rounded-xl border border-gray-100">
            <span class="text-4xl block mb-3">🗂️</span>
            <p class="text-gray-500">아직 보관된 메모나 회의록이 없습니다.</p>
        </div>
    {:else}
        <div class="space-y-4">
            {#each memos as memo}
                <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-200 transition hover:shadow-md">
                    <div class="flex justify-between items-start mb-2">
                        <h3 class="text-lg font-bold text-gray-800">{memo.title}</h3>
                        <span class="text-xs font-medium text-gray-400 bg-gray-100 px-2 py-1 rounded-md">
                            {formatDate(memo.created_at)}
                        </span>
                    </div>
                    
                    {#if memo.description}
                        <p class="text-gray-600 text-sm whitespace-pre-line leading-relaxed">
                            {memo.description}
                        </p>
                    {/if}
                </div>
            {/each}
        </div>
    {/if}
</div>