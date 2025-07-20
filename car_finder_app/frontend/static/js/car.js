// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const preview = document.getElementById('preview');
const analyzeBtn = document.getElementById('analyzeBtn');
const loadingIndicator = document.getElementById('loadingIndicator');
const footerMessage = document.querySelector('footer p');

// Event Listeners
uploadArea.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
analyzeBtn.addEventListener('click', analyzeCar);

// Handle file selection
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        preview.src = e.target.result;
        preview.style.display = 'block';
        analyzeBtn.disabled = false;
        footerMessage.textContent = 'Ready to analyze!';
    };
    reader.readAsDataURL(file);
}

// Drag and Drop functionality
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        handleFileSelect({ target: fileInput });
    }
});

// Analyze car function
async function analyzeCar() {
    if (!fileInput.files.length) return;

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('image', file);

    try {
        // Show loading state
        loadingIndicator.style.display = 'flex';
        analyzeBtn.disabled = true;
        footerMessage.textContent = 'Analyzing your car...';

        // Send to backend
        const response = await fetch('http://localhost:8000/analyze-car', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(await response.text());
        }

        const result = await response.json();
        
        // Display results
        footerMessage.innerHTML = `
            Identified as: <strong>${result.vehicle.make} ${result.vehicle.model}</strong>
            ${result.listings ? `<br><a href="${result.listings}" target="_blank">View listings</a>` : ''}
        `;
        
    } catch (error) {
        console.error('Error:', error);
        footerMessage.textContent = 'Error analyzing car. Please try again.';
    } finally {
        loadingIndicator.style.display = 'none';
        analyzeBtn.disabled = false;
    }
}