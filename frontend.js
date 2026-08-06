const API_URL = "/score";   // same origin by FastAPI

document.getElementById("generateBtn").addEventListener("click", generateCard);
document.getElementById("headshotInput").addEventListener("change", openCropModal);

//cropper js for headshot resizing
const cropModal = document.getElementById("cropModal");
const cropViewport = document.getElementById("cropViewport");
const cropImage = document.getElementById("cropImage");
const headshotPreview = document.getElementById("headshotPreview");

let cropper = null;
let objectUrl = null;
let zoomSmoothingTimeout = null;

//make it smoother
function smoothZoomOnWheel() {
    const canvasEl = cropViewport.querySelector(".cropper-canvas");
    if (!canvasEl) return;
    canvasEl.classList.add("cropper-smooth-zoom");
    clearTimeout(zoomSmoothingTimeout);
    zoomSmoothingTimeout = setTimeout(() => canvasEl.classList.remove("cropper-smooth-zoom"), 150);
}

function openCropModal() {
    const file = document.getElementById("headshotInput").files[0];
    if (!file) return;

    if (objectUrl) URL.revokeObjectURL(objectUrl);
    objectUrl = URL.createObjectURL(file);
    cropImage.src = objectUrl;
    cropModal.style.display = "flex";

    cropImage.onload = () => {
        if (cropper) cropper.destroy();
        cropper = new Cropper(cropImage, {
            aspectRatio: 1,
            viewMode: 1,
            dragMode: "move",
            background: false,
            guides: false,
            center: false,
            highlight: false,
            autoCropArea: 1,
            wheelZoomRatio: 0.05,
        });
        cropViewport.addEventListener("wheel", smoothZoomOnWheel, { passive: true });
    };
}

function closeCropModal() {
    if (cropper) {
        cropper.destroy();
        cropper = null;
    }
    cropViewport.removeEventListener("wheel", smoothZoomOnWheel);
    clearTimeout(zoomSmoothingTimeout);
    cropModal.style.display = "none";
    document.getElementById("headshotInput").value = "";
}
document.getElementById("cropCancelBtn").addEventListener("click", closeCropModal);

document.getElementById("cropConfirmBtn").addEventListener("click", () => {
    if (!cropper) return;
    const canvas = cropper.getCroppedCanvas({ width: 280, height: 280 });
    headshotPreview.src = canvas.toDataURL("image/png");
    headshotPreview.style.display = "block";
    closeCropModal();
});


async function generateCard() {
    const fileInput = document.getElementById("pdfInput");
    const pdfFile = fileInput.files[0];

    if (!pdfFile) {
        console.log("No file selected");
        return;
    }

    const formData = new FormData();
    formData.append("file", pdfFile);

    //sending
    try {
        console.log("Sending resume to backend...");
        const response = await fetch(API_URL, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            const err = await response.json();
            console.error("Backend error:", err.detail);
            return;
        }

        const card = await response.json();
        console.log("Card data received:", card);

    } catch (error) {
        console.error("Request failed:", error);
    }
}