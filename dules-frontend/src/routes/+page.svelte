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

    // 데이터 로딩 함수
    async function loadSchedules() {
        loading = true;
        try {
            schedules = await scheduleApi.getAll();
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
            onclick={() => isFormOpen = true}
            class="bg-indigo-100 text-indigo-700 px-4 py-2 rounded-lg hover:bg-indigo-200 font-semibold"
        >
        ➕ 직접 추가
        </button>
    </div>

    <ImageUpload onuploaded={loadSchedules} />

    {#if loading}
        <div class="text-center p-4">로딩 중...</div>
    {:else if error}
        <div class="bg-red-100 text-red-700 p4 rounded mb-4">{error}</div>
    {:else}
        <div class="space-y-4">
            {#each schedules as schedule}
                <div class="border rounded-lg p-4 shadow-sm hover:shadow-md transition bg-white">
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
    
    <!-- 모달: 조건부 렌더링-->
    {#if isFormOpen}
        <ScheduleForm
            onclose={() => isFormOpen = false}
            onsuccess={loadSchedules}
        />
    {/if}
    
    <ChatInterface />
</main>