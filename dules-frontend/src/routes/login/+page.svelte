<script lang="ts">
    import { authApi } from "$lib/api";
    import { login } from "$lib/stores/auth";
    import { goto } from "$app/navigation";

    let email = $state('');
    let password = $state('');
    let error = $state('');

    async function handleLogin(e: SubmitEvent) {
        e.preventDefault();
        try {
            const formData = new FormData();
            formData.append('username', email);
            formData.append('password', password);

            const data = await authApi.login(formData);

            // 토큰 저장
            login(data.access_token, data.refresh_token, email);

            goto('/');
        } catch (e: any) {
            console.error(e);
            error = e.response?.data?.message || "로그인에 실패했습니다."
        }
    }
</script>

<div class="flex items-center justify-center min-h-screen bg-gray-100">
    <div class="bg-white p-8 rounded-lg shadow-md w-96">
        <h1 class="text-2xl font-bold mb-6 text-center text-indigo-600">Dules 로그인</h1>

        {#if error}
            <div class='bg-red-100 text-red-700 p-3 rounded mb-4 text-sm'>{error}</div>
        {/if}

        <form onsubmit={handleLogin} class="space-y-4">
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
                <lable for="password" class="block text-sm font-medium text-gray-700">비밀번호</lable>
                <input 
                    id="password"
                    type="password"
                    bind:value={password}
                    required
                    class="mt-1 block w-full border border-gray-300 rounded-md p-2"
                />
            </div>
            <button
                type="submit"
                class="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700"
            >
                로그인
            </button>
        </form>
        <div class="mt-4 text-center text-sm">
            계정이 없으신가요? <a href="/signup" class="text-indigo-600 hover:underline">회원가입</a>
        </div>
    </div>
</div>