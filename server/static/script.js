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
}

// File input change handler
fileInput.addEventListener("change", function (e) {
    handleFile(e.target.files[0]);
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
            showSuccess(data.text);
            console.log("Text extraction successful");
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

function showSuccess(text) {
    output.textContent = text;
    output.className = "has-content";
    output.style.display = "block";
    outputPlaceholder.style.display = "none";
    copyBtn.style.display = "inline-flex";
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
}

function hideOutput() {
    output.style.display = "none";
    outputPlaceholder.style.display = "flex";
    copyBtn.style.display = "none";
}

// Initialize
console.log("SnapText OCR Tool initialized with Google Material Design");
