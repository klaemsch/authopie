<script lang="ts">
	import api from '$lib/api';

	const onSubmit = async (event) => {
		// get form data
		const formData = new FormData(event.target);

		// convert form data to json
		const data = {};
		formData.forEach((value, key) => (data[key] = value));

		// send data to api
		api
			.register(data)
			.then((res) => {
				console.log(res);
				// redirect to /profile
				window.location.href = '/profile';
			})
			.catch((error) => {
				console.log(error);
			});
	};
</script>

<div class="form-container child-container right">
	<h1>Register</h1>
	<form on:submit|preventDefault={onSubmit}>
		<input type="email" name="email" value="" placeholder="Email" />
		<input type="password" name="password" value="" placeholder="Password" />
		<button class="submit-button" type="submit">Register</button>
	</form>
</div>

<style>
	.right {
		right: 0;
	}
</style>
