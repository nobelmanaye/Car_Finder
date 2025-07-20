document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('uploadForm');
    const carImageInput = document.getElementById('carImage');
    const resultsDiv = document.getElementById('results');
    const imagePreview = document.getElementById('imagePreview');
    const analysisResult = document.getElementById('analysisResult');
    const carListings = document.getElementById('carListings');

    // Show error message immediately
    function showNotCar(message = "This doesn't appear to be a vehicle") {
        resultsDiv.style.display = 'block';
        analysisResult.innerHTML = `
            <div class="not-vehicle">
                <h2>❌ Not a Vehicle</h2>
                <p>${message}</p>
                <p>Please upload a clear image of a car, truck, or motorcycle.</p>
            </div>
        `;
        carListings.innerHTML = '';
    }

    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const file = carImageInput.files[0];
        if (!file) return;

        // Show preview immediately
        resultsDiv.style.display = 'block';
        const previewUrl = URL.createObjectURL(file);
        imagePreview.innerHTML = `<img src="${previewUrl}" alt="Uploaded vehicle">`;
        
        // Show loading state
        analysisResult.innerHTML = '<p class="loading">🔍 Analyzing image...</p>';
        carListings.innerHTML = '';

        try {
            const formData = new FormData();
            formData.append('image', file);

            const response = await fetch('/api/analyze-car', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!data.success) {
                showNotCar(data.message);
                return;
            }

            // Show vehicle info
            analysisResult.innerHTML = `
                <div class="vehicle-info">
                    <h2>✅ Vehicle Identified</h2>
                    <p><strong>Make:</strong> ${data.make || 'Unknown'}</p>
                    <p><strong>Model:</strong> ${data.model || 'Unknown'}</p>
                    <p><strong>Confidence:</strong> ${Math.round(data.confidence * 100)}%</p>
                </div>
            `;

            // Show listings if available
            if (data.listings) {
                carListings.innerHTML = `
                    <h3>🔎 Listings Found</h3>
                    <a href="${data.listings}" target="_blank" class="listings-link">
                        View ${data.make} ${data.model} listings
                    </a>
                `;
            }

        } catch (error) {
            showNotCar("We couldn't analyze this image");
            console.error("Analysis error:", error);
        } finally {
            URL.revokeObjectURL(previewUrl);
        }
    });

    // Quick client-side check for obvious non-images
    carImageInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;

        // Very basic check - in production you'd want more robust validation
        if (!file.type.startsWith('image/')) {
            showNotCar("This isn't an image file");
            return;
        }

        // Show preview immediately
        const previewUrl = URL.createObjectURL(file);
        imagePreview.innerHTML = `<img src="${previewUrl}" alt="Upload preview">`;
    });
});