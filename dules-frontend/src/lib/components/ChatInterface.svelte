<script lang="ts">
    import {chatApi} from '$lib/api';

    interface Message {
        id: number;
        text: string;
        sender: 'user' | 'ai';
    }

    let isOpen = $state(false); // 채팅창 상태용
    let inputText = $state('');
    let messages = $state<Message[]>([
        {id: 0, text: '안녕하세요! 일정에 대해 궁금한 점을 물어보세요!', sender: 'ai'}
    ]);
    let isLoading = $state(false)
    
    // 스크롤 자동 이동을 위한 요소 참조
    let chatContainer = $state<HTMLDivElement>();

    async function sendMessage(e: SubmitEvent) {
        e.preventDefault();

        if (!inputText.trim() || isLoading) return;

        const userMsg = inputText;
        messages = [...messages, { id: Date.now(), text: userMsg, sender: 'user'}];
        inputText = '';
        scrollToBottom();

        isLoading = true;

        try {
            const response = await chatApi.sendMessage(userMsg);

            messages = [...messages, { id: Date.now() + 1, text: response.answer, sender: 'ai'}];
        } catch (e) {
            messages = [...messages, { id: Date.now() + 1, text: '오류가 발생했습니다.', sender: 'ai'}];
        } finally {
            isLoading = false;
            scrollToBottom();
        }
    }
    
    function scrollToBottom() {
        // DOM 업데이트 후 실행
        setTimeout(() => {
            if (chatContainer) chatContainer.scrollTop = chatContainer.scrollHeight;
        }, 0);
    }
</script>

<!-- 채팅 플로팅 버튼-->
<div class="fixed bottom-6 right-6 z-50">
    {#if !isOpen}
        <button
            onclick={() => isOpen = true}
            class="bg-indigo-600 hover:bg-indigo-700 text-white rounded-full p-4 shadow-lg transition-all"> AI 비서
        </button>
    {:else}
        <!-- 채팅창 UI-->
        <div class="bg-white rounded-lg shadow-2xl w-80 sm:w-96 flex flex-col border border-gray-200" style="height:500px;">
            <!--헤더-->
            <div class="bg-indigo-600 text-white p-4 rounded-t-lg flex justify-between items-center">
                <h3 class="font-bold">Dules AI</h3>
                <button onclick={() => isOpen = false} class="text-white hover:text-gray-200">X</button>
            </div>

            <!-- 메세지 목록-->
            <div 
                bind:this={chatContainer}
                class="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50"
            >
                {#each messages as msg (msg.id)}
                    <div class={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div class={`max-w-[80%] rounded-lg p-3 text-sm whitespace-pre-wrap ${msg.sender === 'user' ? 'bg-indigo-500 text-white rounded-br-none' : 'bg-white text-gray-800 border border-gray-200 rounded-bl-none shawdow-sm'}`}>
                            {msg.text}
                        </div>
                    </div>
                {/each}
                {#if isLoading}
                    <div class="flex justify-start">
                        <div class="bg-gray-200 text-gray-500 rounded-lg p-2 text-xs animate-pulse">
                            생각 중...
                        </div>
                    </div>
                {/if}
            </div>

            <!-- 입력 창 -->
            <div class="p-3 border-t bg-white rounded-b-lg">
                <form onsubmit={sendMessage} class="flex gap-2">
                    <input
                        type="text"
                        bind:value={inputText}
                        placeholder="질문을 입력하세요."
                        class="flex-1 border rounded px-3 py-2 text-sm focus:outline-none focus:border-indigo-500" 
                    />
                    <button 
                        type="submit"
                        disabled={isLoading}
                        class="bg-indigo-600 text-white px-4 py-2 rounded text-sm hover:bg-indigo-700 disabled:opacity-50"
                    >
                    전송
                    </button>
                </form>
            </div>
        </div>
    {/if}
</div>