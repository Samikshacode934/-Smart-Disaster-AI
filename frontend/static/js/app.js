// Initialize Map
const map = L.map('map').setView([22.9734, 78.6569], 5);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// Layer Control
const floodLayer = L.layerGroup().addTo(map);
const fireLayer = L.layerGroup().addTo(map);

// Load Disasters from Flask API
async function loadDisasters() {
    const response = await fetch('/api/disasters');
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

    const disasters = await response.json();
     console.log("Loaded disasters:", disasters);  // Debug
    
    // Clear existing markers
        floodLayer.clearLayers();
        fireLayer.clearLayers();
        
        if (disasters.length === 0) {
            console.warn("No disasters found in database");
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
            <small>Detected: ${new Date(d.timestamp).toLocaleString()}</small>
             ${d.image_url ? `<br><a href="${d.image_url}" target="_blank">View Image</a>` : ''}
        `);
        
        d.type === 'flood' ? marker.addTo(floodLayer) : marker.addTo(fireLayer);
    });
}

// Toggle Layers
document.getElementById('flood-toggle').addEventListener('click', function() {
    map.hasLayer(floodLayer) ? map.removeLayer(floodLayer) : map.addLayer(floodLayer);
    this.classList.toggle('active');
});

document.getElementById('fire-toggle').addEventListener('click', function() {
    map.hasLayer(fireLayer) ? map.removeLayer(fireLayer) : map.addLayer(fireLayer);
    this.classList.toggle('active');
});

// Analyze Image
document.getElementById('analyze-btn').addEventListener('click', async function() {
    const url = document.getElementById('image-url').value;
    if (!url) return alert('Please enter an image URL');
    
    try {
        const response = await fetch('/detect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image_url: url })
        });
        
        const result = await response.json();
        console.log("Full response:", result);  // Debug
        
        let resultsHTML = `
            <p><strong>Type:</strong> ${result.prediction?.type || 'N/A'}</p>
            <p><strong>Confidence:</strong> ${result.prediction?.confidence ? (result.prediction.confidence * 100).toFixed(1)+'%' : 'N/A'}</p>
        `;
        
        if (result.inserted_id) {
            resultsHTML += `<p><strong>MongoDB ID:</strong> ${result.inserted_id}</p>`;
        }
        
        if (result.error) {
            resultsHTML += `<p class="text-danger">Error: ${result.error}</p>`;
        }
        
        document.getElementById('results').innerHTML = resultsHTML;
        
        loadDisasters(); // Refresh map
    } catch (error) {
        console.error("Request failed:", error);
        document.getElementById('results').innerHTML = `
            <p class="text-danger">Request failed: ${error.message}</p>
        `;
    }
});

db.disasters.insertOne({
  type: "test",
  location: { type: "Point", coordinates: [77.2, 28.6] },
  timestamp: new Date(),
  confidence: 0.95,
  image_url: "https://example.com/test.jpg"
})

// Initial Load
loadDisasters();