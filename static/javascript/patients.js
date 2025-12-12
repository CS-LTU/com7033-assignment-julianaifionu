function showJsFlash(message, type = 'danger') {
	const flash = document.getElementById('js-flash-container');
	if (!flash) return;

	// clear old flash messages
	flash.innerHTML = '';

	const wrapper = document.createElement('div');
	wrapper.innerHTML = `
      <div class="alert alert-${type} alert-dismissible fade show" role="alert">
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>
    `;

	const alertEl = wrapper.firstElementChild;
	flash.appendChild(alertEl);

	// Auto-dismiss flash after 4 seconds
	setTimeout(() => {
		try {
			if (window.bootstrap && bootstrap.Alert) {
				const alertInstance = bootstrap.Alert.getOrCreateInstance(alertEl);
				alertInstance.close();
			} else {
				alertEl.classList.remove('show');
				alertEl.addEventListener('transitionend', () => alertEl.remove());
			}
		} catch (e) {
			alertEl.remove();
		}
	}, 4000);
}

// Create patient JS logic
let currentStep = 1;

function animateCard() {
	let card = document.getElementById('formCard');
	card.classList.remove('fade-in');
	void card.offsetWidth;
	card.classList.add('fade-in');
}

function updateIcons() {
	for (let i = 1; i <= 4; i++) {
		let circle = document.querySelector('#icon' + i + ' .circle');
		if (i <= currentStep) circle.classList.add('active');
		else circle.classList.remove('active');
	}
}

function showStep(step) {
	document
		.querySelectorAll('.step-section')
		.forEach((sec) => sec.classList.add('d-none'));
	document.getElementById('step' + step).classList.remove('d-none');
	updateIcons();
	animateCard();
}

function nextStep() {
	// Step 1: Demographics
	if (currentStep === 1) {
		if (
			!first_name.value.trim() ||
			!last_name.value.trim() ||
			!date_of_birth.value.trim() ||
			!gender.value.trim()
		) {
			showJsFlash(
				'Please complete demographic information before continuing.',
				'danger'
			);
			return;
		}
	}

	// Step 2: Medical info
	if (currentStep === 2) {
		if (
			!ever_married.value.trim() ||
			!work_type.value.trim() ||
			!residence_type.value.trim() ||
			!smoking_status.value.trim()
		) {
			showJsFlash(
				'Please complete all lifestyle information fields before continuing.',
				'danger'
			);
			return;
		}
	}

	// Step 3: Medical
	if (currentStep === 3) {
		if (
			!avg_glucose_level.value.trim() ||
			!bmi.value.trim() ||
			!stroke.value.trim() ||
			!hypertension.value.trim() ||
			!heart_disease.value.trim()
		) {
			showJsFlash(
				'Please complete all health stats fields before continuing.',
				'danger'
			);
			return;
		}
	}

	if (currentStep < 4) currentStep++;
	if (currentStep === 4) fillReview();

	showStep(currentStep);
}

function previousStep() {
	if (currentStep > 1) currentStep--;
	showStep(currentStep);
}

function fillReview() {
	// Demographic
	document.getElementById('review_demo').innerHTML = `
        <strong>Name:</strong> ${first_name.value} ${last_name.value}<br>
        <strong>DOB:</strong> ${date_of_birth.value}<br>
        <strong>Gender:</strong> ${gender.value}
    `;

	// Lifestyle
	document.getElementById('review_lifestyle').innerHTML = `
        <strong>Married:</strong> ${ever_married.value || 'N/A'}<br>
        <strong>Work Type:</strong> ${work_type.value || 'N/A'}<br>
        <strong>Resident:</strong> ${residence_type.value || 'N/A'}<br>
        <strong>Smoking:</strong> ${smoking_status.value || 'N/A'}
    `;

	// Medical
	document.getElementById('review_medical').innerHTML = `
        <strong>Hypertension:</strong> ${hypertension.value || 'N/A'}<br>
        <strong>Heart Disease:</strong> ${heart_disease.value || 'N/A'}<br>
        <strong>Had Stroke:</strong> ${stroke.value || 'N/A'}<br>
        <strong>BMI:</strong> ${bmi.value || 'N/A'}<br>
        <strong>Glucose Level:</strong> ${avg_glucose_level.value || 'N/A'}
    `;
}

function submitForm() {
	// create a hidden form to POST all data
	const form = document.createElement('form');
	form.method = 'POST';
	form.action = CREATE_PATIENT_URL;

	// CSRF token input
	csfr_input = document.createElement('input');
	csfr_input.type = 'hidden';
	csfr_input.name = 'csrf_token';
	csfr_input.value = CSRF_TOKEN;
	form.appendChild(csfr_input);

	const fields = [
		'first_name',
		'last_name',
		'date_of_birth',
		'gender',
		'ever_married',
		'work_type',
		'residence_type',
		'smoking_status',
		'hypertension',
		'heart_disease',
		'stroke',
		'bmi',
		'avg_glucose_level',
	];

	fields.forEach((id) => {
		let input = document.createElement('input');
		input.type = 'hidden';
		input.name = id;
		input.value = document.getElementById(id).value;
		form.appendChild(input);
	});

	document.body.appendChild(form);
	form.submit();
}
