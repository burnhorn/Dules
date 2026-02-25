<script lang="ts">
    import { scheduleApi } from "$lib/api";

    let { onuploaded } = $props<{ onuploaded?: () => void}>();

    let isUploading = $state(false);
    let fileInput: HTMLInputElement;

    async function handleFileSelect(event: Event) {
        const target = event.target as HTMLInputElement;
        if (target.files && target.files.length > 0) {
            const file = target.files[0];
            await uploadFile(file);
        }
    }

    async function uploadFile(file: File){
        isUploading = true;
        try {
            const result = await scheduleApi.uploadImage(file);
            alert(`일정이 등록되었습니다: ${result.title}`);
            
            // 존재할 때만 실행
            onuploaded?.();

            if (fileInput) fileInput.value = '';
        } catch (e) {
            alert(`이미지 분석에 실패했습니다.`);
            console.error(e);
        } finally {
            isUploading = false;
        }
    }
</script>

<div class="mb-6">
    <input
        bind:this={fileInput}
        type="file"
        accept="image/*"
        onchange={handleFileSelect}
        class="hidden"
        id="image-upload"
    />

    <label
        for="image-upload"
        class={`block w-full border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer transition hover:border-indigo-500 hover:bg-indigo-50 ${isUploading ? 'opacity-50 pointer-events-none' : ''}`}
    >
        {#if isUploading}
            <div class="text-indigo-600 font-semibold animate-pulse">
                AI가 이미지를 분석하고 있습니다. (OCR)
            </div>
        {:else}
            <div class="text-gray-500">
                <span class="text-indigo-600 font-bold">클릭하여 이미지 업로드</span>
                <br>
                <span class="text-sm">(청첩장, 시간표 등을 AI가 자동으로 분석합니다.)</span>
            </div>
        {/if}
    </label>
</div>