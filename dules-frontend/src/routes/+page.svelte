<script lang="ts">
    import { onMount } from "svelte";
    import { scheduleApi } from "$lib/api";
    import type { Schedule } from "$lib/types";

    import { auth, logout } from "$lib/stores/auth";
    import { goto } from "$app/navigation";
    import { authApi } from "$lib/api";

    import ScheduleForm from "$lib/components/ScheduleForm.svelte";
    import ChatInterface from "$lib/components/ChatInterface.svelte";
    import ImageUpload from "$lib/components/ImageUpload.svelte";

    let schedules = $state<Schedule[]>([]);
    let loading = $state(true);
    let error = $state('');
    let isFormOpen = $state(false);
    let selectedSchedule = $state<Schedule | null>(null);
    
    let searchQuery = $state('');
    let searchResults = $state<string[]>([]);
    let isSearchMode = $state(false); // false면 전체 목록, true면 검색 결과 랜더링
    let isSearching = $state(false);
    
    // 데이터 로딩 함수
    async function loadSchedules() {
        loading = true;
        try {
            const data = await scheduleApi.getAll();

            schedules = data.map(item => ({
                ...item, createdAtTime: new Date(item.created_at).getTime()
            })).sort((a, b) => b.createdAtTime - a.createdAtTime);
        } catch (e) {
            error = '데이터를 불러오는데 실패했습니다.';
            console.error(e);
        } finally {
            loading = false;
        }
    }

    onMount(() => {
        if (!$auth.isAuthenticated) {
            goto('/login');
        }
        loadSchedules();
    })

    async function handleLogout() {
        try {
            await authApi.logout(); // Redis에 블랙리스트 등록
        } catch (e) {
            console.error("로그아웃 요청 실패" , e)
        } finally {
            logout(); // 클라이언트 스토어 비우기
            goto('/login');
        }
    }

    async function openEditModal(schedule: Schedule) {
        selectedSchedule = schedule;
        isFormOpen = true
    }

    async function openCreateModal() {
        selectedSchedule = null;
        isFormOpen = true
    }

    async function handleSearch(e: Event) {
        e.preventDefault();
        if (!searchQuery.trim()) return;

        isSearching = true
        isSearchMode = true

        try {
            searchResults = await scheduleApi.search(searchQuery);
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

<main class="container mx-auto p-4 max-w-2xl pb-24">
    <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold mb-6 text-center text-indigo-600">Dules Scheduler</h1>
        
        <!-- 로그아웃 버튼-->
        <div class="flex gap-2">
            <button 
                onclick={handleLogout}
                class="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 font-semibold text-sm"
            >
            로그아웃
            </button>
        </div>

        <!-- 수동 추가 버튼-->
        <button
            onclick={openCreateModal}
            class="bg-indigo-100 text-indigo-700 px-4 py-2 rounded-lg hover:bg-indigo-200 font-semibold"
        >
        ➕ 직접 추가
        </button>
    </div>
    
    <div class="mb-8">
        <form onsubmit={handleSearch} class="relative">
            <input 
                type="text"
                bind:value={searchQuery}
                placeholder="AI에게 물어보세요. (예: 이번 달에 놓치지 말아야 할 중요한 일은?)"
                class="w-full border-2 border-indigo-100 rounded-full py-3 px-6 pr-24 focus:outline-none focus:border-indigo-500 shadow-sm transition-colors"
            />
            <button 
                type="submit"
                disabled={isSearching}
                class="absolute right-2 top-2 bottom-2 bg-indigo-600 text-white rounded-full px-6 hover:bg-indigo-700 disabled:bg-gray-400 font-medium transition-colors"
            >
                {isSearching ? '🔍...': '검색'}
            </button>
        </form>
    </div>

    {#if !isSearchMode}
        <ImageUpload onuploaded={loadSchedules} />
    {/if}

    {#if isSearchMode}
        <div class="bg-indigo-50 rounded-xl p-6 border border-indigo-100 mb-6">
            <div class="flex justify-between items-center mb-4">
                <h3 class="font-bold text-indigo-800">벡터 검색 결과</h3>
                <button onclick={closeSearch} class="text-sm text-gray-500 hover:text-gray-700 underline">
                전체 목록으로 돌아가기
                </button>
            </div>

            {#if isSearching}
                <div class="text-center py-8 text-gray-500">AI가 일정을 찾고 있습니다.</div>
            {:else if searchResults.length > 0}
                <ul class="space-y-3">
                    {#each searchResults as result}
                        <li class="bg-white p-4 rounded-lg shadow-sm border border-gray-100 text-gray-700">
                            {result}
                        </li>
                    {/each}
                </ul>
            {:else}
                <div class="text-center py-8 text-gray-500">
                관련된 내용을 찾지 못했습니다
                </div>
            {/if}
        </div>
    {:else}
        {#if loading}
            <div class="text-center p-4">로딩 중...</div>
        {:else if error}
            <div class="bg-red-100 text-red-700 p4 rounded mb-4">{error}</div>
        {:else}
            <div class="space-y-4">
                {#each schedules as schedule}
                    <div class="relative border rounded-lg p-4 shadow-sm hover:shadow-md transition bg-white">
                        <button
                            onclick={() => openEditModal(schedule)}
                            class="absolute top-10 right-4 text-gray-400 hover:text-indigo-600"
                            title="수정">
                            ✎
                        </button>

                        <div class="flex justify-between items-start">
                            <h2 class="text-xl font-semibold">{schedule.title}</h2>
                            <span class={`px-2 py-1 text-xs rounded ${schedule.type === 'EVENT' ? 'bg-blue-100 text-blue-800': 'bg-green-100 text-green-800'}`}>{schedule.type}
                            </span>
                        </div>
                        {#if schedule.description}
                            <p class="text-gray-600 mt-2">{schedule.description}</p>
                        {/if}
                        <div class="text-sm text-gray-400 mt-3 flex gap-4">
                            {#if schedule.start_at}
                                <span> {new Date(schedule.start_at).toLocaleString()}</span>
                            {/if}
                            {#if schedule.deadline}
                                <span class="text-red-400"> 마감: {new Date(schedule.deadline).toLocaleString()}</span>
                            {/if}
                        </div>
                    </div>
                {/each}

                {#if schedules.length === 0}
                    <div class="text-center text-gray-500 py-10">
                        등록된 일정이 없습니다.
                    </div>
                {/if}
            </div>
        {/if}
    {/if}
    
    <!-- 모달: 조건부 렌더링-->
    {#if isFormOpen}
        <ScheduleForm
            onclose={() => isFormOpen = false}
            onsuccess={loadSchedules}
            scheduleToEdit={selectedSchedule}
        />
    {/if}
    
    <ChatInterface />
</main>