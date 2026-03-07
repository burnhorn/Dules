<script lang="ts">
    import { scheduleApi } from "$lib/api";
    import { invalidateAll } from "$app/navigation";

    let isUploading = $state(false);
    let fileInput: HTMLInputElement | null = null;

    async function handleFileSelect(event: Event) {
        const target = event.target as HTMLInputElement;
        if (target.files && target.files.length > 0) {
            const file = target.files[0];
            await uploadFile(file);
        }
    }

    async function uploadFile(file: File) {
        if (isUploading) return;
        isUploading = true;

        try {
            const result = await scheduleApi.uploadImage(file);
            alert(`[분석 완료]\n 일정: ${result.title}\n시간: ${new Date(result.start_at!).toLocaleString()}`);

            await invalidateAll();
        } catch (e) {
            alert("이미지 분석에 실패했습니다. 다시 시도해주세요.")
            console.error(e)
        } finally {
            isUploading = false;
            if (fileInput) fileInput.value = '';
        }
    }

</script>

<nav class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-6 py-3 pb-safe z-50 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
    <div class="flex justify-between items-center max-w-md mx-auto relative">
        
        <a href="/" class="flex flex-col items-center text-gray-500 hover:text-indigo-600 transition">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
            </svg>
            <span class="text-[10px] mt-1 font-medium">홈</span>
        </a>

        <div class="absolute left-1/2 -translate-x-1/2 -top-8">
            <label class={`flex items-center justify-center w-16 h-16 bg-indigo-600 rounded-full shadow-lg cursor-pointer transform transition active:scale-95 ${isUploading ? 'animate-pulse bg-indigo-400' : 'hover:bg-indigo-700'}`}>
                <input 
                    bind:this={fileInput}
                    type="file" 
                    accept="image/*" 
                    capture="environment" 
                    onchange={handleFileSelect}
                    disabled={isUploading}
                    class="hidden" 
                />
                
                {#if isUploading}
                    <svg class="animate-spin w-8 h-8 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                {:else}
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-8 h-8 text-white">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6.827 6.175A2.31 2.31 0 015.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 00-1.134-.175 2.31 2.31 0 01-1.64-1.055l-.822-1.316a2.192 2.192 0 00-1.736-1.039 48.774 48.774 0 00-5.232 0 2.192 2.192 0 00-1.736 1.039l-.821 1.316z" />
                        <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 12.75a4.5 4.5 0 11-9 0 4.5 4.5 0 019 0zM18.75 10.5h.008v.008h-.008V10.5z" />
                    </svg>
                {/if}
            </label>
        </div>

        <a href="/mypage" class="flex flex-col items-center text-gray-500 hover:text-indigo-600 transition">
             <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
            </svg>
            <span class="text-[10px] mt-1 font-medium">내 정보</span>
        </a>
    </div>
</nav>