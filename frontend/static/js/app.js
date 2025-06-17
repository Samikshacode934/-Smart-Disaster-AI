// Initialize Map
const map = L.map('map').setView([22.9734, 78.6569], 5);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// Layer Control
const floodLayer = L.layerGroup().addTo(map);
const fireLayer = L.layerGroup().addTo(map);

// Load Disasters from Flask API
async function loadDisasters() {
    try {
        const response = await fetch('/api/disasters');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const disasters = await response.json();
        console.log("Loaded disasters:", disasters);  // Debug

        // Clear layers
        floodLayer.clearLayers();
        fireLayer.clearLayers();

        if (!disasters || disasters.length === 0) {
            console.warn("No disasters found");
            return;
        }

        disasters.forEach(d => {
            const marker = L.circleMarker(
                [d.location.coordinates[1], d.location.coordinates[0]],
                {
                    radius: 8,
                    color: d.type === 'flood' ? '#0d6efd' : '#dc3545',
                    fillOpacity: 0.7
                }
            ).bindPopup(`
                <b>${d.type.toUpperCase()}</b><br>
                Confidence: ${(d.confidence * 100).toFixed(1)}%<br>
                <small>${new Date(d.timestamp).toLocaleString()}</small>
                ${d.image_url ? `<br><a href="${d.image_url}" target="_blank">View Image</a>` : ''}
            `);

            d.type === 'flood' ? marker.addTo(floodLayer) : marker.addTo(fireLayer);
        });
    } catch (err) {
        console.error("Failed to load disasters:", err);
    }
}

// Toggle Buttons
document.getElementById('flood-toggle').addEventListener('click', function () {
    map.hasLayer(floodLayer) ? map.removeLayer(floodLayer) : map.addLayer(floodLayer);
    this.classList.toggle('active');
});

document.getElementById('fire-toggle').addEventListener('click', function () {
    map.hasLayer(fireLayer) ? map.removeLayer(fireLayer) : map.addLayer(fireLayer);
    this.classList.toggle('active');
});

// Analyze Button
document.getElementById('analyze-btn').addEventListener('click', async function () {
    const url = document.getElementById('image-url').value.trim();
    const resultsBox = document.getElementById('results');

    if (!url) {
        alert('Please enter an image URL');
        return;
    }

    resultsBox.innerHTML = `<p class="text-muted">Analyzing...</p>`;

    try {
        const response = await fetch('/detect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image_url: url })
        });

        const result = await response.json();
        console.log("Detection response:", result);

        if (result.error) {
            resultsBox.innerHTML = `<p class="text-danger">Error: ${result.error}</p>`;
            return;
        }

        let html = `
            <p><strong>Type:</strong> ${result.prediction?.type || 'N/A'}</p>
            <p><strong>Confidence:</strong> ${result.prediction?.confidence ? (result.prediction.confidence * 100).toFixed(1) + '%' : 'N/A'}</p>
            <img src="${url}" alt="Analyzed Image" class="img-fluid mt-2 rounded shadow-sm"/>
        `;

        if (result.inserted_id) {
            html += `<p class="small text-muted mt-2">MongoDB ID: ${result.inserted_id}</p>`;
        }

        resultsBox.innerHTML = html;

        // Refresh map markers
        loadDisasters();

    } catch (error) {
        console.error("Detection failed:", error);
        resultsBox.innerHTML = `<p class="text-danger">Request failed: ${error.message}</p>`;
    }
});

// Initial Load
loadDisasters();
