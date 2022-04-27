<script lang="ts">
	import '../app.css';
    import Header from '$lib/Header.svelte'
</script>

<svelte:head>
	<title>TinyAuth</title>
</svelte:head>

<Header />

<main>
	<slot />
</main>
