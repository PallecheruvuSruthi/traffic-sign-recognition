/**
 * Intelligent Traffic Sign Recognition - Frontend Logic
 * Vanilla JavaScript implementation for file upload, camera capture,
 * validation, fetch API communication, and dynamic UI updates.
 */

(function () {
  'use strict';

  // State Management
  const state = {
    selectedFile: null,
    capturedDataUrl: null,
    imageSource: null, // 'upload' or 'camera'
    cameraStream: null,
    isSubmitting: false,
    modelAvailable: false,
    catalogData: [],
  };

  // DOM Elements
  const elements = {
    // Header & Status
    modelStatusIndicator: document.getElementById('model-status-indicator'),
    modelStatusText: document.getElementById('model-status-text'),
    btnOpenCatalog: document.getElementById('btn-open-catalog'),

    // Alerts
    globalAlert: document.getElementById('global-alert'),
    alertTitle: document.getElementById('alert-title'),
    alertMessage: document.getElementById('alert-message'),
    btnCloseAlert: document.getElementById('btn-close-alert'),

    // Tabs
    tabUpload: document.getElementById('tab-upload'),
    tabCamera: document.getElementById('tab-camera'),
    paneUpload: document.getElementById('pane-upload'),
    paneCamera: document.getElementById('pane-camera'),

    // Upload
    dropZone: document.getElementById('drop-zone'),
    fileInput: document.getElementById('file-input'),
    btnBrowseTrigger: document.getElementById('btn-browse-trigger'),

    // Camera
    cameraPrompt: document.getElementById('camera-prompt'),
    cameraFeedContainer: document.getElementById('camera-feed-container'),
    cameraVideo: document.getElementById('camera-video'),
    cameraCanvas: document.getElementById('camera-canvas'),
    btnOpenCamera: document.getElementById('btn-open-camera'),
    btnCaptureImage: document.getElementById('btn-capture-image'),
    btnStopCamera: document.getElementById('btn-stop-camera'),

    // Preview
    previewSection: document.getElementById('preview-section'),
    imagePreview: document.getElementById('image-preview'),
    previewFilename: document.getElementById('preview-filename'),
    previewDimensions: document.getElementById('preview-dimensions'),
    previewSize: document.getElementById('preview-size'),
    previewSource: document.getElementById('preview-source'),
    btnClearPreview: document.getElementById('btn-clear-preview'),

    // Actions
    btnRecognize: document.getElementById('btn-recognize'),
    btnReset: document.getElementById('btn-reset'),

    // Results Column
    resultPlaceholder: document.getElementById('result-placeholder'),
    loadingState: document.getElementById('loading-state'),
    modelUnavailableCard: document.getElementById('model-unavailable-card'),
    modelUnavailableMessage: document.getElementById('model-unavailable-message'),
    resultDisplay: document.getElementById('result-display'),

    // Result Fields
    resClassId: document.getElementById('res-class-id'),
    resCategory: document.getElementById('res-category'),
    resSignName: document.getElementById('res-sign-name'),
    resConfidencePct: document.getElementById('res-confidence-pct'),
    confidenceBar: document.getElementById('confidence-bar'),
    resUncertaintyBanner: document.getElementById('res-uncertainty-banner'),
    resUncertaintyText: document.getElementById('res-uncertainty-text'),
    resDescription: document.getElementById('res-description'),
    resAction: document.getElementById('res-action'),
    topCandidatesList: document.getElementById('top-candidates-list'),
    predictionTimestamp: document.getElementById('prediction-timestamp'),

    // Modal
    catalogModal: document.getElementById('catalog-modal'),
    btnCloseCatalog: document.getElementById('btn-close-catalog'),
    btnModalDismiss: document.getElementById('btn-modal-dismiss'),
    catalogSearch: document.getElementById('catalog-search'),
    catalogGrid: document.getElementById('catalog-grid'),
  };

  // Supported Extensions and Limits
  const ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.ppm'];
  const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024; // 10 MB

  // =========================================================================
  // Initialization
  // =========================================================================
  function init() {
    bindEvents();
    checkBackendHealth();
    preloadCatalog();
  }

  // =========================================================================
  // Event Bindings
  // =========================================================================
  function bindEvents() {
    // Tabs
    elements.tabUpload.addEventListener('click', () => switchTab('upload'));
    elements.tabCamera.addEventListener('click', () => switchTab('camera'));

    // File Upload
    elements.btnBrowseTrigger.addEventListener('click', (e) => {
      e.stopPropagation();
      elements.fileInput.click();
    });
    elements.dropZone.addEventListener('click', () => elements.fileInput.click());
    elements.fileInput.addEventListener('change', handleFileInputChange);

    // Drag and Drop
    elements.dropZone.addEventListener('dragover', handleDragOver);
    elements.dropZone.addEventListener('dragleave', handleDragLeave);
    elements.dropZone.addEventListener('drop', handleDrop);

    // Camera
    elements.btnOpenCamera.addEventListener('click', startCamera);
    elements.btnCaptureImage.addEventListener('click', captureFrame);
    elements.btnStopCamera.addEventListener('click', stopCamera);

    // Preview
    elements.btnClearPreview.addEventListener('click', clearImageSelection);

    // Main Actions
    elements.btnRecognize.addEventListener('click', handleRecognize);
    elements.btnReset.addEventListener('click', handleResetAll);

    // Alert Dismiss
    elements.btnCloseAlert.addEventListener('click', hideAlert);

    // Catalog Modal
    elements.btnOpenCatalog.addEventListener('click', openCatalog);
    elements.btnCloseCatalog.addEventListener('click', closeCatalog);
    elements.btnModalDismiss.addEventListener('click', closeCatalog);
    elements.catalogSearch.addEventListener('input', filterCatalog);
    elements.catalogModal.addEventListener('click', (e) => {
      if (e.target === elements.catalogModal) closeCatalog();
    });

    // Cleanup on window unload
    window.addEventListener('beforeunload', stopCamera);
  }

  // =========================================================================
  // Tab Management
  // =========================================================================
  function switchTab(tabName) {
    if (tabName === 'upload') {
      elements.tabUpload.classList.add('active');
      elements.tabUpload.setAttribute('aria-selected', 'true');
      elements.tabCamera.classList.remove('active');
      elements.tabCamera.setAttribute('aria-selected', 'false');

      elements.paneUpload.classList.remove('hidden');
      elements.paneCamera.classList.add('hidden');

      // Stop camera if running
      stopCamera();
    } else {
      elements.tabCamera.classList.add('active');
      elements.tabCamera.setAttribute('aria-selected', 'true');
      elements.tabUpload.classList.remove('active');
      elements.tabUpload.setAttribute('aria-selected', 'false');

      elements.paneCamera.classList.remove('hidden');
      elements.paneUpload.classList.add('hidden');
    }
  }

  // =========================================================================
  // Drag & Drop / File Input Handling
  // =========================================================================
  function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    elements.dropZone.classList.add('dragover');
  }

  function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    elements.dropZone.classList.remove('dragover');
  }

  function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    elements.dropZone.classList.remove('dragover');

    const dt = e.dataTransfer;
    if (dt && dt.files && dt.files.length > 0) {
      processSelectedFile(dt.files[0]);
    }
  }

  function handleFileInputChange(e) {
    if (e.target.files && e.target.files.length > 0) {
      processSelectedFile(e.target.files[0]);
    }
  }

  function processSelectedFile(file) {
    hideAlert();

    // 1. Validate file extension
    const name = file.name.toLowerCase();
    const hasValidExt = ALLOWED_EXTENSIONS.some((ext) => name.endsWith(ext));
    if (!hasValidExt) {
      showAlert(
        'Unsupported File Format',
        `File "${file.name}" is not supported. Please select a JPG, PNG, WebP, or PPM image.`,
        'danger'
      );
      elements.fileInput.value = '';
      return;
    }

    // 2. Validate file size
    if (file.size > MAX_FILE_SIZE_BYTES) {
      const mb = (file.size / (1024 * 1024)).toFixed(1);
      showAlert(
        'File Too Large',
        `The selected file is ${mb} MB, which exceeds the 10 MB maximum limit.`,
        'danger'
      );
      elements.fileInput.value = '';
      return;
    }

    if (file.size === 0) {
      showAlert('Empty File', 'The selected file is 0 bytes and cannot be decoded.', 'danger');
      elements.fileInput.value = '';
      return;
    }

    // 3. Read and verify image with FileReader
    const reader = new FileReader();
    reader.onload = function (e) {
      const dataUrl = e.target.result;
      const testImg = new Image();
      testImg.onload = function () {
        // Image successfully decoded
        state.selectedFile = file;
        state.capturedDataUrl = null;
        state.imageSource = 'upload';

        displayImagePreview(dataUrl, file.name, file.size, testImg.naturalWidth, testImg.naturalHeight, 'Uploaded File');
        clearResultsArea();
      };
      testImg.onerror = function () {
        showAlert(
          'Corrupted Image',
          'Failed to decode image data. The file appears to be damaged or corrupted.',
          'danger'
        );
        clearImageSelection();
      };
      testImg.src = dataUrl;
    };
    reader.onerror = function () {
      showAlert('File Read Error', 'Unable to read the chosen file from your system.', 'danger');
    };
    reader.readAsDataURL(file);
  }

  // =========================================================================
  // Camera Handling (navigator.mediaDevices.getUserMedia)
  // =========================================================================
  async function startCamera() {
    hideAlert();

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      showAlert(
        'Camera API Unsupported',
        'Your browser does not support the MediaDevices camera API, or you are running in an insecure context. Camera access requires localhost or HTTPS.',
        'warning'
      );
      return;
    }

    try {
      const constraints = {
        video: {
          facingMode: 'environment', // Prefer rear/environment camera on phones
          width: { ideal: 640 },
          height: { ideal: 480 },
        },
        audio: false,
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      state.cameraStream = stream;
      elements.cameraVideo.srcObject = stream;
      await elements.cameraVideo.play();

      elements.cameraPrompt.classList.add('hidden');
      elements.cameraFeedContainer.classList.remove('hidden');
    } catch (err) {
      let friendlyMessage = 'Unable to access the camera: ' + err.message;
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        friendlyMessage =
          'Camera permission was denied. Please allow camera permissions in your browser address bar and try again.';
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        friendlyMessage = 'No camera hardware was detected on your system.';
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        friendlyMessage =
          'The camera is currently in use by another application or tab. Please close other camera programs and try again.';
      }
      showAlert('Camera Access Notice', friendlyMessage, 'warning');
      stopCamera();
    }
  }

  function captureFrame() {
    if (!state.cameraStream || !elements.cameraVideo.videoWidth) {
      showAlert('Capture Failed', 'Camera is not ready yet. Please wait for feed to appear.', 'warning');
      return;
    }

    const video = elements.cameraVideo;
    const canvas = elements.cameraCanvas;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const dataUrl = canvas.toDataURL('image/jpeg', 0.92);

    state.selectedFile = null;
    state.capturedDataUrl = dataUrl;
    state.imageSource = 'camera';

    // Calculate approx size in bytes from base64
    const approxBytes = Math.round((dataUrl.length * 3) / 4);
    displayImagePreview(dataUrl, 'camera_capture.jpg', approxBytes, canvas.width, canvas.height, 'Live Camera Capture');

    clearResultsArea();
    showAlert('Image Captured', 'Frame captured from live camera. Ready for recognition.', 'success');
  }

  function stopCamera() {
    if (state.cameraStream) {
      state.cameraStream.getTracks().forEach((track) => track.stop());
      state.cameraStream = null;
    }
    if (elements.cameraVideo) {
      elements.cameraVideo.srcObject = null;
    }
    elements.cameraFeedContainer.classList.add('hidden');
    elements.cameraPrompt.classList.remove('hidden');
  }

  // =========================================================================
  // Image Preview & Reset
  // =========================================================================
  function displayImagePreview(src, filename, sizeBytes, width, height, sourceLabel) {
    elements.imagePreview.src = src;
    elements.previewFilename.textContent = filename;
    elements.previewDimensions.textContent = `${width} × ${height} px`;
    elements.previewSize.textContent = formatBytes(sizeBytes);
    elements.previewSource.textContent = sourceLabel;

    elements.previewSection.classList.remove('hidden');
    elements.btnRecognize.disabled = false;
  }

  function clearImageSelection() {
    state.selectedFile = null;
    state.capturedDataUrl = null;
    state.imageSource = null;
    elements.fileInput.value = '';
    elements.imagePreview.src = '';
    elements.previewSection.classList.add('hidden');
    elements.btnRecognize.disabled = true;
  }

  function clearResultsArea() {
    elements.resultPlaceholder.classList.remove('hidden');
    elements.loadingState.classList.add('hidden');
    elements.modelUnavailableCard.classList.add('hidden');
    elements.resultDisplay.classList.add('hidden');
    elements.predictionTimestamp.textContent = '';
  }

  function handleResetAll() {
    stopCamera();
    clearImageSelection();
    clearResultsArea();
    hideAlert();
    switchTab('upload');
  }

  // =========================================================================
  // Backend Communication: /predict
  // =========================================================================
  async function handleRecognize() {
    // Prevent duplicate clicks
    if (state.isSubmitting) return;
    if (!state.selectedFile && !state.capturedDataUrl) {
      showAlert('No Image Selected', 'Please upload or capture an image before clicking recognize.', 'warning');
      return;
    }

    hideAlert();
    setSubmittingState(true);

    // Switch view to loading
    elements.resultPlaceholder.classList.add('hidden');
    elements.modelUnavailableCard.classList.add('hidden');
    elements.resultDisplay.classList.add('hidden');
    elements.loadingState.classList.remove('hidden');

    try {
      let response;

      if (state.selectedFile) {
        // Upload via FormData
        const formData = new FormData();
        formData.append('image', state.selectedFile);

        response = await fetch('/predict', {
          method: 'POST',
          body: formData,
        });
      } else if (state.capturedDataUrl) {
        // Captured from camera via JSON base64
        response = await fetch('/predict', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ image: state.capturedDataUrl }),
        });
      }

      const data = await response.json().catch(() => null);

      if (!response.ok || !data || data.success === false) {
        // Handle Model Unavailable (503 or model_available == false)
        if (response.status === 503 || (data && data.model_available === false)) {
          showModelUnavailable(
            data && data.error
              ? data.error
              : 'Traffic sign recognition is not available yet because a compatible trained model has not been installed. Please add a trained model and try again.'
          );
        } else {
          // Validation or server error
          const msg = data && data.error ? data.error : `Server responded with status ${response.status}.`;
          showAlert('Recognition Notice', msg, 'danger');
          elements.loadingState.classList.add('hidden');
          elements.resultPlaceholder.classList.remove('hidden');
        }
        return;
      }

      // Success: Render prediction results
      renderPrediction(data);
    } catch (err) {
      console.error('Fetch error:', err);
      showAlert(
        'Connection Error',
        'Failed to connect to the Flask server. Please verify the backend is running at http://127.0.0.1:5000.',
        'danger'
      );
      elements.loadingState.classList.add('hidden');
      elements.resultPlaceholder.classList.remove('hidden');
    } finally {
      setSubmittingState(false);
    }
  }

  function renderPrediction(data) {
    elements.loadingState.classList.add('hidden');
    elements.resultPlaceholder.classList.add('hidden');
    elements.modelUnavailableCard.classList.add('hidden');

    const isRecognized = data.sign_detected !== false && !data.is_uncertain;

    // Badges & Title
    if (isRecognized) {
      elements.resClassId.textContent = `Class #${data.class_id}`;
      elements.resClassId.className = 'badge badge-accent';
      elements.resCategory.textContent = data.category || 'Standard';
      elements.resSignName.textContent = data.name;
      elements.resSignName.style.color = 'var(--text-main)';
    } else {
      elements.resClassId.textContent = 'Unrecognized / Non-Sign';
      elements.resClassId.className = 'badge badge-warning';
      elements.resCategory.textContent = data.display_category || 'Ambiguous / Non-Sign';
      elements.resSignName.textContent = data.display_title || 'No Recognizable Traffic Sign Detected';
      elements.resSignName.style.color = '#b45309';
    }

    // Confidence
    const pct = data.confidence_pct || (data.confidence * 100).toFixed(1);
    elements.resConfidencePct.textContent = `${pct}%`;
    elements.confidenceBar.style.width = `${Math.min(100, Math.max(0, pct))}%`;

    // Dynamic bar color depending on recognition and confidence
    if (isRecognized && pct >= 80) {
      elements.confidenceBar.style.background = 'var(--color-success)';
      elements.resConfidencePct.style.color = 'var(--color-success)';
    } else if (pct >= 50) {
      elements.confidenceBar.style.background = 'var(--color-warning)';
      elements.resConfidencePct.style.color = 'var(--color-warning)';
    } else {
      elements.confidenceBar.style.background = 'var(--color-danger)';
      elements.resConfidencePct.style.color = 'var(--color-danger)';
    }

    // Uncertainty Warning
    if (data.is_uncertain && data.uncertainty_message) {
      elements.resUncertaintyText.textContent = data.uncertainty_message;
      elements.resUncertaintyBanner.classList.remove('hidden');
    } else {
      elements.resUncertaintyBanner.classList.add('hidden');
    }

    // Descriptions & Actions
    elements.resDescription.textContent = data.description || 'No detailed description available.';
    elements.resAction.textContent = data.action || 'Comply with standard roadway signage regulations.';

    // Top 3 Candidates
    elements.topCandidatesList.innerHTML = '';
    if (data.top_candidates && data.top_candidates.length > 0) {
      data.top_candidates.forEach((cand) => {
        const item = document.createElement('div');
        item.className = 'candidate-item';
        item.innerHTML = `
          <div class="candidate-info">
            <span class="candidate-rank">${cand.rank}.</span>
            <span class="candidate-name">${cand.name}</span>
          </div>
          <span class="candidate-prob">${cand.confidence_pct}%</span>
        `;
        elements.topCandidatesList.appendChild(item);
      });
    }

    // Timestamp
    const now = new Date();
    elements.predictionTimestamp.textContent = `Analyzed at ${now.toLocaleTimeString()}`;

    // Reveal result card
    elements.resultDisplay.classList.remove('hidden');
  }

  function showModelUnavailable(message) {
    elements.loadingState.classList.add('hidden');
    elements.resultPlaceholder.classList.add('hidden');
    elements.resultDisplay.classList.add('hidden');

    elements.modelUnavailableMessage.textContent = message;
    elements.modelUnavailableCard.classList.remove('hidden');
  }

  function setSubmittingState(isSubmitting) {
    state.isSubmitting = isSubmitting;
    elements.btnRecognize.disabled = isSubmitting;
    const spinner = elements.btnRecognize.querySelector('.btn-spinner');
    const label = elements.btnRecognize.querySelector('.btn-text-label');

    if (isSubmitting) {
      spinner.classList.remove('hidden');
      label.textContent = 'Processing...';
    } else {
      spinner.classList.add('hidden');
      label.textContent = 'Recognize Traffic Sign';
    }
  }

  // =========================================================================
  // Health Check & Catalog
  // =========================================================================
  async function checkBackendHealth() {
    try {
      const res = await fetch('/health');
      if (!res.ok) throw new Error(`Status ${res.status}`);
      const data = await res.json();

      const modelStatus = data.model_status || {};
      state.modelAvailable = !!modelStatus.model_available;

      if (state.modelAvailable) {
        elements.modelStatusIndicator.className = 'status-pill status-success';
        elements.modelStatusText.textContent = 'Model Ready (CNN Loaded)';
      } else {
        elements.modelStatusIndicator.className = 'status-pill status-warning';
        elements.modelStatusText.textContent = 'No Model Installed';
      }
    } catch (err) {
      elements.modelStatusIndicator.className = 'status-pill status-neutral';
      elements.modelStatusText.textContent = 'Backend Offline';
    }
  }

  async function preloadCatalog() {
    try {
      const res = await fetch('/api/classes');
      if (!res.ok) return;
      const data = await res.json();
      state.catalogData = data.classes || [];
      renderCatalogGrid(state.catalogData);
    } catch (e) {
      console.warn('Could not preload catalog:', e);
    }
  }

  function renderCatalogGrid(classes) {
    elements.catalogGrid.innerHTML = '';
    if (classes.length === 0) {
      elements.catalogGrid.innerHTML = '<p class="catalog-empty">No matching signs found.</p>';
      return;
    }

    classes.forEach((c) => {
      const card = document.createElement('div');
      card.className = 'catalog-item';
      card.innerHTML = `
        <div class="catalog-item-header">
          <span class="catalog-cid">#${c.id}</span>
          <span class="catalog-cat">${c.category}</span>
        </div>
        <h4 class="catalog-name">${c.name}</h4>
        <p class="catalog-desc">${c.description}</p>
      `;
      elements.catalogGrid.appendChild(card);
    });
  }

  function filterCatalog() {
    const q = elements.catalogSearch.value.trim().toLowerCase();
    if (!q) {
      renderCatalogGrid(state.catalogData);
      return;
    }

    const filtered = state.catalogData.filter((item) => {
      return (
        item.name.toLowerCase().includes(q) ||
        String(item.id).includes(q) ||
        item.category.toLowerCase().includes(q) ||
        item.description.toLowerCase().includes(q)
      );
    });
    renderCatalogGrid(filtered);
  }

  function openCatalog() {
    elements.catalogModal.classList.remove('hidden');
    elements.catalogSearch.value = '';
    renderCatalogGrid(state.catalogData);
    elements.catalogSearch.focus();
  }

  function closeCatalog() {
    elements.catalogModal.classList.add('hidden');
  }

  // =========================================================================
  // UI Helpers: Alert Banner & Byte Formatter
  // =========================================================================
  function showAlert(title, message, type = 'danger') {
    elements.alertTitle.textContent = title;
    elements.alertMessage.textContent = message;

    elements.globalAlert.className = `alert-banner alert-${type}`;
    elements.globalAlert.classList.remove('hidden');

    // Auto-scroll into view if offscreen
    elements.globalAlert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function hideAlert() {
    elements.globalAlert.classList.add('hidden');
  }

  function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }

  // Self-execute
  init();
})();
