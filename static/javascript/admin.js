function copyActivationLink() {
	const text = document.getElementById('activationLink').textContent;

	navigator.clipboard.writeText(text).then(() => {
		const copyIcon = document.getElementById('copyIcon');
		const checkIcon = document.getElementById('checkIcon');

		copyIcon.classList.add('d-none');
		checkIcon.classList.remove('d-none');

		// Revert after 2 seconds
		setTimeout(() => {
			checkIcon.classList.add('d-none');
			copyIcon.classList.remove('d-none');
		}, 2000);
	});
}
