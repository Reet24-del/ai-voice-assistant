// Main JavaScript functionality for the web app
document.addEventListener('DOMContentLoaded', function() {
    const fetchDataBtn = document.getElementById('fetchDataBtn');
    const clearDataBtn = document.getElementById('clearDataBtn');
    const apiResponse = document.getElementById('apiResponse');
    
    // TTS elements
    const ttsText = document.getElementById('ttsText');
    const voiceSelect = document.getElementById('voiceSelect');
    const speedRange = document.getElementById('speedRange');
    const speedValue = document.getElementById('speedValue');
    const generateTtsBtn = document.getElementById('generateTtsBtn');
    const ttsResponse = document.getElementById('ttsResponse');
    const audioPlayer = document.getElementById('audioPlayer');
    
    // Echo Bot elements
    const startRecordingBtn = document.getElementById('startRecordingBtn');
    const stopRecordingBtn = document.getElementById('stopRecordingBtn');
    const recordingStatus = document.getElementById('recordingStatus');
    const recordingStatusText = document.getElementById('recordingStatusText');
    const recordingResponse = document.getElementById('recordingResponse');
    const uploadStatus = document.getElementById('uploadStatus');
    const uploadStatusText = document.getElementById('uploadStatusText');
    const uploadResponse = document.getElementById('uploadResponse');
    const recordedAudioPlayer = document.getElementById('recordedAudioPlayer');
    
    // Echo Bot v2 TTS elements
    const startEchoTtsRecordingBtn = document.getElementById('startEchoTtsRecordingBtn');
    const stopEchoTtsRecordingBtn = document.getElementById('stopEchoTtsRecordingBtn');
    const echoTtsVoiceSelect = document.getElementById('echoTtsVoiceSelect');
    const echoTtsRecordingStatus = document.getElementById('echoTtsRecordingStatus');
    const echoTtsRecordingStatusText = document.getElementById('echoTtsRecordingStatusText');
    const echoTtsRecordingResponse = document.getElementById('echoTtsRecordingResponse');
    const echoTtsProcessingStatus = document.getElementById('echoTtsProcessingStatus');
    const echoTtsProcessingStatusText = document.getElementById('echoTtsProcessingStatusText');
    const echoTtsProcessingResponse = document.getElementById('echoTtsProcessingResponse');
    const echoTtsAudioPlayer = document.getElementById('echoTtsAudioPlayer');
    
    // Transcription elements
    const startTranscribeRecordingBtn = document.getElementById('startTranscribeRecordingBtn');
    const stopTranscribeRecordingBtn = document.getElementById('stopTranscribeRecordingBtn');
    const transcribeRecordingStatus = document.getElementById('transcribeRecordingStatus');
    const transcribeRecordingStatusText = document.getElementById('transcribeRecordingStatusText');
    const transcribeRecordingResponse = document.getElementById('transcribeRecordingResponse');
    const transcriptionStatus = document.getElementById('transcriptionStatus');
    const transcriptionStatusText = document.getElementById('transcriptionStatusText');
    const transcriptionResponse = document.getElementById('transcriptionResponse');
    const transcribeAudioPlayer = document.getElementById('transcribeAudioPlayer');
    
    // LLM Audio Assistant elements
    const startLlmAudioRecordingBtn = document.getElementById('startLlmAudioRecordingBtn');
    const stopLlmAudioRecordingBtn = document.getElementById('stopLlmAudioRecordingBtn');
    const llmAudioVoiceSelect = document.getElementById('llmAudioVoiceSelect');
    const llmAudioRecordingStatus = document.getElementById('llmAudioRecordingStatus');
    const llmAudioRecordingStatusText = document.getElementById('llmAudioRecordingStatusText');
    const llmAudioRecordingResponse = document.getElementById('llmAudioRecordingResponse');
    const llmAudioProcessingStatus = document.getElementById('llmAudioProcessingStatus');
    const llmAudioProcessingStatusText = document.getElementById('llmAudioProcessingStatusText');
    const llmAudioProcessingResponse = document.getElementById('llmAudioProcessingResponse');
    const llmAudioPlayer = document.getElementById('llmAudioPlayer');
    
    // MediaRecorder variables for Echo Bot
    let mediaRecorder;
    let audioChunks = [];
    let stream;
    
    // MediaRecorder variables for Transcription
    let transcribeMediaRecorder;
    let transcribeAudioChunks = [];
    let transcribeStream;
    
    // MediaRecorder variables for Echo Bot v2 TTS
    let echoTtsMediaRecorder;
    let echoTtsAudioChunks = [];
    let echoTtsStream;
    
    // MediaRecorder variables for LLM Audio Assistant
    let llmAudioMediaRecorder;
    let llmAudioChunks = [];
    let llmAudioStream;

    // Function to fetch data from the Flask API
    async function fetchDataFromAPI() {
        try {
            // Show loading state
            apiResponse.innerHTML = `
                <div class="alert alert-info">
                    <div class="d-flex align-items-center">
                        <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                        Loading data from API...
                    </div>
                </div>
            `;

            const response = await fetch('/api/hello');
            const data = await response.json();

            if (response.ok) {
                apiResponse.innerHTML = `
                    <div class="alert alert-success">
                        <h5>API Response:</h5>
                        <p><strong>Message:</strong> ${data.message}</p>
                        <p><strong>Status:</strong> ${data.status}</p>
                        <p><strong>Timestamp:</strong> ${new Date().toLocaleString()}</p>
                    </div>
                `;
            } else {
                throw new Error('API request failed');
            }
        } catch (error) {
            apiResponse.innerHTML = `
                <div class="alert alert-danger">
                    <h5>Error:</h5>
                    <p>Failed to fetch data from API: ${error.message}</p>
                </div>
            `;
        }
    }

    // Function to clear the API response
    function clearData() {
        apiResponse.innerHTML = '';
    }

    // TTS Functions
    
    // Update speed value display
    function updateSpeedValue() {
        speedValue.textContent = speedRange.value;
    }
    
    // Generate TTS audio
    async function generateTTS() {
        const text = ttsText.value.trim();
        
        if (!text) {
            ttsResponse.innerHTML = `
                <div class="alert alert-warning">
                    Please enter some text to convert to speech.
                </div>
            `;
            return;
        }
        
        try {
            // Show loading state
            generateTtsBtn.disabled = true;
            generateTtsBtn.innerHTML = `
                <div class="d-flex align-items-center justify-content-center">
                    <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                    Generating speech...
                </div>
            `;
            
            ttsResponse.innerHTML = `
                <div class="alert alert-info">
                    <div class="d-flex align-items-center">
                        <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                        Processing your text...
                    </div>
                </div>
            `;
            
            // Prepare request data
            const requestData = {
                text: text,
                voice_id: voiceSelect.value,
                speed: parseInt(speedRange.value)
            };
            
            // Call FastAPI TTS endpoint
            const response = await fetch('http://127.0.0.1:8000/generate-tts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });
            
            const data = await response.json();
            
            if (response.ok && data.status === 'success') {
                // Success - show audio player
                ttsResponse.innerHTML = `
                    <div class="alert alert-success">
                        <h6>✅ Speech generated successfully!</h6>
                        <p class="mb-0">${data.message}</p>
                    </div>
                `;
                
                // Set audio source and show player
                audioPlayer.src = data.audio_url;
                audioPlayer.style.display = 'block';
                audioPlayer.load(); // Reload the audio element
                
                // Auto-play the audio (might be blocked by browser)
                try {
                    await audioPlayer.play();
                } catch (playError) {
                    console.log('Auto-play blocked by browser:', playError);
                }
                
            } else {
                // Error from TTS API
                throw new Error(data.detail || data.message || 'TTS generation failed');
            }
            
        } catch (error) {
            console.error('TTS Error:', error);
            ttsResponse.innerHTML = `
                <div class="alert alert-danger">
                    <h6>❌ Error generating speech</h6>
                    <p class="mb-0">${error.message}</p>
                </div>
            `;
            audioPlayer.style.display = 'none';
        } finally {
            // Reset button state
            generateTtsBtn.disabled = false;
            generateTtsBtn.innerHTML = `
                <i class="fas fa-microphone"></i> Generate Speech
            `;
        }
    }
    
    // Event listeners
    fetchDataBtn.addEventListener('click', fetchDataFromAPI);
    clearDataBtn.addEventListener('click', clearData);
    
    // TTS Event listeners
    speedRange.addEventListener('input', updateSpeedValue);
    generateTtsBtn.addEventListener('click', generateTTS);
    
    // Echo Bot Event listeners
    startRecordingBtn.addEventListener('click', startRecording);
    stopRecordingBtn.addEventListener('click', stopRecording);
    
    // Echo Bot v2 TTS Event listeners
    startEchoTtsRecordingBtn.addEventListener('click', startEchoTtsRecording);
    stopEchoTtsRecordingBtn.addEventListener('click', stopEchoTtsRecording);
    
    // Transcription Event listeners
    startTranscribeRecordingBtn.addEventListener('click', startTranscribeRecording);
    stopTranscribeRecordingBtn.addEventListener('click', stopTranscribeRecording);
    
    // LLM Audio Assistant Event listeners
    startLlmAudioRecordingBtn.addEventListener('click', startLlmAudioRecording);
    stopLlmAudioRecordingBtn.addEventListener('click', stopLlmAudioRecording);
    
    // Allow Enter key to submit TTS form
    ttsText.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            generateTTS();
        }
    });

    // Echo Bot Functions
    
    // Check if MediaRecorder is supported
    function checkMediaRecorderSupport() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            recordingResponse.innerHTML = `
                <div class="alert alert-danger">
                    <h6>❌ Media Recording Not Supported</h6>
                    <p class="mb-0">Your browser doesn't support audio recording. Please try a modern browser like Chrome, Firefox, or Edge.</p>
                </div>
            `;
            startRecordingBtn.disabled = true;
            return false;
        }
        
        if (!window.MediaRecorder) {
            recordingResponse.innerHTML = `
                <div class="alert alert-danger">
                    <h6>❌ MediaRecorder Not Supported</h6>
                    <p class="mb-0">Your browser doesn't support the MediaRecorder API. Please try a modern browser.</p>
                </div>
            `;
            startRecordingBtn.disabled = true;
            return false;
        }
        
        return true;
    }
    
    // Start recording function
    async function startRecording() {
        if (!checkMediaRecorderSupport()) {
            return;
        }
        
        try {
            // Show status
            recordingStatus.style.display = 'block';
            recordingStatusText.textContent = 'Requesting microphone access...';
            
            // Request microphone access
            stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                } 
            });
            
            // Clear previous recordings and responses
            audioChunks = [];
            recordingResponse.innerHTML = '';
            uploadResponse.innerHTML = '';
            uploadStatus.style.display = 'none';
            recordedAudioPlayer.style.display = 'none';
            
            // Create MediaRecorder
            const options = {
                mimeType: 'audio/webm;codecs=opus'
            };
            
            // Fallback for browsers that don't support webm
            if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                options.mimeType = 'audio/webm';
                if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                    options.mimeType = 'audio/mp4';
                    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                        delete options.mimeType;
                    }
                }
            }
            
            mediaRecorder = new MediaRecorder(stream, options);
            
            // Set up event handlers
            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };
            
            mediaRecorder.onstop = () => {
                // Create blob from recorded chunks
                const audioBlob = new Blob(audioChunks, { 
                    type: mediaRecorder.mimeType || 'audio/webm' 
                });
                
                // Create URL for the recorded audio
                const audioUrl = URL.createObjectURL(audioBlob);
                
                // Set up audio player
                recordedAudioPlayer.src = audioUrl;
                recordedAudioPlayer.style.display = 'block';
                
                // Show success message
                recordingResponse.innerHTML = `
                    <div class="alert alert-success">
                        <h6>✅ Recording completed!</h6>
                        <p class="mb-0">Your voice has been recorded. Click play below to hear your echo!</p>
                    </div>
                `;
                
                // Auto-play the recorded audio
                try {
                    recordedAudioPlayer.play();
                } catch (playError) {
                    console.log('Auto-play blocked by browser:', playError);
                }
                
                // Upload the audio file to the server
                uploadAudioToServer(audioBlob);
                
                // Clean up the stream
                if (stream) {
                    stream.getTracks().forEach(track => track.stop());
                }
            };
            
            mediaRecorder.onerror = (event) => {
                console.error('MediaRecorder error:', event.error);
                recordingResponse.innerHTML = `
                    <div class="alert alert-danger">
                        <h6>❌ Recording Error</h6>
                        <p class="mb-0">An error occurred during recording: ${event.error}</p>
                    </div>
                `;
                resetRecordingUI();
            };
            
            // Start recording
            mediaRecorder.start();
            
            // Update UI
            recordingStatusText.textContent = 'Recording... Click "Stop Recording" when finished.';
            startRecordingBtn.disabled = true;
            stopRecordingBtn.disabled = false;
            startRecordingBtn.innerHTML = '<i class="fas fa-microphone"></i> Recording...';
            stopRecordingBtn.innerHTML = '<i class="fas fa-stop"></i> Stop Recording';
            
        } catch (error) {
            console.error('Error starting recording:', error);
            
            let errorMessage = 'Failed to access microphone.';
            if (error.name === 'NotAllowedError') {
                errorMessage = 'Microphone access denied. Please allow microphone access and try again.';
            } else if (error.name === 'NotFoundError') {
                errorMessage = 'No microphone found. Please connect a microphone and try again.';
            }
            
            recordingResponse.innerHTML = `
                <div class="alert alert-danger">
                    <h6>❌ Recording Failed</h6>
                    <p class="mb-0">${errorMessage}</p>
                </div>
            `;
            
            resetRecordingUI();
        }
    }
    
    // Stop recording function
    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            recordingStatusText.textContent = 'Processing recording...';
            mediaRecorder.stop();
        }
        
        resetRecordingUI();
    }
    
    // Reset recording UI
    function resetRecordingUI() {
        recordingStatus.style.display = 'none';
        startRecordingBtn.disabled = false;
        stopRecordingBtn.disabled = true;
        startRecordingBtn.innerHTML = '<i class="fas fa-microphone"></i> Start Recording';
        stopRecordingBtn.innerHTML = '<i class="fas fa-stop"></i> Stop Recording';
    }
    
    // Upload audio file to server
    async function uploadAudioToServer(audioBlob) {
        try {
            // Show upload status
            uploadStatus.style.display = 'block';
            uploadStatusText.textContent = 'Uploading audio to server...';
            uploadResponse.innerHTML = '';
            
            // Create FormData with the audio file
            const formData = new FormData();
            const timestamp = new Date().getTime();
            const filename = `recording_${timestamp}.webm`;
            formData.append('audio_file', audioBlob, filename);
            
            // Upload to FastAPI server
            const response = await fetch('http://127.0.0.1:8000/upload-audio', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok && data.status === 'success') {
                // Success response
                uploadResponse.innerHTML = `
                    <div class="alert alert-success">
                        <h6>📤 Upload Successful!</h6>
                        <p class="mb-1"><strong>Filename:</strong> ${data.filename}</p>
                        <p class="mb-1"><strong>Content Type:</strong> ${data.content_type}</p>
                        <p class="mb-1"><strong>File Size:</strong> ${formatFileSize(data.size)}</p>
                        <p class="mb-0"><small class="text-muted">${data.message}</small></p>
                    </div>
                `;
            } else {
                // Error from upload API
                throw new Error(data.detail || data.message || 'Upload failed');
            }
            
        } catch (error) {
            console.error('Upload Error:', error);
            uploadResponse.innerHTML = `
                <div class="alert alert-danger">
                    <h6>❌ Upload Failed</h6>
                    <p class="mb-0">Failed to upload audio to server: ${error.message}</p>
                </div>
            `;
        } finally {
            // Hide upload status
            uploadStatus.style.display = 'none';
        }
    }
    
    // Helper function to format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Transcription Functions
    
    // Check if MediaRecorder is supported for transcription
    function checkTranscribeMediaRecorderSupport() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            transcribeRecordingResponse.innerHTML = `
                <div class="alert alert-danger">
                    <h6>❌ Media Recording Not Supported</h6>
                    <p class="mb-0">Your browser doesn't support audio recording. Please try a modern browser like Chrome, Firefox, or Edge.</p>
                </div>
            `;
            startTranscribeRecordingBtn.disabled = true;
            return false;
        }
        
        if (!window.MediaRecorder) {
            transcribeRecordingResponse.innerHTML = `
                <div class="alert alert-danger">
                    <h6>❌ MediaRecorder Not Supported</h6>
                    <p class="mb-0">Your browser doesn't support the MediaRecorder API. Please try a modern browser.</p>
                </div>
            `;
            startTranscribeRecordingBtn.disabled = true;
            return false;
        }
        
        return true;
    }
    
    // Start transcription recording function
    async function startTranscribeRecording() {
        if (!checkTranscribeMediaRecorderSupport()) {
            return;
        }
        
        try {
            // Show status
            transcribeRecordingStatus.style.display = 'block';
            transcribeRecordingStatusText.textContent = 'Requesting microphone access...';
            
            // Request microphone access
            transcribeStream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                } 
            });
            
            // Clear previous recordings and responses
            transcribeAudioChunks = [];
            transcribeRecordingResponse.innerHTML = '';
            transcriptionResponse.innerHTML = '';
            transcriptionStatus.style.display = 'none';
            transcribeAudioPlayer.style.display = 'none';
            
            // Create MediaRecorder
            const options = {
                mimeType: 'audio/webm;codecs=opus'
            };
            
            // Fallback for browsers that don't support webm
            if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                options.mimeType = 'audio/webm';
                if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                    options.mimeType = 'audio/mp4';
                    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                        delete options.mimeType;
                    }
                }
            }
            
            transcribeMediaRecorder = new MediaRecorder(transcribeStream, options);
            
            // Set up event handlers
            transcribeMediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    transcribeAudioChunks.push(event.data);
                }
            };
            
            transcribeMediaRecorder.onstop = () => {
                // Create blob from recorded chunks
                const audioBlob = new Blob(transcribeAudioChunks, { 
                    type: transcribeMediaRecorder.mimeType || 'audio/webm' 
                });
                
                // Create URL for the recorded audio
                const audioUrl = URL.createObjectURL(audioBlob);
                
                // Set up audio player
                transcribeAudioPlayer.src = audioUrl;
                transcribeAudioPlayer.style.display = 'block';
                
                // Show success message
                transcribeRecordingResponse.innerHTML = `
                    <div class="alert alert-success">
                        <h6>✅ Recording completed!</h6>
                        <p class="mb-0">Your voice has been recorded. Sending for transcription...</p>
                    </div>
                `;
                
                // Auto-play the recorded audio
                try {
                    transcribeAudioPlayer.play();
                } catch (playError) {
                    console.log('Auto-play blocked by browser:', playError);
                }
                
                // Send the audio file for transcription
                transcribeAudioFile(audioBlob);
                
                // Clean up the stream
                if (transcribeStream) {
                    transcribeStream.getTracks().forEach(track => track.stop());
                }
            };
            
            transcribeMediaRecorder.onerror = (event) => {
                console.error('MediaRecorder error:', event.error);
                transcribeRecordingResponse.innerHTML = `
                    <div class="alert alert-danger">
                        <h6>❌ Recording Error</h6>
                        <p class="mb-0">An error occurred during recording: ${event.error}</p>
                    </div>
                `;
                resetTranscribeRecordingUI();
            };
            
            // Start recording
            transcribeMediaRecorder.start();
            
            // Update UI
            transcribeRecordingStatusText.textContent = 'Recording... Click "Stop Recording" when finished.';
            startTranscribeRecordingBtn.disabled = true;
            stopTranscribeRecordingBtn.disabled = false;
            startTranscribeRecordingBtn.innerHTML = '<i class="fas fa-microphone"></i> Recording...';
            stopTranscribeRecordingBtn.innerHTML = '<i class="fas fa-stop"></i> Stop Recording';
            
        } catch (error) {
            console.error('Error starting transcription recording:', error);
            
            let errorMessage = 'Failed to access microphone.';
            if (error.name === 'NotAllowedError') {
                errorMessage = 'Microphone access denied. Please allow microphone access and try again.';
            } else if (error.name === 'NotFoundError') {
                errorMessage = 'No microphone found. Please connect a microphone and try again.';
            }
            
            transcribeRecordingResponse.innerHTML = `
                <div class="alert alert-danger">
                    <h6>❌ Recording Failed</h6>
                    <p class="mb-0">${errorMessage}</p>
                </div>
            `;
            
            resetTranscribeRecordingUI();
        }
    }
    
    // Stop transcription recording function
    function stopTranscribeRecording() {
        if (transcribeMediaRecorder && transcribeMediaRecorder.state === 'recording') {
            transcribeRecordingStatusText.textContent = 'Processing recording...';
            transcribeMediaRecorder.stop();
        }
        
        resetTranscribeRecordingUI();
    }
    
    // Reset transcription recording UI
    function resetTranscribeRecordingUI() {
        transcribeRecordingStatus.style.display = 'none';
        startTranscribeRecordingBtn.disabled = false;
        stopTranscribeRecordingBtn.disabled = true;
        startTranscribeRecordingBtn.innerHTML = '<i class="fas fa-microphone"></i> Start Recording for Transcription';
        stopTranscribeRecordingBtn.innerHTML = '<i class="fas fa-stop"></i> Stop Recording';
    }
    
    // Transcribe audio file
    async function transcribeAudioFile(audioBlob) {
        try {
            // Show transcription status
            transcriptionStatus.style.display = 'block';
            transcriptionStatusText.textContent = 'Transcribing your audio with AssemblyAI...';
            transcriptionResponse.innerHTML = '';
            
            // Create FormData with the audio file
            const formData = new FormData();
            const timestamp = new Date().getTime();
            const filename = `transcribe_${timestamp}.webm`;
            formData.append('audio_file', audioBlob, filename);
            
            // Send to FastAPI transcription endpoint
            const response = await fetch('http://127.0.0.1:8000/transcribe/file', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok && data.status === 'success') {
                // Success response
                transcriptionResponse.innerHTML = `
                    <div class="alert alert-success">
                        <h6>🎯 Transcription Complete!</h6>
                        <p class="mb-2"><strong>Transcription:</strong></p>
                        <div class="p-3 bg-light rounded border">
                            <p class="mb-0 text-dark" style="font-size: 1.1em; line-height: 1.5;">"${data.transcription}"</p>
                        </div>
                        ${data.confidence ? `<p class="mb-1 mt-2"><strong>Confidence:</strong> ${(data.confidence * 100).toFixed(1)}%</p>` : ''}
                        ${data.processing_time ? `<p class="mb-0"><strong>Processing Time:</strong> ${data.processing_time} seconds</p>` : ''}
                    </div>
                `;
            } else {
                // Error from transcription API
                throw new Error(data.detail || data.message || 'Transcription failed');
            }
            
        } catch (error) {
            console.error('Transcription Error:', error);
            transcriptionResponse.innerHTML = `
                <div class="alert alert-danger">
                    <h6>❌ Transcription Failed</h6>
                    <p class="mb-0">Failed to transcribe audio: ${error.message}</p>
                </div>
            `;
        } finally {
            // Hide transcription status
            transcriptionStatus.style.display = 'none';
        }
    }
    
    // Echo Bot v2 TTS Functions
    
    // Check if MediaRecorder is supported for Echo TTS
    function checkEchoTtsMediaRecorderSupport() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            echoTtsRecordingResponse.innerHTML = `
                <div class="alert alert-danger">
                    <h6>❌ Media Recording Not Supported</h6>
                    <p class="mb-0">Your browser doesn't support audio recording. Please try a modern browser like Chrome, Firefox, or Edge.</p>
                </div>
            `;
            startEchoTtsRecordingBtn.disabled = true;
            return false;
        }
        
        if (!window.MediaRecorder) {
            echoTtsRecordingResponse.innerHTML = `
                <div class="alert alert-danger">
                    <h6>❌ MediaRecorder Not Supported</h6>
                    <p class="mb-0">Your browser doesn't support the MediaRecorder API. Please try a modern browser.</p>
                </div>
            `;
            startEchoTtsRecordingBtn.disabled = true;
            return false;
        }
        
        return true;
    }
    
    // Start Echo TTS recording function
    async function startEchoTtsRecording() {
        if (!checkEchoTtsMediaRecorderSupport()) {
            return;
        }
        
        try {
            // Show status
            echoTtsRecordingStatus.style.display = 'block';
            echoTtsRecordingStatusText.textContent = 'Requesting microphone access...';
            
            // Request microphone access
            echoTtsStream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                } 
            });
            
            // Clear previous recordings and responses
            echoTtsAudioChunks = [];
            echoTtsRecordingResponse.innerHTML = '';
            echoTtsProcessingResponse.innerHTML = '';
            echoTtsProcessingStatus.style.display = 'none';
            echoTtsAudioPlayer.style.display = 'none';
            
            // Create MediaRecorder
            const options = {
                mimeType: 'audio/webm;codecs=opus'
            };
            
            // Fallback for browsers that don't support webm
            if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                options.mimeType = 'audio/webm';
                if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                    options.mimeType = 'audio/mp4';
                    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                        delete options.mimeType;
                    }
                }
            }
            
            echoTtsMediaRecorder = new MediaRecorder(echoTtsStream, options);
            
            // Set up event handlers
            echoTtsMediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    echoTtsAudioChunks.push(event.data);
                }
            };
            
            echoTtsMediaRecorder.onstop = () => {
                // Create blob from recorded chunks
                const audioBlob = new Blob(echoTtsAudioChunks, { 
                    type: echoTtsMediaRecorder.mimeType || 'audio/webm' 
                });
                
                // Show success message
                echoTtsRecordingResponse.innerHTML = `
                    <div class="alert alert-success">
                        <h6>✅ Recording completed!</h6>
                        <p class="mb-0">Your voice has been recorded. Processing with TTS...</p>
                    </div>
                `;
                
                // Send the audio file for TTS processing
                processEchoTtsAudio(audioBlob);
                
                // Clean up the stream
                if (echoTtsStream) {
                    echoTtsStream.getTracks().forEach(track => track.stop());
                }
            };
            
            echoTtsMediaRecorder.onerror = (event) => {
                console.error('MediaRecorder error:', event.error);
                echoTtsRecordingResponse.innerHTML = `
                    <div class="alert alert-danger">
                        <h6>❌ Recording Error</h6>
                        <p class="mb-0">An error occurred during recording: ${event.error}</p>
                    </div>
                `;
                resetEchoTtsRecordingUI();
            };
            
            // Start recording
            echoTtsMediaRecorder.start();
            
            // Update UI
            echoTtsRecordingStatusText.textContent = 'Recording... Click "Stop Recording" when finished.';
            startEchoTtsRecordingBtn.disabled = true;
            stopEchoTtsRecordingBtn.disabled = false;
            startEchoTtsRecordingBtn.innerHTML = '<i class="fas fa-microphone"></i> Recording...';
            stopEchoTtsRecordingBtn.innerHTML = '<i class="fas fa-stop"></i> Stop Recording';
            
        } catch (error) {
            console.error('Error starting Echo TTS recording:', error);
            
            let errorMessage = 'Failed to access microphone.';
            if (error.name === 'NotAllowedError') {
                errorMessage = 'Microphone access denied. Please allow microphone access and try again.';
            } else if (error.name === 'NotFoundError') {
                errorMessage = 'No microphone found. Please connect a microphone and try again.';
            }
            
            echoTtsRecordingResponse.innerHTML = `
                <div class="alert alert-danger">
                    <h6>❌ Recording Failed</h6>
                    <p class="mb-0">${errorMessage}</p>
                </div>
            `;
            
            resetEchoTtsRecordingUI();
        }
    }
    
    // Stop Echo TTS recording function
    function stopEchoTtsRecording() {
        if (echoTtsMediaRecorder && echoTtsMediaRecorder.state === 'recording') {
            echoTtsRecordingStatusText.textContent = 'Processing recording...';
            echoTtsMediaRecorder.stop();
        }
        
        resetEchoTtsRecordingUI();
    }
    
    // Reset Echo TTS recording UI
    function resetEchoTtsRecordingUI() {
        echoTtsRecordingStatus.style.display = 'none';
        startEchoTtsRecordingBtn.disabled = false;
        stopEchoTtsRecordingBtn.disabled = true;
        startEchoTtsRecordingBtn.innerHTML = '<i class="fas fa-microphone"></i> Start Recording';
        stopEchoTtsRecordingBtn.innerHTML = '<i class="fas fa-stop"></i> Stop Recording';
    }
    
    // Process Echo TTS audio with transcription and TTS
    async function processEchoTtsAudio(audioBlob) {
        try {
            // Show processing status
            echoTtsProcessingStatus.style.display = 'block';
            echoTtsProcessingStatusText.textContent = 'Transcribing and generating TTS...';
            echoTtsProcessingResponse.innerHTML = '';
            
            // Create FormData with the audio file and voice selection
            const formData = new FormData();
            const timestamp = new Date().getTime();
            const filename = `echo_tts_${timestamp}.webm`;
            formData.append('audio_file', audioBlob, filename);
            formData.append('voice_id', echoTtsVoiceSelect.value);
            formData.append('speed', '100');
            
            // Send to FastAPI Echo TTS endpoint
            const response = await fetch('http://127.0.0.1:8000/tts/echo', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok && data.status === 'success') {
                // Success response
                echoTtsProcessingResponse.innerHTML = `
                    <div class="alert alert-success">
                        <h6>🎉 Echo TTS Complete!</h6>
                        <p class="mb-2"><strong>What you said:</strong></p>
                        <div class="p-3 bg-light rounded border mb-3">
                            <p class="mb-0 text-dark" style="font-size: 1.1em; line-height: 1.5;">"${data.transcription}"</p>
                        </div>
                        <p class="mb-2"><strong>Now playing in ${echoTtsVoiceSelect.options[echoTtsVoiceSelect.selectedIndex].text} voice:</strong></p>
                        ${data.processing_time ? `<p class="mb-0"><strong>Processing Time:</strong> ${data.processing_time} seconds</p>` : ''}
                    </div>
                `;
                
                // Set audio source and show player
                echoTtsAudioPlayer.src = data.audio_url;
                echoTtsAudioPlayer.style.display = 'block';
                echoTtsAudioPlayer.load(); // Reload the audio element
                
                // Auto-play the TTS audio
                try {
                    await echoTtsAudioPlayer.play();
                } catch (playError) {
                    console.log('Auto-play blocked by browser:', playError);
                }
                
            } else {
                // Error from Echo TTS API
                throw new Error(data.detail || data.message || 'Echo TTS processing failed');
            }
            
        } catch (error) {
            console.error('Echo TTS Processing Error:', error);
            echoTtsProcessingResponse.innerHTML = `
                <div class="alert alert-danger">
                    <h6>❌ Echo TTS Processing Failed</h6>
                    <p class="mb-0">Failed to process echo TTS: ${error.message}</p>
                </div>
            `;
            echoTtsAudioPlayer.style.display = 'none';
        } finally {
            // Hide processing status
            echoTtsProcessingStatus.style.display = 'none';
        }
    }
    
    // LLM Audio Assistant Functions
    
    // Check if MediaRecorder is supported for LLM Audio Assistant
    function checkLlmAudioMediaRecorderSupport() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            llmAudioRecordingResponse.innerHTML = `
                <div class="alert alert-danger">
                    <h6>❌ Media Recording Not Supported</h6>
                    <p class="mb-0">Your browser doesn't support audio recording. Please try a modern browser like Chrome, Firefox, or Edge.</p>
                </div>
            `;
            startLlmAudioRecordingBtn.disabled = true;
            return false;
        }
        
        if (!window.MediaRecorder) {
            llmAudioRecordingResponse.innerHTML = `
                <div class="alert alert-danger">
                    <h6>❌ MediaRecorder Not Supported</h6>
                    <p class="mb-0">Your browser doesn't support the MediaRecorder API. Please try a modern browser.</p>
                </div>
            `;
            startLlmAudioRecordingBtn.disabled = true;
            return false;
        }
        
        return true;
    }
    
    // Start LLM Audio Assistant recording function
    async function startLlmAudioRecording() {
        if (!checkLlmAudioMediaRecorderSupport()) {
            return;
        }
        
        try {
            // Show status
            llmAudioRecordingStatus.style.display = 'block';
            llmAudioRecordingStatusText.textContent = 'Requesting microphone access...';
            
            // Request microphone access
            llmAudioStream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                } 
            });
            
            // Clear previous recordings and responses
            llmAudioChunks = [];
            llmAudioRecordingResponse.innerHTML = '';
            llmAudioProcessingResponse.innerHTML = '';
            llmAudioProcessingStatus.style.display = 'none';
            llmAudioPlayer.style.display = 'none';
            
            // Create MediaRecorder
            const options = {
                mimeType: 'audio/webm;codecs=opus'
            };
            
            // Fallback for browsers that don't support webm
            if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                options.mimeType = 'audio/webm';
                if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                    options.mimeType = 'audio/mp4';
                    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                        delete options.mimeType;
                    }
                }
            }
            
            llmAudioMediaRecorder = new MediaRecorder(llmAudioStream, options);
            
            // Set up event handlers
            llmAudioMediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    llmAudioChunks.push(event.data);
                }
            };
            
            llmAudioMediaRecorder.onstop = () => {
                // Create blob from recorded chunks
                const audioBlob = new Blob(llmAudioChunks, { 
                    type: llmAudioMediaRecorder.mimeType || 'audio/webm' 
                });
                
                // Show success message
                llmAudioRecordingResponse.innerHTML = `
                    <div class="alert alert-success">
                        <h6>✅ Recording completed!</h6>
                        <p class="mb-0">Your question has been recorded. Processing with AI assistant...</p>
                    </div>
                `;
                
                // Send the audio file for LLM processing
                processLlmAudioQuery(audioBlob);
                
                // Clean up the stream
                if (llmAudioStream) {
                    llmAudioStream.getTracks().forEach(track => track.stop());
                }
            };
            
            llmAudioMediaRecorder.onerror = (event) => {
                console.error('MediaRecorder error:', event.error);
                llmAudioRecordingResponse.innerHTML = `
                    <div class="alert alert-danger">
                        <h6>❌ Recording Error</h6>
                        <p class="mb-0">An error occurred during recording: ${event.error}</p>
                    </div>
                `;
                resetLlmAudioRecordingUI();
            };
            
            // Start recording
            llmAudioMediaRecorder.start();
            
            // Update UI
            llmAudioRecordingStatusText.textContent = 'Recording your question... Click "Stop Recording" when finished.';
            startLlmAudioRecordingBtn.disabled = true;
            stopLlmAudioRecordingBtn.disabled = false;
            startLlmAudioRecordingBtn.innerHTML = '<i class="fas fa-microphone"></i> Recording...';
            stopLlmAudioRecordingBtn.innerHTML = '<i class="fas fa-stop"></i> Stop Recording';
            
        } catch (error) {
            console.error('Error starting LLM Audio recording:', error);
            
            let errorMessage = 'Failed to access microphone.';
            if (error.name === 'NotAllowedError') {
                errorMessage = 'Microphone access denied. Please allow microphone access and try again.';
            } else if (error.name === 'NotFoundError') {
                errorMessage = 'No microphone found. Please connect a microphone and try again.';
            }
            
            llmAudioRecordingResponse.innerHTML = `
                <div class="alert alert-danger">
                    <h6>❌ Recording Failed</h6>
                    <p class="mb-0">${errorMessage}</p>
                </div>
            `;
            
            resetLlmAudioRecordingUI();
        }
    }
    
    // Stop LLM Audio Assistant recording function
    function stopLlmAudioRecording() {
        if (llmAudioMediaRecorder && llmAudioMediaRecorder.state === 'recording') {
            llmAudioRecordingStatusText.textContent = 'Processing recording...';
            llmAudioMediaRecorder.stop();
        }
        
        resetLlmAudioRecordingUI();
    }
    
    // Reset LLM Audio Assistant recording UI
    function resetLlmAudioRecordingUI() {
        llmAudioRecordingStatus.style.display = 'none';
        startLlmAudioRecordingBtn.disabled = false;
        stopLlmAudioRecordingBtn.disabled = true;
        startLlmAudioRecordingBtn.innerHTML = '<i class="fas fa-microphone"></i> Start Recording';
        stopLlmAudioRecordingBtn.innerHTML = '<i class="fas fa-stop"></i> Stop Recording';
    }
    
    // Process LLM Audio Query with transcription, LLM, and TTS
    async function processLlmAudioQuery(audioBlob) {
        try {
            // Show processing status
            llmAudioProcessingStatus.style.display = 'block';
            llmAudioProcessingStatusText.textContent = 'Transcribing, processing with AI, and generating voice response...';
            llmAudioProcessingResponse.innerHTML = '';
            
            // Create FormData with the audio file and voice selection
            const formData = new FormData();
            const timestamp = new Date().getTime();
            const filename = `llm_audio_${timestamp}.webm`;
            formData.append('audio_file', audioBlob, filename);
            formData.append('voice_id', llmAudioVoiceSelect.value);
            formData.append('speed', '100');
            
            // Send to FastAPI LLM Audio Query endpoint
            const response = await fetch('http://127.0.0.1:8000/llm/query-audio', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok && data.status === 'success') {
                // Success response
                llmAudioProcessingResponse.innerHTML = `
                    <div class="alert alert-success">
                        <h6>🤖 AI Assistant Response Complete!</h6>
                        <p class="mb-2"><strong>Your Question:</strong></p>
                        <div class="p-3 bg-light rounded border mb-3">
                            <p class="mb-0 text-dark" style="font-size: 1.1em; line-height: 1.5;">"${data.transcription}"</p>
                        </div>
                        <p class="mb-2"><strong>AI Assistant Response:</strong></p>
                        <div class="p-3 bg-primary bg-opacity-10 rounded border mb-3">
                            <p class="mb-0 text-dark" style="font-size: 1.1em; line-height: 1.5;">${data.response}</p>
                        </div>
                        <p class="mb-2"><strong>Now playing in ${llmAudioVoiceSelect.options[llmAudioVoiceSelect.selectedIndex].text} voice:</strong></p>
                        ${data.processing_time ? `<p class="mb-0"><strong>Processing Time:</strong> ${data.processing_time} seconds</p>` : ''}
                    </div>
                `;
                
                // Set audio source and show player
                llmAudioPlayer.src = data.audio_url;
                llmAudioPlayer.style.display = 'block';
                llmAudioPlayer.load(); // Reload the audio element
                
                // Auto-play the AI response audio
                try {
                    await llmAudioPlayer.play();
                } catch (playError) {
                    console.log('Auto-play blocked by browser:', playError);
                }
                
            } else {
                // Error from LLM Audio Query API
                throw new Error(data.detail || data.message || 'LLM audio query processing failed');
            }
            
        } catch (error) {
            console.error('LLM Audio Query Processing Error:', error);
            llmAudioProcessingResponse.innerHTML = `
                <div class="alert alert-danger">
                    <h6>❌ AI Assistant Processing Failed</h6>
                    <p class="mb-0">Failed to process your question with AI assistant: ${error.message}</p>
                </div>
            `;
            llmAudioPlayer.style.display = 'none';
        } finally {
            // Hide processing status
            llmAudioProcessingStatus.style.display = 'none';
        }
    }
    
    // Welcome message in console
    console.log('🚀 Python Web App loaded successfully!');
    console.log('💡 Click the "Fetch Data from API" button to test the backend connection.');
    console.log('🎵 Try the Text-to-Speech feature!');
    console.log('🎙️ Try the Echo Bot v1 to record and playback your voice!');
    console.log('🆕 Try the NEW Echo Bot v2 - TTS Echo with Murf AI voices!');
    console.log('🎯 Try the Speech-to-Text Transcription feature!');
    console.log('🤖 Try the NEW LLM Audio Assistant - Ask AI questions with your voice!');
    
    // Initialize speed value display
    updateSpeedValue();
    
    // Check Echo Bot support on load
    checkMediaRecorderSupport();
});
