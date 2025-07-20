async function analyzeCar(imageFile) {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    try {
        const response = await fetch('http://localhost:8000/analyze-car', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.text();
            throw new Error(error);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

function setupUpload() {
    const uploadBtn = document.getElementById('upload-btn');
    const fileInput = document.getElementById('car-image');
    const resultsDiv = document.getElementById('results');
    
    uploadBtn.addEventListener('click', async () => {
        if (!fileInput.files.length) {
            alert('Please select an image first');
            return;
        }
        
        try {
            uploadBtn.disabled = true;
            uploadBtn.textContent = 'Processing...';
            
            const result = await analyzeCar(fileInput.files[0]);
            
            resultsDiv.innerHTML = `
                <h3>Vehicle: ${result.vehicle.make} ${result.vehicle.model}</h3>
                ${result.listings ? `<a href="${result.listings}" target="_blank">View Listings</a>` : 'No listings found'}
            `;
        } catch (error) {
            resultsDiv.innerHTML = `<p class="error">Error: ${error.message}</p>`;
        } finally {
            uploadBtn.disabled = false;
            uploadBtn.textContent = 'Analyze Car';
        }
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', setupUpload);