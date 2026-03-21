<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { page } from '$app/state';
	import BottomNav from '$lib/components/BottomNav.svelte';

	let { children } = $props();

	let isAuthPage = $derived(
        page.url.pathname.startsWith('/login') || 
        page.url.pathname.startsWith('/signup')
    );
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<div class="min-h-screen bg-gray-50 mx-auto max-w-md shadow-2xl relative">
	<main class="pb-24 min-h-screen bg-white">
		{@render children()}
	</main>

	{#if !isAuthPage}
		<BottomNav />
	{/if}
</div>