<script lang="ts">
    import { goto } from "$app/navigation";
	import { authApi } from "$lib/api";

    let email = $state('');
    let name = $state('');
    let password = $state('');
    let error = $state('');

    async function handleSignup(e: SubmitEvent) {
        e.preventDefault();
        try {
            await authApi.signup({email, name, password})
            alert('가입이 완료되었습니다. 로그인해주세요.');
            goto('/login');
        } catch (e: any) {
            error = e.message?.data?.message || '회원가입 실패';
        }
    }
</script>

<div class="flex items-center justify-center min-h-screen bg-gray-100">
    <div class="bg-white p-8 rounded-lg shadow-md w-96">
        <h1 class="text-2xl font-bold mb-6 text-center text-indigo-600">회원가입</h1>

        {#if error}
            <div class="bg-red-100 text-red-700 p-3 rounded mb-4 text-sm">{error}</div>
        {/if}

        <form onsubmit={handleSignup} class="space-y-4">
            <div>
                <label for="email" class="block text-sm font-medium text-gray-700">이메일</label>
                <input
                    id="email"
                    type="email"
                    bind:value={email}
                    required
                    class="mt-1 block w-full border border-gray-300 rounded-md p-2" 
                />
            </div>
            <div>
                <label for="name" class="block text-sm font-medium text-gray-700">이름</label>
                <input 
                    id="name" 
                    type="text" 
                    bind:value={name} 
                    required 
                    class="mt-1 block w-full border border-gray-300 rounded-md p-2"
                />
            </div>
            <div>
                <label for="password" class="block text-sm font-medium text-gray-700">비밀번호 (8자 이상)</label>
                <input
                    id="password"
                    type="password"
                    bind:value={password}
                    required
                    minlength="8"
                    class="mt-1 block w-full border border-gray-300 rounded-md p-2"
                />
            </div>
            <button
                type="submit"
                class="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700">
            가입하기
            </button>
        </form>
    </div>
</div>