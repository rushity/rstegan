// Function to update file name display
function updateFileName(inputId, labelId) {
    const input = document.getElementById(inputId);
    const label = document.getElementById(labelId);
    if (input.files.length > 0) {
        label.textContent = input.files[0].name;
    } else {
        label.textContent = "Choose File";
    }
}

// Function to encode image
function encodeImage() {
    const fileInput = document.getElementById('encodeImage');
    const textInput = document.getElementById('text');

    if (fileInput.files.length === 0 || !textInput.value) {
        alert('Please select an image and enter text to encode.');
        return;
    }

    const formData = new FormData();
    formData.append('image', fileInput.files[0]);
    formData.append('text', textInput.value);

    fetch('/encode', {
        method: 'POST',
        body: formData
    })
    .then(response => response.blob())
    .then(blob => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'encoded_image.png';
        document.body.appendChild(a);
        a.click();
        URL.revokeObjectURL(url);
    })
    .catch(error => console.error('Error:', error));
}

// Function to decode image
function decodeImage() {
    const fileInput = document.getElementById('decodeImage');
    if (fileInput.files.length === 0) {
        alert('Please select an image to decode.');
        return;
    }

    const formData = new FormData();
    formData.append('image', fileInput.files[0]);

    fetch('/decode', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(text => {
        document.getElementById('decodedMessage').textContent = "Decoded Message: " + text;
    })
    .catch(error => console.error('Error:', error));
}
