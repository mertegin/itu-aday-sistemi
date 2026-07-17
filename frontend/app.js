// İTÜ Aday Sistemi — chat client
// Özellikler: XAI basit/teknik mod, hazır senaryolar (adım adım), transcript export, aşama göstergesi.

const API_BASE = window.location.origin + "/api";

let sessionId = null;
let xaiMode = "simple";      // "simple" | "tech"
let lastData = null;          // son /chat cevabı (XAI re-render için)
let scenarioQueue = [];       // hazır senaryonun kalan mesajları

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

const MOTIVATION_TR = {
    money: "maddi kazanç", science: "bilim/araştırma", prestige: "prestij",
    interest: "ilgi/tutku", family: "aile", unknown: "henüz belirsiz",
};

const AXIS_TR = {
    field: "alan seçimi", university: "üniversite seçimi", department: "bölüm seçimi",
};

// ============ HAZIR SENARYOLAR ============
const DEMO_SCENARIOS = {
    tip_muh: {
        label: "Tıp mı mühendislik mi?",
        messages: [
            "selam ben Mert",
            "1200 falan bekliyorum",
            "aslında tıp da istiyorum, doktorluk hep hayalimdi ama bilgisayar da ilgimi çekiyor",
            "insanlara yardım etmek benim için önemli",
        ],
    },
    koc_itu: {
        label: "Koç vs İTÜ",
        messages: [
            "Merhaba, Zeynep ben",
            "800 civarı sıralamam var. Koç'tan tam burs teklifi aldım ama İTÜ'yü de düşünüyorum",
            "Maddi durum bizim için önemli açıkçası",
            "Peki mezun olduktan sonra iş bulma konusunda fark var mı?",
        ],
    },
    matematik: {
        label: "Matematik kaygısı",
        messages: [
            "merhaba",
            "1400 sıralamam var, İTÜ bilgisayar istiyorum ama açıkçası korkuyorum",
            "matematiğim çok iyi değil, kalırsam ne olur diye düşünüyorum",
            "peki destek var mı okulda zorlanırsam",
        ],
    },
    yz_compe: {
        label: "Yapay Zeka mı Bilgisayar mı?",
        messages: [
            "Selam, ben Ege",
            "Sıralamam 1800. Yapay zeka mühendisliği mi bilgisayar mühendisliği mi karar veremiyorum",
            "Hedefim machine learning engineer olmak",
            "İkisinin farkı tam olarak ne?",
        ],
    },
    aile: {
        label: "Aile baskısı (ODTÜ)",
        messages: [
            "merhaba",
            "1100 sıralamam var, ben İTÜ bilgisayar istiyorum ama ailem ODTÜ istiyor illa",
            "babam ODTÜ mezunu, oranın daha iyi olduğunu söylüyor",
            "aileme nasıl anlatabilirim bilmiyorum",
        ],
    },
    para: {
        label: "Para motivasyonu",
        messages: [
            "selam",
            "900 sıram var. açık konuşayım benim için önemli olan para kazanmak",
            "hangi bölüm daha çok kazandırır? yazılımcılar gerçekten iyi kazanıyor mu",
            "yurt dışına gitmek de mantıklı mı maaş için",
        ],
    },
    maddi_destek: {
        label: "Maddi kaygı ve burs",
        messages: [
            "Merhaba, sıralamam 800 civarında",
            "İTÜ Bilgisayar istiyorum ama ailemin masrafları karşılaması zor",
            "Bu sıralamayla ne kadar burs alabilirim, koşulları neler?",
            "Yurt ve yemek desteği de var mı?",
        ],
    },
    girisimcilik: {
        label: "Girişimcilik ve İTÜ Çekirdek",
        messages: [
            "Selam, 800 sıralamam var ve yazılım girişimi kurmak istiyorum",
            "İTÜ Çekirdek bu konuda gerçekten ne kadar güçlü?",
            "Somut şirketleşme ve yatırım verileri var mı?",
            "Ben öğrenci olarak hangi avantajlardan yararlanabilirim?",
        ],
    },
};

// ============ DOM ============
const messagesEl = document.getElementById("messages");
const inputEl = document.getElementById("messageInput");
const chatForm = document.getElementById("chatForm");
const submitBtn = chatForm.querySelector("button[type='submit']");
const xaiContent = document.getElementById("xaiContent");

const sessionIdEl = document.getElementById("sessionId");
const fsmStateEl = document.getElementById("fsmState");
const turnCountEl = document.getElementById("turnCount");
const candNameEl = document.getElementById("candName");
const indecisionMainEl = document.getElementById("indecisionMain");
const motivationEl = document.getElementById("motivation");
const yksRankEl = document.getElementById("yksRank");
const engagementEl = document.getElementById("engagement");
const stageBadgeEl = document.getElementById("stageBadge");

const scenarioSelect = document.getElementById("scenarioSelect");
const scenarioStartBtn = document.getElementById("scenarioStartBtn");
const scenarioNextBtn = document.getElementById("scenarioNextBtn");
const scenarioRemainingEl = document.getElementById("scenarioRemaining");

// Senaryo dropdown doldur
Object.entries(DEMO_SCENARIOS).forEach(([key, sc]) => {
    const opt = document.createElement("option");
    opt.value = key;
    opt.textContent = sc.label;
    scenarioSelect.appendChild(opt);
});

// ============ EVENT'LER ============
document.getElementById("newSessionBtn").addEventListener("click", () => startNewSession());

document.getElementById("resetBtn").addEventListener("click", async () => {
    if (!sessionId) return;
    if (!confirm("Bu session'ı silmek istediğine emin misin?")) return;
    await fetch(`${API_BASE}/session/${sessionId}`, { method: "DELETE" });
    startNewSession();
});

document.getElementById("exportBtn").addEventListener("click", exportTranscript);

document.getElementById("xaiModeSimple").addEventListener("click", () => setXaiMode("simple"));
document.getElementById("xaiModeTech").addEventListener("click", () => setXaiMode("tech"));

scenarioStartBtn.addEventListener("click", async () => {
    const key = scenarioSelect.value;
    if (!key) { alert("Önce bir senaryo seç."); return; }
    await startNewSession();
    scenarioQueue = [...DEMO_SCENARIOS[key].messages];
    appendSystemMsg(`Senaryo başladı: "${DEMO_SCENARIOS[key].label}" — ${scenarioQueue.length} mesaj adım adım oynatılacak.`);
    await playNextScenarioMessage();
});

scenarioNextBtn.addEventListener("click", playNextScenarioMessage);

chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = inputEl.value.trim();
    if (!text) return;
    await sendMessage(text);
});

// ============ SENARYO OYNATMA ============
async function playNextScenarioMessage() {
    if (scenarioQueue.length === 0) {
        scenarioNextBtn.style.display = "none";
        appendSystemMsg("Senaryo tamamlandı. Konuşmaya elle devam edebilirsin.");
        return;
    }
    const msg = scenarioQueue.shift();
    updateScenarioButtons();
    await sendMessage(msg);
    updateScenarioButtons();
}

function updateScenarioButtons() {
    if (scenarioQueue.length > 0) {
        scenarioNextBtn.style.display = "block";
        scenarioRemainingEl.textContent = scenarioQueue.length;
    } else {
        scenarioNextBtn.style.display = "none";
    }
}

// ============ SESSION ============
async function startNewSession() {
    const res = await fetch(`${API_BASE}/session/new`, { method: "POST" });
    const data = await res.json();
    sessionId = data.session_id;
    scenarioQueue = [];
    lastData = null;
    updateScenarioButtons();

    sessionIdEl.textContent = sessionId;
    fsmStateEl.textContent = STAGE_TR.S1_GREETING;
    stageBadgeEl.textContent = STAGE_TR.S1_GREETING;
    turnCountEl.textContent = "0";
    candNameEl.textContent = "—";
    indecisionMainEl.textContent = "—";
    motivationEl.textContent = "—";
    yksRankEl.textContent = "?";
    engagementEl.textContent = "—";
    const fsmLink = document.getElementById("fsmDiagramLink");
    if (fsmLink) fsmLink.href = `/fsm.html?session=${sessionId}`;

    messagesEl.innerHTML = "";
    xaiContent.innerHTML = '<p class="muted">İlk mesajı gönderdiğinizde bot\'un neden bu şekilde cevap verdiği burada görünecek.</p>';
    appendSystemMsg("Yeni görüşme başladı. Mesaj yaz veya soldan hazır senaryo seç.");
}

// ============ MESAJ ============
async function sendMessage(text) {
    appendMsg("user", text);
    inputEl.value = "";
    submitBtn.disabled = true;

    const typingEl = document.createElement("div");
    typingEl.className = "typing";
    typingEl.textContent = "Neco yazıyor…";
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
        lastData = data;

        appendMsg("assistant", data.response_text, {
            argument: factLabel(data.rag?.facts?.[0]) || data.xai_meta.argument_label,
            fsm: `${data.xai_meta.fsm_from} → ${data.xai_meta.fsm_to}`,
        });

        updateSidebar(data);
        renderXAI();
    } catch (err) {
        typingEl.remove();
        appendSystemMsg(`Bağlantı hatası: ${err.message}`);
    } finally {
        submitBtn.disabled = false;
        inputEl.focus();
    }
}

function appendMsg(role, text, meta = null) {
    const el = document.createElement("div");
    el.className = `msg ${role}`;

    const textEl = document.createElement("div");
    textEl.textContent = text;
    el.appendChild(textEl);

    if (meta && role === "assistant" && xaiMode === "tech") {
        const metaEl = document.createElement("div");
        metaEl.className = "meta";
        const argChip = document.createElement("span");
        argChip.className = "chip arg";
        argChip.textContent = meta.argument;
        metaEl.appendChild(argChip);
        const fsmChip = document.createElement("span");
        fsmChip.className = "chip fsm";
        fsmChip.textContent = meta.fsm;
        metaEl.appendChild(fsmChip);
        el.appendChild(metaEl);
    }
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

// ============ SIDEBAR ============
const RISK_TR = { safe: "Güvenli", borderline: "Sınırda", hard: "Zor", unknown: "?" };
const DEPT_TR = {
    bilgisayar: "Bilgisayar", yapay_zeka_veri: "YZ-Veri",
    elektronik_haberlesme: "Elektronik", elektrik: "Elektrik",
    kontrol_otomasyon: "Kontrol-Oto.", ucak: "Uçak", uzay: "Uzay",
    makine: "Makine", endustri: "Endüstri", matematik: "Matematik",
    siber_guvenlik: "Siber Güv.", insaat: "İnşaat", gemi: "Gemi", kimya: "Kimya",
    yazilim: "Yazılım",
};
const STAGE_DECISION_TR = { kesif: "keşif", kiyaslama: "kıyaslama", itiraz: "itiraz", kapanis: "kapanış" };
const CONSTRAINT_TR = {
    city_istanbul: "İstanbul", public_university: "Devlet üniv.",
    cost_sensitivity: "Maliyet", housing_needed: "Yurt",
    family_influence: "Aile etkisi", english_medium: "İngilizce",
    abroad_goal: "Yurt dışı", campus_social: "Sosyal kampüs",
};
const TOPIC_TR = {
    faculty_research: "Hocalar ve öğrenci iletişimi",
    teaching_quality: "Ders anlatımı",
    academic_workload: "Ders ve sınav düzeni",
    technical_resources: "Laboratuvar ve teknik imkânlar",
    research_projects: "Araştırma ve projeler",
    curriculum_year1: "Birinci sınıf dersleri",
    curriculum_details: "Müfredat ayrıntıları",
    curriculum_overview: "Bölümün içeriği",
    difficulty: "Derslerin zorluk düzeyi",
    housing_details: "Yurt yaşamı",
    financial_support: "Burs ve maddi destek",
    campus_life: "Kampüs yaşamı",
    clubs_teams: "Kulüpler ve takımlar",
    career_evidence: "Kariyer ve işe geçiş",
    differentiators: "İTÜ Bilgisayar'ın farkları",
    comparison: "Üniversite karşılaştırması",
};

function topicLabel(topic) {
    return TOPIC_TR[topic] || topic.replaceAll("_", " ");
}

function factLabel(fact) {
    if (!fact) return "Kaynaklı bölüm bilgisi";
    if (fact.label) return fact.label;
    const id = fact.id || "";
    if (id.includes("faculty")) return "Akademik kadro ve hocalar";
    if (id.includes("curriculum")) return "Dersler ve müfredat";
    if (id.includes("housing") || id.includes("dorm")) return "Yurt ve barınma";
    if (id.includes("career") || id.includes("employment")) return "Kariyer ve iş olanakları";
    if (id.includes("campus")) return "Kampüs yaşamı";
    if (id.includes("scholarship")) return "Burs ve destekler";
    return "Kaynaklı bölüm bilgisi";
}

function updateSidebar(data) {
    const stageTr = STAGE_TR[data.fsm_state] || data.fsm_state;
    fsmStateEl.textContent = stageTr;
    stageBadgeEl.textContent = stageTr;
    turnCountEl.textContent = data.turn_count;

    const p = data.profile || {};
    const factors = data.xai_meta.decision_factors || {};
    candNameEl.textContent = p.display_name || "—";
    indecisionMainEl.textContent = AXIS_TR[factors.main_indecision_axis] || "—";
    motivationEl.textContent = MOTIVATION_TR[factors.dominant_motivation] || factors.dominant_motivation || "—";
    yksRankEl.textContent = p.yks_rank ? `${p.yks_rank}` : "?";
    engagementEl.textContent = (p.engagement_level ?? 0).toFixed(2);

    // Risk bandı — adayın masasındaki HER bölüm için ayrı (2800'lü robotik adaya
    // "Bilgisayar zor" yerine "Bilgisayar zor · Kontrol güvenli" gösterilir)
    const bands = data.academic?.risk_bands || [];
    const riskEl = document.getElementById("riskBand");
    if (bands.length > 1) {
        riskEl.className = "risk-multi";
        riskEl.innerHTML = bands.map(b =>
            `<span class="risk-pill ${b.band}" title="taban ~${b.cutoff_2025 ?? "?"}">${escapeHtml(DEPT_TR[b.department] || b.department)}: ${RISK_TR[b.band] || b.band}</span>`
        ).join(" ");
    } else {
        const band = data.academic?.risk_band || "unknown";
        riskEl.className = `risk-pill ${band}`;
        riskEl.textContent = RISK_TR[band] || band;
    }

    // Karar aşaması
    const stage = p.indecision?.decision_stage || "kesif";
    document.getElementById("decisionStage").textContent = STAGE_DECISION_TR[stage] || stage;

    // Bilinen kısıtlar
    const constraints = p.constraints || {};
    const known = Object.entries(constraints).filter(([, v]) => v !== null && v !== undefined);
    const rowEl = document.getElementById("constraintsRow");
    const listEl = document.getElementById("constraintsList");
    if (known.length > 0) {
        rowEl.style.display = "block";
        listEl.innerHTML = known.map(([k, v]) => {
            const label = CONSTRAINT_TR[k] || k;
            const val = typeof v === "boolean" ? (v ? "✓" : "✗") : v.toFixed(1);
            return `<span class="constraint-chip">${escapeHtml(label)}: ${val}</span>`;
        }).join("");
    } else {
        rowEl.style.display = "none";
    }
}

// ============ XAI PANEL ============
function setXaiMode(mode) {
    xaiMode = mode;
    document.getElementById("xaiModeSimple").classList.toggle("active", mode === "simple");
    document.getElementById("xaiModeTech").classList.toggle("active", mode === "tech");
    renderXAI();
}

function renderXAI() {
    if (!lastData) return;
    if (xaiMode === "simple") renderXAISimple(lastData);
    else renderXAITech(lastData);
}

function renderXAISimple(data) {
    const meta = data.xai_meta;
    const factors = meta.decision_factors || {};
    const stage = STAGE_TR[meta.fsm_to] || meta.fsm_to;
    const motivation = MOTIVATION_TR[factors.dominant_motivation] || "henüz belirsiz";
    const axis = AXIS_TR[factors.main_indecision_axis] || "—";
    const rank = factors.yks_rank ? `${factors.yks_rank}` : "henüz bilinmiyor";
    const route = factors.route || {};
    const utility = factors.utility || {};
    const answerFocus = factLabel(data.rag?.facts?.[0]);

    const prov = data.profile?.provenance || {};
    const facts = Object.entries(prov).filter(([, v]) => v.confidence >= 0.75).map(([k]) => k);
    const guesses = Object.entries(prov).filter(([, v]) => v.confidence < 0.75).map(([k]) => k);

    xaiContent.innerHTML = `
        <div class="card simple-card">
            <h4>Şu An Ne Oluyor?</h4>
            <p>Neco <strong>${escapeHtml(stage)}</strong> aşamasında.</p>
        </div>
        <div class="card simple-card">
            <h4>Bu Turda Ne Yaptı?</h4>
            <p><strong>${escapeHtml(answerFocus)}</strong> odağında doğrudan cevap verdi.</p>
        </div>
        <div class="card simple-card">
            <h4>Neden?</h4>
            <p>${route.primary_topic && route.primary_topic !== "general"
                ? `Son mesajda <strong>${escapeHtml(topicLabel(route.primary_topic))}</strong> konusu yakalandı; güncel soru önce cevaplandı.`
                : `Adayın YKS sırası <strong>${escapeHtml(rank)}</strong>, baskın motivasyonu <strong>${escapeHtml(motivation)}</strong> ve ana kararsızlığı <strong>${escapeHtml(axis)}</strong> olduğu için bu yaklaşım seçildi.`}</p>
            ${utility.overridden ? `<p style="margin-top:6px;color:var(--gray-500)">Utility katmanı, aday uyumu nedeniyle ilk bandit seçimini düzeltti.</p>` : ""}
        </div>
        ${facts.length > 0 || guesses.length > 0 ? `
        <div class="card simple-card">
            <h4>Aday Hakkında Bildiklerim</h4>
            ${facts.length > 0 ? `<p><strong>Kesin</strong> (aday söyledi): ${facts.slice(0, 8).map(escapeHtml).join(", ")}</p>` : ""}
            ${guesses.length > 0 ? `<p style="margin-top:6px;color:var(--gray-500)"><strong>Tahmin</strong> (çıkarım): ${guesses.slice(0, 6).map(escapeHtml).join(", ")}</p>` : ""}
        </div>` : ""}
        ${data.ethics_check && !data.ethics_check.clean ? `
        <div class="card simple-card warn">
            <h4>Etik Filtre</h4>
            <p>⚠ Cevap etik filtre tarafından ${data.ethics_check.replaced ? "değiştirildi" : "yumuşatıldı"}.</p>
        </div>` : ""}
        ${data.fact_gate && !data.fact_gate.clean ? `
        <div class="card simple-card warn">
            <h4>Fact Gate</h4>
            <p>Kaynak disi iddia yakalandi; cevap guvenli metinle degistirildi.</p>
        </div>` : ""}
        ${data.rag?.facts?.length ? `
        <div class="card simple-card">
            <h4>Kullanılan Kaynaklı Bilgiler</h4>
            <p>Konu: ${escapeHtml((data.rag.topics || []).map(topicLabel).join(", "))}</p>
            <p style="margin-top:6px;color:var(--gray-500)">${data.rag.facts.slice(0, 3).map(f => escapeHtml(factLabel(f))).join(" · ")}</p>
        </div>` : ""}
    `;
}

function renderXAITech(data) {
    const meta = data.xai_meta;
    const factors = meta.decision_factors || {};
    const route = factors.route || {};
    const utility = factors.utility || {};
    const reward = data.reward_breakdown_previous_turn;
    xaiContent.innerHTML = `
        <div class="card">
            <h4>Seçilen Argüman</h4>
            <p><strong>${escapeHtml(meta.argument_label)}</strong> <code>${escapeHtml(meta.argument_id)}</code></p>
        </div>

        <div class="card">
            <h4>FSM Geçişi</h4>
            <p><span class="fsm-transition">${escapeHtml(meta.fsm_from)} <span class="arrow">→</span> ${escapeHtml(meta.fsm_to)}</span></p>
            <p style="margin-top:8px;color:var(--gray-500);font-size:11.5px;">Trigger: <code>${escapeHtml(meta.fsm_trigger)}</code></p>
        </div>

        <div class="card">
            <h4>Neden Bu Karar?</h4>
            <p>${escapeHtml(meta.reason_tr)}</p>
        </div>

        <div class="card">
            <h4>Karar Faktörleri</h4>
            <div class="factor"><span class="key">user_type</span><span>${escapeHtml(factors.user_type ?? "-")}</span></div>
            <div class="factor"><span class="key">bandit_score</span><span>${(factors.bandit_score ?? 0).toFixed(3)}</span></div>
            <div class="factor"><span class="key">exploration_bonus</span><span>${(factors.exploration_bonus ?? 0).toFixed(3)}</span></div>
            <div class="factor"><span class="key">fsm_weight</span><span>${(factors.fsm_weight ?? 0).toFixed(2)}</span></div>
            <div class="factor"><span class="key">yks_rank</span><span>${factors.yks_rank ?? "?"}</span></div>
            <div class="factor"><span class="key">dominant_motivation</span><span>${escapeHtml(factors.dominant_motivation ?? "-")}</span></div>
            <div class="factor"><span class="key">indecision_axis</span><span>${escapeHtml(factors.main_indecision_axis ?? "-")}</span></div>
        </div>

        <div class="card">
            <h4>Current-turn Router</h4>
            <div class="factor"><span class="key">topic</span><span>${escapeHtml(route.primary_topic || "general")}</span></div>
            <div class="factor"><span class="key">confidence</span><span>${(route.confidence ?? 0).toFixed(2)}</span></div>
            <div class="factor"><span class="key">forced_argument</span><span>${escapeHtml(route.forced_argument_id || "-")}</span></div>
        </div>

        <div class="card">
            <h4>Negotiation Utility</h4>
            <div class="factor"><span class="key">override</span><span>${utility.overridden ? "evet" : "hayır"}</span></div>
            <div class="factor"><span class="key">original</span><span>${escapeHtml(utility.original_argument_id || meta.argument_id)}</span></div>
            <div class="factor"><span class="key">margin</span><span>${(utility.margin ?? 0).toFixed(3)}</span></div>
        </div>

        ${factors.alternatives && factors.alternatives.length > 0 ? `
        <div class="card">
            <h4>Alternatif Argümanlar</h4>
            ${factors.alternatives.slice(0, 3).map(alt => `
                <div class="factor">
                    <span class="key">${escapeHtml(alt[0])}</span>
                    <span>${(alt[1] ?? 0).toFixed(3)}</span>
                </div>
            `).join("")}
        </div>` : ""}

        <div class="card">
            <h4>Etik Filtre</h4>
            <p>${data.ethics_check?.clean ? "✓ Temiz" : (data.ethics_check?.replaced ? "⚠ Yanıt güvenli metinle değiştirildi" : "⚠ Yumuşatıldı")}</p>
        </div>

        <div class="card">
            <h4>Fact Gate</h4>
            <p>${data.fact_gate?.clean ? "✓ Kaynak kontrolünden geçti" : "⚠ Kaynak dışı iddia yakalandı"}</p>
            ${data.fact_gate?.violations?.length ? `<p style="margin-top:6px;color:var(--gray-500);font-size:11.5px;">${escapeHtml(JSON.stringify(data.fact_gate.violations))}</p>` : ""}
        </div>

        ${data.rag?.facts?.length ? `
        <div class="card">
            <h4>RAG Bilgileri</h4>
            <p style="margin-bottom:8px;color:var(--gray-500);font-size:11.5px;">Konu: ${escapeHtml((data.rag.topics || []).map(topicLabel).join(", "))}</p>
            ${data.rag.facts.slice(0, 4).map(f => `
                <div class="factor" title="${escapeHtml(f.text)}">
                    <span class="key">${escapeHtml(factLabel(f))}</span>
                    <span>${escapeHtml(f.source || "-")} ${escapeHtml(f.year || "")}</span>
                </div>
            `).join("")}
        </div>` : ""}

        <div class="card">
            <h4>Ödül (önceki tur)</h4>
            <p>${data.reward_previous_turn !== null && data.reward_previous_turn !== undefined ? data.reward_previous_turn.toFixed(3) : "(ilk tur)"}</p>
            ${reward ? `
                <div class="factor"><span class="key">engagement</span><span>${(reward.engagement ?? 0).toFixed(3)}</span></div>
                <div class="factor"><span class="key">argument_effectiveness</span><span>${(reward.argument_effectiveness ?? 0).toFixed(3)}</span></div>
                <div class="factor"><span class="key">reaction</span><span>${escapeHtml(reward.reaction || "-")}</span></div>
            ` : ""}
        </div>

        <div class="card">
            <h4>Sesli Yanıt</h4>
            <div class="factor"><span class="key">word_count</span><span>${data.speech_check?.word_count ?? "-"}</span></div>
            <div class="factor"><span class="key">trimmed</span><span>${data.speech_check?.trimmed ? "evet" : "hayır"}</span></div>
        </div>

        ${renderProvenanceCard(data)}
    `;
}

function renderProvenanceCard(data) {
    const prov = data.profile?.provenance || {};
    const entries = Object.entries(prov);
    if (entries.length === 0) return "";
    const rows = entries
        .sort((a, b) => b[1].confidence - a[1].confidence)
        .slice(0, 12)
        .map(([k, v]) => `
            <div class="factor">
                <span class="key">${escapeHtml(k)}</span>
                <span title="turn ${v.source_turn}→${v.updated_turn}">${v.confidence >= 0.75 ? "●" : "○"} ${v.confidence.toFixed(2)}</span>
            </div>`).join("");
    return `
        <div class="card">
            <h4>Profil Kanıt Durumu (● kesin / ○ tahmin)</h4>
            ${rows}
        </div>`;
}

// ============ EXPORT ============
async function exportTranscript() {
    if (!sessionId) { alert("Aktif session yok."); return; }
    const res = await fetch(`${API_BASE}/session/${sessionId}`);
    if (!res.ok) { alert("Session verisi alınamadı — henüz mesaj yok olabilir."); return; }
    const data = await res.json();

    const lines = [`# Görüşme Transcript — ${data.session_id}`, ""];
    lines.push(`- Aday: ${data.display_name || "(isimsiz)"}`);
    lines.push(`- Tur sayısı: ${data.turn_count}`);
    lines.push(`- Son aşama: ${STAGE_TR[data.fsm_state] || data.fsm_state}`);
    lines.push("");
    lines.push("## Konuşma");
    lines.push("");
    data.messages.forEach(m => {
        const who = m.role === "user" ? "🧑 Aday" : "🤖 Neco";
        lines.push(`**${who}:** ${m.text}`);
        lines.push("");
    });
    lines.push("## Karar Logları");
    lines.push("");
    data.strategy_logs.forEach(s => {
        lines.push(`- Turn ${s.turn}: \`${s.fsm_from} → ${s.fsm_to}\` · argüman: \`${s.argument_id}\`` +
                   (s.reward != null ? ` · önceki tur ödülü: ${s.reward.toFixed(2)}` : ""));
    });

    const blob = new Blob([lines.join("\n")], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `transcript_${data.session_id}.md`;
    a.click();
    URL.revokeObjectURL(url);
}

function escapeHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    }[c]));
}

// Startup
startNewSession();
