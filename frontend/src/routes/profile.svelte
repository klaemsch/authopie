<script lang="ts">

    import api from '$lib/api'

    import { onMount } from 'svelte';

    let data = {};
    let errorMessage = '';

    onMount(() => {
        data['token'] = document.cookie.replace('token=', '');
    });

    function validateToken(event) {
        api
			.validate(data)
			.then((res) => {
				console.log(res);
			})
			.catch((error) => {
				console.log(error.response);
                errorMessage = error.response.data.detail;
			});
    };

</script>

<div class="container">
    <div>
        last token: {data['token']}
    </div>
    <button on:click={validateToken}>
        Validate
    </button>
    <div>
        {errorMessage}
    </div>
    <a href="/">Renew</a>
</div>