/**
 * GlobeTrotter - Real-Time Camera Capture Component
 * Supports HTML5 WebRTC live webcam capture, snapshot rendering to canvas,
 * Base64 encoding, retake, front/back camera toggling, and file fallback.
 */

class LiveCameraCapture {
    constructor(options) {
        this.container = typeof options.container === 'string' ? document.querySelector(options.container) : options.container;
        if (!this.container) return;

        this.video = this.container.querySelector('.camera-video');
        this.canvas = this.container.querySelector('.camera-canvas');
        this.previewImg = this.container.querySelector('.camera-preview-img');
        this.hiddenInput = this.container.querySelector('.camera-hidden-input');
        this.fileInput = this.container.querySelector('.camera-file-input');
        
        this.startBtn = this.container.querySelector('.btn-start-camera');
        this.captureBtn = this.container.querySelector('.btn-capture-photo');
        this.retakeBtn = this.container.querySelector('.btn-retake-photo');
        this.switchBtn = this.container.querySelector('.btn-switch-camera');
        this.uploadTabBtn = this.container.querySelector('.btn-tab-upload');
        this.cameraTabBtn = this.container.querySelector('.btn-tab-camera');
        this.statusText = this.container.querySelector('.camera-status-text');

        this.stream = null;
        this.facingMode = 'user'; // 'user' or 'environment'
        this.init();
    }

    init() {
        if (this.startBtn) {
            this.startBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.startCamera();
            });
        }

        if (this.captureBtn) {
            this.captureBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.captureSnapshot();
            });
        }

        if (this.retakeBtn) {
            this.retakeBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.retakeSnapshot();
            });
        }

        if (this.switchBtn) {
            this.switchBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.facingMode = this.facingMode === 'user' ? 'environment' : 'user';
                this.startCamera();
            });
        }

        // Handle tabs if present (Camera vs File Upload)
        if (this.cameraTabBtn && this.uploadTabBtn) {
            this.cameraTabBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.showCameraMode();
            });
            this.uploadTabBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.showUploadMode();
            });
        }

        // When user chooses file from file picker, clear captured base64 data
        if (this.fileInput) {
            this.fileInput.addEventListener('change', (e) => {
                if (this.fileInput.files && this.fileInput.files[0]) {
                    const reader = new FileReader();
                    reader.onload = (event) => {
                        if (this.previewImg) {
                            this.previewImg.src = event.target.result;
                            this.previewImg.style.display = 'block';
                        }
                        if (this.hiddenInput) {
                            this.hiddenInput.value = ''; // clear camera base64 to favor file upload
                        }
                        if (this.video) this.video.style.display = 'none';
                        this.stopCamera();
                    };
                    reader.readAsDataURL(this.fileInput.files[0]);
                }
            });
        }
    }

    async startCamera() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            this.updateStatus('Live camera is not supported on this browser. Please use file upload.', 'error');
            return;
        }

        this.stopCamera();
        this.updateStatus('Starting camera...', 'info');

        try {
            const constraints = {
                audio: false,
                video: {
                    facingMode: this.facingMode,
                    width: { ideal: 640 },
                    height: { ideal: 640 }
                }
            };

            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
            if (this.video) {
                this.video.srcObject = this.stream;
                this.video.style.display = 'block';
                await this.video.play();
            }

            if (this.previewImg) this.previewImg.style.display = 'none';
            if (this.startBtn) this.startBtn.style.display = 'none';
            if (this.captureBtn) this.captureBtn.style.display = 'inline-flex';
            if (this.switchBtn) this.switchBtn.style.display = 'inline-flex';
            if (this.retakeBtn) this.retakeBtn.style.display = 'none';

            this.updateStatus('Camera live! Position yourself and click "Take Photo".', 'success');
        } catch (err) {
            console.error('Camera access error:', err);
            let msg = 'Unable to access camera. Please allow camera permissions.';
            if (err.name === 'NotAllowedError') {
                msg = 'Camera permission denied. Please allow camera in browser address bar.';
            } else if (err.name === 'NotFoundError') {
                msg = 'No camera device detected.';
            }
            this.updateStatus(msg, 'error');
        }
    }

    captureSnapshot() {
        if (!this.video || !this.stream) return;

        const width = this.video.videoWidth || 480;
        const height = this.video.videoHeight || 480;

        if (!this.canvas) {
            this.canvas = document.createElement('canvas');
        }
        this.canvas.width = width;
        this.canvas.height = height;

        const ctx = this.canvas.getContext('2d');
        // Mirror if front camera for natural selfie look
        if (this.facingMode === 'user') {
            ctx.translate(width, 0);
            ctx.scale(-1, 1);
        }
        ctx.drawImage(this.video, 0, 0, width, height);

        // Convert to base64 JPEG
        const dataUrl = this.canvas.toDataURL('image/jpeg', 0.9);

        // Set hidden input value for form submission
        if (this.hiddenInput) {
            this.hiddenInput.value = dataUrl;
        }

        // Show captured image preview
        if (this.previewImg) {
            this.previewImg.src = dataUrl;
            this.previewImg.style.display = 'block';
        }

        // Hide video and switch action buttons
        if (this.video) this.video.style.display = 'none';
        if (this.captureBtn) this.captureBtn.style.display = 'none';
        if (this.switchBtn) this.switchBtn.style.display = 'none';
        if (this.retakeBtn) this.retakeBtn.style.display = 'inline-flex';

        // Clear file input so base64 takes precedence
        if (this.fileInput) {
            this.fileInput.value = '';
        }

        this.stopCamera();
        this.updateStatus('Photo captured successfully!', 'success');

        // Play subtle flash animation
        this.container.classList.add('camera-flash');
        setTimeout(() => this.container.classList.remove('camera-flash'), 300);
    }

    retakeSnapshot() {
        if (this.hiddenInput) this.hiddenInput.value = '';
        if (this.previewImg) this.previewImg.style.display = 'none';
        if (this.retakeBtn) this.retakeBtn.style.display = 'none';
        this.startCamera();
    }

    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        if (this.video) {
            this.video.srcObject = null;
        }
    }

    showCameraMode() {
        if (this.cameraTabBtn) this.cameraTabBtn.classList.add('active');
        if (this.uploadTabBtn) this.uploadTabBtn.classList.remove('active');
        
        const cameraBox = this.container.querySelector('.camera-view-box');
        const uploadBox = this.container.querySelector('.camera-upload-box');
        if (cameraBox) cameraBox.style.display = 'block';
        if (uploadBox) uploadBox.style.display = 'none';
    }

    showUploadMode() {
        this.stopCamera();
        if (this.uploadTabBtn) this.uploadTabBtn.classList.add('active');
        if (this.cameraTabBtn) this.cameraTabBtn.classList.remove('active');
        
        const cameraBox = this.container.querySelector('.camera-view-box');
        const uploadBox = this.container.querySelector('.camera-upload-box');
        if (cameraBox) cameraBox.style.display = 'none';
        if (uploadBox) uploadBox.style.display = 'block';
    }

    updateStatus(msg, type = 'info') {
        if (!this.statusText) return;
        this.statusText.textContent = msg;
        this.statusText.className = `camera-status-text status-${type}`;
    }
}

// Auto-initialize all elements with `data-camera-component`
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-camera-component]').forEach(el => {
        new LiveCameraCapture({ container: el });
    });
});
