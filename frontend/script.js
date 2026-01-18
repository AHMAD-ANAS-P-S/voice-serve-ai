
const API_URL = "/api/v1/process";

const chatContainer = document.getElementById('chat-container');
const micBtn = document.getElementById('mic-btn');
const textInput = document.getElementById('text-input');
const sendBtn = document.getElementById('send-btn');
const uploadBtn = document.getElementById('upload-btn');
const fileInput = document.getElementById('file-input');
const uploadsPreview = document.getElementById('uploads-preview');
const audioPlayer = document.getElementById('audio-player');

let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let pendingImage = null;

// Generate User ID
const userId = "user_" + Math.random().toString(36).substr(2, 9);

// --- Event Listeners ---

textInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

sendBtn.addEventListener('click', () => sendMessage());

uploadBtn.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        pendingImage = file;
        showPreview(file);
    }
});

micBtn.addEventListener('click', toggleRecording);

// --- Functions ---

function showPreview(file) {
    uploadsPreview.innerHTML = '';
    const img = document.createElement('img');
    img.src = URL.createObjectURL(file);
    img.className = 'preview-thumb';
    uploadsPreview.appendChild(img);
}

function appendMessage(text, isUser = false, imageFile = null) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;

    let contentHtml = `<p>${text || (imageFile ? 'Sent an image' : '')}</p>`;

    if (imageFile) {
        const imgUrl = URL.createObjectURL(imageFile);
        contentHtml += `<img src="${imgUrl}" class="image-preview" style="max-height: 150px;">`;
    }

    msgDiv.innerHTML = `
        <div class="avatar">${isUser ? '👤' : '🤖'}</div>
        <div class="bubble">${contentHtml}</div>
    `;

    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function sendMessage(audioBlob = null) {
    const text = textInput.value.trim();

    if (!text && !audioBlob && !pendingImage) return;

    // UI Updates
    if (text) appendMessage(text, true);
    if (pendingImage) appendMessage(null, true, pendingImage);
    if (audioBlob) appendMessage("🎤 Audio Sent", true);

    textInput.value = '';
    uploadsPreview.innerHTML = '';
    addLoadingBubble();

    // Prepare Data
    const formData = new FormData();
    formData.append("user_id", userId);

    if (text) formData.append("text", text);
    if (audioBlob) formData.append("audio", audioBlob, "voice.webm"); // webm/mp3 handling in backend
    if (pendingImage) formData.append("image", pendingImage);

    pendingImage = null;

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        removeLoadingBubble();

        if (data.response) {
            appendMessage(data.response, false);
        }

        if (data.voice_url) {
            playAudio(data.voice_url);
        }

    } catch (error) {
        console.error(error);
        removeLoadingBubble();
        appendMessage("Error communicating with server.", false);
    }
}

function playAudio(url) {
    audioPlayer.src = url;
    audioPlayer.play().catch(e => console.log("Autoplay blocked:", e));
}

function addLoadingBubble() {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message bot-message loading-msg';
    msgDiv.id = 'loading-bubble';
    msgDiv.innerHTML = `
        <div class="avatar">🤖</div>
        <div class="bubble">...</div>
    `;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function removeLoadingBubble() {
    const bubble = document.getElementById('loading-bubble');
    if (bubble) bubble.remove();
}

// --- Voice Logic ---

async function toggleRecording() {
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            sendMessage(audioBlob);
        };

        mediaRecorder.start();
        isRecording = true;
        micBtn.classList.add('recording');

    } catch (err) {
        alert("Microphone access denied or error: " + err);
    }
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        micBtn.classList.remove('recording');
    }
}
