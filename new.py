<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YOLOv8 Signature Detection & Verification</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            padding: 40px;
            max-width: 900px;
            width: 100%;
            animation: slideUp 0.6s ease-out;
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
        }

        .header h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .header p {
            color: #666;
            font-size: 1.1em;
        }

        .upload-section {
            margin-bottom: 30px;
        }

        .file-upload {
            position: relative;
            display: inline-block;
            width: 100%;
        }

        .file-input {
            width: 100%;
            padding: 20px;
            border: 3px dashed #667eea;
            border-radius: 15px;
            background: #f8f9ff;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 1.1em;
            color: #667eea;
        }

        .file-input:hover {
            background: #eef1ff;
            border-color: #764ba2;
            transform: translateY(-2px);
        }

        .file-input.dragover {
            background: #e3e8ff;
            border-color: #4f46e5;
        }

        input[type="file"] {
            position: absolute;
            opacity: 0;
            width: 100%;
            height: 100%;
            cursor: pointer;
        }

        .settings {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }

        .setting-group {
            background: #f8f9ff;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #e5e7eb;
        }

        .setting-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #374151;
        }

        .setting-group input, .setting-group select {
            width: 100%;
            padding: 10px;
            border: 2px solid #d1d5db;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s ease;
        }

        .setting-group input:focus, .setting-group select:focus {
            outline: none;
            border-color: #667eea;
        }

        .process-btn {
            width: 100%;
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.2em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 30px;
        }

        .process-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }

        .process-btn:disabled {
            background: #9ca3af;
            cursor: not-allowed;
        }

        .results {
            margin-top: 30px;
        }

        .result-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            border-left: 5px solid #667eea;
            animation: fadeIn 0.4s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }

        .result-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 15px;
        }

        .page-info {
            font-weight: 600;
            color: #374151;
            font-size: 1.1em;
        }

        .status {
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9em;
        }

        .status.detected {
            background: #dcfce7;
            color: #166534;
        }

        .status.not-detected {
            background: #fef2f2;
            color: #991b1b;
        }

        .validation-status {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-top: 10px;
            padding: 15px;
            border-radius: 10px;
            font-weight: 600;
            font-size: 1.1em;
        }

        .validation-status.validated {
            background: linear-gradient(135deg, #059669, #10b981);
            color: white;
            box-shadow: 0 4px 15px rgba(5, 150, 105, 0.3);
        }

        .validation-status.not-validated {
            background: linear-gradient(135deg, #dc2626, #ef4444);
            color: white;
            box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3);
        }

        .validation-status.verifying {
            background: linear-gradient(135deg, #f59e0b, #fbbf24);
            color: white;
        }

        .signature-list {
            margin-top: 15px;
        }

        .signature-item {
            background: #f8f9ff;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border: 1px solid #e5e7eb;
            position: relative;
        }

        .signature-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }

        .signature-info {
            display: flex;
            gap: 20px;
            align-items: center;
        }

        .confidence {
            font-weight: 600;
            color: #667eea;
        }

        .verification-badge {
            padding: 6px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: 600;
        }

        .verification-badge.valid {
            background: #dcfce7;
            color: #166534;
        }

        .verification-badge.invalid {
            background: #fef2f2;
            color: #991b1b;
        }

        .verification-badge.verifying {
            background: #fef3c7;
            color: #92400e;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }

        .verification-score {
            font-size: 0.9em;
            color: #6b7280;
            margin-top: 5px;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: #667eea;
        }

        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #f3f4f6;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .summary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
            text-align: center;
        }

        .summary h3 {
            margin-bottom: 10px;
            font-size: 1.3em;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }

        .stat-item {
            background: rgba(255, 255, 255, 0.2);
            padding: 10px;
            border-radius: 8px;
            text-align: center;
        }

        .stat-number {
            font-size: 1.5em;
            font-weight: bold;
            display: block;
        }

        .final-validation {
            background: white;
            padding: 25px;
            border-radius: 12px;
            margin-top: 20px;
            text-align: center;
            font-size: 1.3em;
            font-weight: 600;
            border: 3px solid;
            animation: finalResult 0.6s ease-out;
        }

        .final-validation.validated {
            border-color: #059669;
            color: #059669;
            background: linear-gradient(135deg, #dcfce7, #f0fdf4);
        }

        .final-validation.not-validated {
            border-color: #dc2626;
            color: #dc2626;
            background: linear-gradient(135deg, #fef2f2, #fef7f7);
        }

        @keyframes finalResult {
            0% {
                transform: scale(0.9);
                opacity: 0;
            }
            50% {
                transform: scale(1.05);
            }
            100% {
                transform: scale(1);
                opacity: 1;
            }
        }

        @media (max-width: 768px) {
            .container {
                padding: 20px;
                margin: 10px;
            }

            .settings {
                grid-template-columns: 1fr;
            }

            .header h1 {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Signature Detection & Verification</h1>
            <p>Upload PDF or Image files to detect and verify signatures</p>
        </div>

        <div class="upload-section">
            <div class="file-upload">
                <div class="file-input" id="fileInput">
                    <input type="file" id="fileUpload" accept=".pdf,.jpg,.jpeg,.png,.bmp,.tiff,.tif" multiple>
                    📁 Click to select files or drag & drop here
                    <br><small>Supports: PDF, JPG, PNG, BMP, TIFF</small>
                </div>
            </div>
        </div>

        <div class="settings">
            <div class="setting-group">
                <label for="confidence">Detection Confidence</label>
                <input type="range" id="confidence" min="0.1" max="1.0" step="0.05" value="0.25">
                <small>Current: <span id="confidenceValue">0.25</span></small>
            </div>
            <div class="setting-group">
                <label for="verification">Verification Threshold</label>
                <input type="range" id="verification" min="0.1" max="1.0" step="0.05" value="0.5">
                <small>Current: <span id="verificationValue">0.5</span></small>
            </div>
            <div class="setting-group">
                <label for="dpi">PDF Resolution (DPI)</label>
                <select id="dpi">
                    <option value="150">150 DPI (Fast)</option>
                    <option value="200" selected>200 DPI (Balanced)</option>
                    <option value="300">300 DPI (High Quality)</option>
                </select>
            </div>
        </div>

        <button class="process-btn" id="processBtn" disabled>
            🔍 Detect & Verify Signatures
        </button>

        <div id="results" class="results"></div>
    </div>

    <script>
        // Mock data for demonstration - replace with actual YOLO and verification integration
        const mockDetectionResults = {
            'contract.pdf': [
                { page: 1, signatures: [{ confidence: 0.856, bbox: [120, 450, 280, 520] }] },
                { page: 2, signatures: [] },
                { page: 3, signatures: [
                    { confidence: 0.723, bbox: [200, 300, 350, 380] },
                    { confidence: 0.445, bbox: [400, 600, 520, 670] }
                ]}
            ],
            'document.jpg': [
                { page: 1, signatures: [{ confidence: 0.912, bbox: [150, 200, 300, 280] }] }
            ],
            'form.pdf': [
                { page: 1, signatures: [] }
            ]
        };

        let selectedFiles = [];
        let isProcessing = false;
        let currentProcessingStep = '';

        // DOM elements
        const fileUpload = document.getElementById('fileUpload');
        const fileInput = document.getElementById('fileInput');
        const processBtn = document.getElementById('processBtn');
        const resultsDiv = document.getElementById('results');
        const confidenceSlider = document.getElementById('confidence');
        const confidenceValue = document.getElementById('confidenceValue');
        const verificationSlider = document.getElementById('verification');
        const verificationValue = document.getElementById('verificationValue');

        // Update slider displays
        confidenceSlider.addEventListener('input', (e) => {
            confidenceValue.textContent = e.target.value;
        });

        verificationSlider.addEventListener('input', (e) => {
            verificationValue.textContent = e.target.value;
        });

        // File upload handling
        fileUpload.addEventListener('change', handleFileSelect);
        fileInput.addEventListener('dragover', handleDragOver);
        fileInput.addEventListener('dragleave', handleDragLeave);
        fileInput.addEventListener('drop', handleFileDrop);

        function handleFileSelect(e) {
            selectedFiles = Array.from(e.target.files);
            updateFileInput();
            updateProcessButton();
        }

        function handleDragOver(e) {
            e.preventDefault();
            fileInput.classList.add('dragover');
        }

        function handleDragLeave(e) {
            e.preventDefault();
            fileInput.classList.remove('dragover');
        }

        function handleFileDrop(e) {
            e.preventDefault();
            fileInput.classList.remove('dragover');
            selectedFiles = Array.from(e.dataTransfer.files);
            updateFileInput();
            updateProcessButton();
        }

        function updateFileInput() {
            if (selectedFiles.length > 0) {
                const fileNames = selectedFiles.map(f => f.name).join(', ');
                fileInput.innerHTML = `
                    <input type="file" id="fileUpload" accept=".pdf,.jpg,.jpeg,.png,.bmp,.tiff,.tif" multiple>
                    ✅ ${selectedFiles.length} file(s) selected
                    <br><small>${fileNames.length > 50 ? fileNames.substring(0, 50) + '...' : fileNames}</small>
                `;
                document.getElementById('fileUpload').addEventListener('change', handleFileSelect);
            }
        }

        function updateProcessButton() {
            processBtn.disabled = selectedFiles.length === 0 || isProcessing;
        }

        // Main processing function
        processBtn.addEventListener('click', processFiles);

        async function processFiles() {
            if (selectedFiles.length === 0) return;

            isProcessing = true;
            updateProcessButton();
            
            const confidence = parseFloat(confidenceSlider.value);
            const verificationThreshold = parseFloat(verificationSlider.value);
            const dpi = parseInt(document.getElementById('dpi').value);
            
            let allResults = [];
            let totalSignatures = 0;
            let validatedSignatures = 0;
            let pagesWithSignatures = 0;
            let totalPages = 0;
            let anySignatureValidated = false;

            // Show initial loading
            showLoadingState('Initializing detection models...');
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Process each file
            for (let i = 0; i < selectedFiles.length; i++) {
                const file = selectedFiles[i];
                const fileName = file.name;
                
                showLoadingState(`Processing ${fileName} (${i + 1}/${selectedFiles.length})`);
                
                // Step 1: Detect signatures
                showLoadingState(`🔍 Detecting signatures in ${fileName}...`);
                const detectionResults = await detectSignatures(fileName, confidence);
                
                // Step 2: Verify each detected signature
                const verifiedResults = [];
                
                for (let pageResult of detectionResults) {
                    totalPages++;
                    
                    if (pageResult.signatures.length > 0) {
                        pagesWithSignatures++;
                        
                        showLoadingState(`✔️ Verifying signatures on page ${pageResult.page}...`);
                        
                        const verifiedSignatures = [];
                        for (let j = 0; j < pageResult.signatures.length; j++) {
                            const signature = pageResult.signatures[j];
                            totalSignatures++;
                            
                            // Call verification model for each signature
                            const verificationResult = await verifySignature(fileName, pageResult.page, j + 1, signature, verificationThreshold);
                            
                            verifiedSignatures.push({
                                ...signature,
                                verified: verificationResult.isValid,
                                verificationScore: verificationResult.score
                            });
                            
                            if (verificationResult.isValid) {
                                validatedSignatures++;
                                anySignatureValidated = true;
                            }
                        }
                        
                        verifiedResults.push({
                            page: pageResult.page,
                            signatures: verifiedSignatures
                        });
                    } else {
                        verifiedResults.push(pageResult);
                    }
                }
                
                allResults.push({ fileName, results: verifiedResults });
            }

            displayResults(allResults, totalSignatures, validatedSignatures, pagesWithSignatures, totalPages, anySignatureValidated);
            
            isProcessing = false;
            updateProcessButton();
        }

        function showLoadingState(message) {
            resultsDiv.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <h3>${message}</h3>
                    <p>Processing with ${confidenceSlider.value} detection confidence and ${verificationSlider.value} verification threshold</p>
                </div>
            `;
        }

        async function detectSignatures(fileName, confidence) {
            // Simulate detection API call - replace with actual YOLO integration
            await new Promise(resolve => setTimeout(resolve, 800));
            
            if (mockDetectionResults[fileName]) {
                return mockDetectionResults[fileName].map(pageResult => ({
                    page: pageResult.page,
                    signatures: pageResult.signatures.filter(sig => sig.confidence >= confidence)
                }));
            } else {
                // Generate random results for demo
                const numPages = fileName.toLowerCase().includes('.pdf') ? Math.floor(Math.random() * 4) + 1 : 1;
                const results = [];
                
                for (let i = 1; i <= numPages; i++) {
                    const hasSignature = Math.random() > 0.5;
                    const signatures = [];
                    
                    if (hasSignature) {
                        const numSigs = Math.floor(Math.random() * 2) + 1;
                        for (let j = 0; j < numSigs; j++) {
                            const conf = Math.random() * 0.7 + 0.3;
                            if (conf >= confidence) {
                                signatures.push({
                                    confidence: conf,
                                    bbox: [
                                        Math.floor(Math.random() * 400),
                                        Math.floor(Math.random() * 600),
                                        Math.floor(Math.random() * 200) + 400,
                                        Math.floor(Math.random() * 100) + 600
                                    ]
                                });
                            }
                        }
                    }
                    
                    results.push({ page: i, signatures });
                }
                
                return results;
            }
        }

        async function verifySignature(fileName, pageNum, sigIndex, signature, threshold) {
            // Simulate verification model API call - replace with actual verification integration
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Simulate verification score (0-1)
            const verificationScore = Math.random();
            const isValid = verificationScore >= threshold;
            
            console.log(`Verifying ${fileName} - Page ${pageNum} - Signature ${sigIndex}: Score = ${verificationScore.toFixed(3)}, Valid = ${isValid}`);
            
            return {
                isValid: isValid,
                score: verificationScore
            };
        }

        function displayResults(allResults, totalSignatures, validatedSignatures, pagesWithSignatures, totalPages, anySignatureValidated) {
            let html = '';

            // Display results for each file
            for (let fileResult of allResults) {
                const { fileName, results } = fileResult;
                
                html += `<div class="result-card">`;
                html += `<h3 style="color: #374151; margin-bottom: 15px;">📄 ${fileName}</h3>`;
                
                for (let pageResult of results) {
                    const { page, signatures } = pageResult;
                    const hasSignatures = signatures.length > 0;
                    const hasValidatedSignatures = signatures.some(sig => sig.verified);
                    
                    html += `
                        <div class="result-header">
                            <span class="page-info">Page ${page}</span>
                            <span class="status ${hasSignatures ? 'detected' : 'not-detected'}">
                                ${hasSignatures ? '✅ Signature Detected' : '❌ No Signature'}
                            </span>
                        </div>
                    `;
                    
                    if (hasSignatures) {
                        // Page-level validation status
                        html += `
                            <div class="validation-status ${hasValidatedSignatures ? 'validated' : 'not-validated'}">
                                ${hasValidatedSignatures ? '🔒 VALIDATED' : '🚫 NOT VALIDATED'}
                                <span style="font-size: 0.9em; opacity: 0.9;">
                                    (${signatures.filter(s => s.verified).length}/${signatures.length} signatures verified)
                                </span>
                            </div>
                        `;
                        
                        html += `<div class="signature-list">`;
                        signatures.forEach((sig, index) => {
                            html += `
                                <div class="signature-item">
                                    <div class="signature-header">
                                        <div class="signature-info">
                                            <span>Signature ${index + 1}</span>
                                            <span class="confidence">Detection: ${(sig.confidence * 100).toFixed(1)}%</span>
                                        </div>
                                        <span class="verification-badge ${sig.verified ? 'valid' : 'invalid'}">
                                            ${sig.verified ? '✅ VALID' : '❌ INVALID'}
                                        </span>
                                    </div>
                                    <div class="verification-score">
                                        Verification Score: ${(sig.verificationScore * 100).toFixed(1)}%
                                    </div>
                                    <small>Bounding Box: [${sig.bbox.join(', ')}]</small>
                                </div>
                            `;
                        });
                        html += `</div>`;
                    }
                }
                
                html += `</div>`;
            }

            // Final validation result
            html += `
                <div class="final-validation ${anySignatureValidated ? 'validated' : 'not-validated'}">
                    ${anySignatureValidated ? '🎉 VALIDATED - At least one signature was successfully verified!' : '❌ NOT VALIDATED - No signatures passed verification'}
                </div>
            `;

            // Add summary
            html += `
                <div class="summary">
                    <h3>📊 Processing Summary</h3>
                    <div class="stats">
                        <div class="stat-item">
                            <span class="stat-number">${totalSignatures}</span>
                            <span>Signatures Detected</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">${validatedSignatures}</span>
                            <span>Signatures Validated</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">${pagesWithSignatures}</span>
                            <span>Pages with Signatures</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">${totalPages > 0 ? ((validatedSignatures / Math.max(totalSignatures, 1)) * 100).toFixed(1) : 0}%</span>
                            <span>Validation Rate</span>
                        </div>
                    </div>
                </div>
            `;

            resultsDiv.innerHTML = html;
        }

        // Reset functionality
        function resetInterface() {
            selectedFiles = [];
            resultsDiv.innerHTML = '';
            fileInput.innerHTML = `
                <input type="file" id="fileUpload" accept=".pdf,.jpg,.jpeg,.png,.bmp,.tiff,.tif" multiple>
                📁 Click to select files or drag & drop here
                <br><small>Supports: PDF, JPG, PNG, BMP, TIFF</small>
            `;
            document.getElementById('fileUpload').addEventListener('change', handleFileSelect);
            updateProcessButton();
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                resetInterface();
            }
        });
    </script>
</body>
</html>
