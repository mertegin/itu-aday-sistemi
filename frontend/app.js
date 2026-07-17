// İTÜ Aday Sistemi — sohbet ekranı (sade sürüm)
// Sadece sohbet: mesajlaşma, aşama göstergesi, yeni oturum. XAI/senaryo/istatistik yok.

const API_BASE = window.location.origin + "/api";

let sessionId = null;

// ============ TÜRKÇE AŞAMA İSİMLERİ ============
const STAGE_TR = {
    S0_FALLBACK: "Toparlanma",
    S1_GREETING: "Karşılama",
    S2_INDECISION_PROBE: "Adayı tanıma",
    S2R_PROFILE_UPDATE: "Profil güncelleme",
    S3_ARGUMENT_SELECTION: "Strateji seçimi",
    S4_ARGUMENT_DELIVERY: "Öneri sunumu",
    S5_RECEPTION_EVAL: "Tepki değerlendirme",
    S6_RAG_DEEP_DIVE: "Detay bilgi",
    S7_CONCERN_HANDLING: "Endişe yönetimi",
    S8_IDEAL_MATCH_SUMMARY: "İdeal tercih özeti",
    S9_CLOSING: "Kapanış",
};

// ============ DOM ============
const messagesEl = document.getElementById("messages");
const inputEl = document.getElementById("messageInput");
const chatForm = document.getElementById("chatForm");
const submitBtn = chatForm.querySelector("button[type='submit']");
const sessionIdEl = document.getElementById("sessionId");
const stageBadgeEl = document.getElementById("stageBadge");

// ============ EVENT'LER ============
document.getElementById("newSessionBtn").addEventListener("click", () => startNewSession());

chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = inputEl.value.trim();
    if (!text) return;
    await sendMessage(text);
});

// Oturum kimliğini tıklayınca kopyala (hata bildirmek için lazım oluyor)
sessionIdEl.addEventListener("click", async () => {
    if (!sessionId) return;
    try {
        await navigator.clipboard.writeText(sessionId);
        const old = sessionIdEl.textContent;
        sessionIdEl.textContent = "kopyalandı ✓";
        setTimeout(() => { sessionIdEl.textContent = old; }, 1200);
    } catch { /* clipboard izni yoksa sessiz geç */ }
});

// ============ SESSION ============
async function startNewSession() {
    const res = await fetch(`${API_BASE}/session/new`, { method: "POST" });
    const data = await res.json();
    sessionId = data.session_id;

    sessionIdEl.textContent = sessionId;
    stageBadgeEl.textContent = STAGE_TR.S1_GREETING;
    messagesEl.innerHTML = "";
    appendSystemMsg("Yeni sohbet başladı — merhaba diyerek başlayabilirsin.");
    inputEl.focus();
}

// ============ MESAJ ============
async function sendMessage(text) {
    appendMsg("user", text);
    inputEl.value = "";
    submitBtn.disabled = true;

    const typingEl = document.createElement("div");
    typingEl.className = "typing";
    typingEl.innerHTML = "<i></i><i></i><i></i>";
    messagesEl.appendChild(typingEl);
    scrollToBottom();

    try {
        const res = await fetch(`${API_BASE}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sessionId, text }),
        });

        typingEl.remove();

        if (!res.ok) {
            appendSystemMsg(`Hata (${res.status}): ${await res.text()}`);
            return;
        }

        const data = await res.json();
        sessionId = data.session_id;
        sessionIdEl.textContent = sessionId;

        appendMsg("assistant", data.response_text);
        stageBadgeEl.textContent = STAGE_TR[data.fsm_state] || data.fsm_state;
    } catch (err) {
        typingEl.remove();
        appendSystemMsg(`Bağlantı hatası: ${err.message}`);
    } finally {
        submitBtn.disabled = false;
        inputEl.focus();
    }
}

function appendMsg(role, text) {
    const el = document.createElement("div");
    el.className = `msg ${role}`;
    el.textContent = text;
    messagesEl.appendChild(el);
    scrollToBottom();
}

function appendSystemMsg(text) {
    const el = document.createElement("div");
    el.className = "msg system";
    el.textContent = text;
    messagesEl.appendChild(el);
    scrollToBottom();
}

function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

// Startup
startNewSession();
