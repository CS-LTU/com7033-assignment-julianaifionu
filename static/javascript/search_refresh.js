const searchInput = document.getElementById('searchInput');
const clearBtn = document.getElementById('clearBtn');

function toggleClearIcon() {
	if (searchInput.value.trim() !== '') {
		clearBtn.style.display = 'block';
	} else {
		clearBtn.style.display = 'none';
	}
}

toggleClearIcon();

searchInput.addEventListener('input', toggleClearIcon);

// Clear input when icon is clicked
clearBtn.addEventListener('click', function () {
	searchInput.value = '';
	toggleClearIcon();
	searchInput.focus();

	// Redirect to base URL to clear search
	window.location.href = window.location.pathname;
});
