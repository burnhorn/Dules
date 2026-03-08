<script lang="ts">
    import { onMount } from "svelte";
    import { scheduleApi, authApi, chatApi } from "$lib/api";
    import type { Schedule } from "$lib/types";

    import { auth, logout } from "$lib/stores/auth";
    import { goto } from "$app/navigation";

    import ScheduleForm from "$lib/components/ScheduleForm.svelte";
	import CalendarView from "$lib/components/CalendarView.svelte";

    import { scheduleStore } from "$lib/stores/schedule.svelte";
    
    let isFormOpen = $state(false);
    let selectedSchedule = $state<Schedule | null>(null);
    let searchQuery = $state('');
    let searchResults = $state<string[]>([]);
    let isSearchMode = $state(false);
    let isSearching = $state(false);
    
    onMount(() => {
        if (!$auth.isAuthenticated) {
            goto('/login');
            return; 
        }
        scheduleStore.load();
    })

    async function handleLogout() {
        try {
            await authApi.logout(); 
        } catch (e) {
            console.error("로그아웃 요청 실패" , e)
        } finally {
            logout();
            goto('/login');
        }
    }

    function openEditModal(schedule: Schedule) {
        selectedSchedule = schedule;
        isFormOpen = true
    }

    function openCreateModal() {
        selectedSchedule = null;
        isFormOpen = true
    }

    async function handleSearch(e: SubmitEvent) {
        e.preventDefault(); 
        
        if (!searchQuery.trim()) return;

        isSearching = true
        isSearchMode = true

        try {
            searchResults = await chatApi.search(searchQuery);
        } catch (e) {
            console.error(e);
            alert('검색 중 오류가 발생했습니다.')
        } finally {
            isSearching = false;
        }
    }

    function closeSearch() {
        isSearchMode = false;
        searchQuery = '';
        searchResults = [];
    }
</script>

{#if $auth.isAuthenticated}
    <div class="px-5 py-6 min-h-screen bg-white"> 
        
        <div class="flex justify-between items-center mb-6">
            <h1 class="text-2xl font-bold text-gray-900 tracking-tight">나의 일정</h1>
            
            <div class="flex gap-2">
                <button 
                    onclick={openCreateModal}
                    class="w-10 h-10 flex items-center justify-center rounded-full bg-indigo-50 text-indigo-600 hover:bg-indigo-100 transition-colors"
                    aria-label="일정 직접 추가"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-6 h-6">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                    </svg>
                </button>

                <button 
                    onclick={handleLogout}
                    class="w-10 h-10 flex items-center justify-center rounded-full bg-gray-100 text-gray-500 hover:bg-gray-200 transition-colors"
                    aria-label="로그아웃"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-5 h-5">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
                    </svg>
                </button>
            </div>
        </div>
        
        <div class="mb-6 sticky top-0 z-30 bg-white pb-2">
            <form onsubmit={handleSearch} class="relative group">
                <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none" aria-hidden="true">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5 text-indigo-500 group-focus-within:text-indigo-600 transition-colors">
                        <path fill-rule="evenodd" d="M9 4.5a.75.75 0 01.721.544l.813 2.846a3.75 3.75 0 002.576 2.576l2.846.813a.75.75 0 010 1.442l-2.846.813a3.75 3.75 0 00-2.576 2.576l-.813 2.846a.75.75 0 01-1.442 0l-.813-2.846a3.75 3.75 0 00-2.576-2.576l-2.846-.813a.75.75 0 010-1.442l2.846-.813a3.75 3.75 0 002.576-2.576l.813-2.846A.75.75 0 019 4.5zM6 20.25a.75.75 0 01.75.75v.008c0 .414-.336.75-.75.75h-.008a.75.75 0 01-.75-.75V21c0-.414.336-.75.75-.75H6z" clip-rule="evenodd" />
                    </svg>
                </div>
                
                <input 
                    type="text"
                    bind:value={searchQuery}
                    placeholder="AI에게 물어보세요 (예: 오늘 놓친 거 없어?)"
                    aria-label="일정 검색 및 AI 질문" 
                    class="block w-full pl-12 pr-12 py-3.5 bg-gray-50 border-0 text-gray-900 rounded-2xl ring-1 ring-inset ring-gray-200 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 focus:bg-white sm:text-sm sm:leading-6 shadow-sm transition-all"
                />
                
                <button 
                    type="submit"
                    disabled={isSearching}
                    class="absolute inset-y-0 right-0 flex items-center pr-3"
                    aria-label="검색 전송"
                >
                    <div class="p-1.5 rounded-full text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors">
                        {#if isSearching}
                            <svg class="animate-spin h-5 w-5" aria-label="검색 중" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                        {:else}
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5">
                                <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
                            </svg>
                        {/if}
                    </div>
                </button>
            </form>
        </div>

        {#if isSearchMode}
            <div class="bg-white rounded-2xl p-5 border border-indigo-100 shadow-sm mb-6">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="font-bold text-indigo-900 text-sm flex items-center gap-2">AI 답변</h3>
                    <button onclick={closeSearch} class="text-xs text-gray-500 underline py-2 px-2">닫기</button>
                </div>
                
                {#if isSearching}
                    <div class="text-center py-6 text-sm text-gray-500 animate-pulse">기억을 더듬고 있습니다...</div>
                {:else if searchResults.length > 0}
                    <div class="bg-indigo-50/50 p-4 rounded-xl text-sm text-gray-800 leading-relaxed border border-indigo-100 whitespace-pre-wrap">
                        {searchResults.join('\n\n')}
                    </div>
                {:else}
                    <div class="text-center py-6 text-sm text-gray-500">관련된 내용이 없어요.</div>
                {/if}
            </div>

        {:else if scheduleStore.loading}
            <div class="text-center p-10 text-gray-400">로딩 중...</div>

        {:else if scheduleStore.error}
            <div class="bg-red-50 text-red-600 p-4 rounded-lg text-sm">{scheduleStore.error}</div>

        {:else}
            <div class="pb-20"> 
                <CalendarView
                    schedules={scheduleStore.schedules}
                    onEventClick={openEditModal}
                />
                {#if scheduleStore.schedules.length === 0}
                    <div class="flex flex-col items-center justify-center py-20 text-gray-400">
                        <span class="text-4xl mb-2">📷</span>
                        <p class="text-sm">하단 카메라 버튼을 눌러<br>일정을 추가해보세요!</p>
                    </div>
                {/if}
            </div>
        {/if}

        {#if isFormOpen}
            <ScheduleForm
                onclose={() => isFormOpen = false}
                onsuccess={() => scheduleStore.load()}
                scheduleToEdit={selectedSchedule}
            />
        {/if}
    </div>
{/if}