// DOM elements
const uploadForm = document.getElementById("uploadForm");
const fileInput = document.getElementById("fileInput");
const submitBtn = document.getElementById("submitBtn");
const fileName = document.getElementById("fileName");
const output = document.getElementById("output");
const loading = document.getElementById("loading");
const dragDropArea = document.getElementById("dragDropArea");
const outputPlaceholder = document.getElementById("outputPlaceholder");
const copyBtn = document.getElementById("copyBtn");
const imagePreviewSection = document.getElementById("imagePreviewSection");
const imagePreview = document.getElementById("imagePreview");
const imageInfo = document.getElementById("imageInfo");
const removeImageBtn = document.getElementById("removeImageBtn");

// File handling
function handleFile(file) {
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
        showError("Please select an image file.");
        return;
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
        showError("File size must be less than 10MB.");
        return;
    }

    fileName.textContent = `Selected: ${file.name}`;
    submitBtn.disabled = false;
    clearOutput();

    // Show image preview
    showImagePreview(file);
}

// Image preview functionality
function showImagePreview(file) {
    const reader = new FileReader();

    reader.onload = function (e) {
        imagePreview.src = e.target.result;
        imagePreviewSection.style.display = "block";

        // Show image information
        showImageInfo(file);

        // Hide drag-drop area to save space
        dragDropArea.style.display = "none";
    };

    reader.readAsDataURL(file);
}

function showImageInfo(file) {
    const fileSizeKB = (file.size / 1024).toFixed(1);
    const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
    const displaySize = file.size > 1024 * 1024 ? `${fileSizeMB} MB` : `${fileSizeKB} KB`;

    // Create image to get dimensions
    const img = new Image();
    img.onload = function () {
        imageInfo.innerHTML = `
            <div class="image-info-item">
                <span class="image-info-label">File name:</span>
                <span class="image-info-value">${file.name}</span>
            </div>
            <div class="image-info-item">
                <span class="image-info-label">File size:</span>
                <span class="image-info-value">${displaySize}</span>
            </div>
            <div class="image-info-item">
                <span class="image-info-label">Dimensions:</span>
                <span class="image-info-value">${this.width} × ${this.height}px</span>
            </div>
            <div class="image-info-item">
                <span class="image-info-label">Type:</span>
                <span class="image-info-value">${file.type}</span>
            </div>
        `;
    };

    const reader = new FileReader();
    reader.onload = function (e) {
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}

function hideImagePreview() {
    imagePreviewSection.style.display = "none";
    dragDropArea.style.display = "block";
    imagePreview.src = "";
    imageInfo.innerHTML = "";
}

// File input change handler
fileInput.addEventListener("change", function (e) {
    handleFile(e.target.files[0]);
});

// Remove image button handler
removeImageBtn.addEventListener("click", function () {
    // Clear file input
    fileInput.value = "";

    // Hide image preview
    hideImagePreview();

    // Reset UI state
    fileName.textContent = "";
    submitBtn.disabled = true;
    clearOutput();

    console.log("Image removed");
});

// Drag and drop handlers
dragDropArea.addEventListener("dragover", function (e) {
    e.preventDefault();
    dragDropArea.classList.add("dragover");
});

dragDropArea.addEventListener("dragleave", function (e) {
    e.preventDefault();
    dragDropArea.classList.remove("dragover");
});

dragDropArea.addEventListener("drop", function (e) {
    e.preventDefault();
    dragDropArea.classList.remove("dragover");

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        handleFile(files[0]);
    }
});

// Form submission
uploadForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    if (!fileInput.files.length) {
        showError("Please select a file.");
        return;
    }

    const file = fileInput.files[0];
    showLoading(true);
    clearOutput();

    try {
        const formData = new FormData();
        formData.append("file", file);

        console.log("Uploading file:", file.name);

        const res = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        if (res.ok && data.text) {
            showSuccess(data.text, data.confidence);
            console.log("Text extraction successful");
            console.log("OCR confidence:", data.confidence);
        } else {
            showError(data.error || "Failed to extract text");
            console.error("Extraction failed:", data.error);
        }
    } catch (error) {
        showError("Network error: " + error.message);
        console.error("Upload error:", error);
    } finally {
        showLoading(false);
    }
});

// Copy functionality
copyBtn.addEventListener("click", async function () {
    const text = output.textContent;
    if (!text) return;

    try {
        await navigator.clipboard.writeText(text);

        // Visual feedback
        const originalContent = copyBtn.innerHTML;
        copyBtn.innerHTML = '<span class="material-icon">check</span>Copied!';
        copyBtn.classList.add("copied");

        setTimeout(() => {
            copyBtn.innerHTML = originalContent;
            copyBtn.classList.remove("copied");
        }, 2000);

        console.log("Text copied to clipboard");
    } catch (err) {
        console.error("Failed to copy text:", err);

        // Fallback for older browsers
        const textArea = document.createElement("textarea");
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand("copy");
        document.body.removeChild(textArea);

        // Visual feedback for fallback
        const originalContent = copyBtn.innerHTML;
        copyBtn.innerHTML = '<span class="material-icon">check</span>Copied!';
        copyBtn.classList.add("copied");

        setTimeout(() => {
            copyBtn.innerHTML = originalContent;
            copyBtn.classList.remove("copied");
        }, 2000);
    }
});

// UI helper functions
function showLoading(show) {
    loading.style.display = show ? "block" : "none";
    submitBtn.disabled = show;
    if (show) {
        hideOutput();
    }
}

function showSuccess(text, confidence = null) {
    output.textContent = text;
    output.className = "has-content";
    output.style.display = "block";
    outputPlaceholder.style.display = "none";
    copyBtn.style.display = "inline-flex";

    // Show confidence information if available
    if (confidence && !confidence.error) {
        showConfidenceInfo(confidence);
    }
}

function showConfidenceInfo(confidence) {
    // Create or update confidence display
    let confidenceDiv = document.getElementById("confidenceInfo");
    if (!confidenceDiv) {
        confidenceDiv = document.createElement("div");
        confidenceDiv.id = "confidenceInfo";
        confidenceDiv.className = "confidence-info";

        // Insert after output header
        const outputHeader = document.querySelector(".output-header");
        outputHeader.parentNode.insertBefore(confidenceDiv, outputHeader.nextSibling);
    }

    const avgConfidence = Math.round(confidence.average_confidence || 0);
    const confidenceClass = avgConfidence >= 80 ? "high" : avgConfidence >= 60 ? "medium" : "low";

    confidenceDiv.innerHTML = `
        <div class="confidence-header">
            <span class="confidence-label">OCR Quality:</span>
            <span class="confidence-score confidence-${confidenceClass}">${avgConfidence}%</span>
        </div>
        <div class="confidence-details">
            <span>Words detected: ${confidence.word_count || 0}</span>
            ${confidence.low_confidence_words ? `<span>Low confidence words: ${confidence.low_confidence_words}</span>` : ''}
        </div>
    `;

    confidenceDiv.style.display = "block";
}

function showError(message) {
    output.textContent = message;
    output.className = "has-error";
    output.style.display = "block";
    outputPlaceholder.style.display = "none";
    copyBtn.style.display = "none";
}

function clearOutput() {
    output.textContent = "";
    output.className = "";
    hideOutput();
    hideConfidenceInfo();
}

function hideOutput() {
    output.style.display = "none";
    outputPlaceholder.style.display = "flex";
    copyBtn.style.display = "none";
}

function hideConfidenceInfo() {
    const confidenceDiv = document.getElementById("confidenceInfo");
    if (confidenceDiv) {
        confidenceDiv.style.display = "none";
    }
}

function resetForm() {
    fileInput.value = "";
    fileName.textContent = "";
    submitBtn.disabled = true;
    hideImagePreview();
    clearOutput();
}

// Initialize
console.log("SnapText OCR Tool initialized with Google Material Design");
