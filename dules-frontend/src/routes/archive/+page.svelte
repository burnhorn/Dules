<script lang="ts">
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { auth } from "$lib/stores/auth";
    import ArchiveList from '$lib/components/ArchiveList.svelte';

    onMount(() => {
        if (!$auth.isAuthenticated) {
            goto('/login');
        }
    });
</script>

{#if $auth.isAuthenticated}
    <ArchiveList />
{/if}