// FSM Diagram - static layout + optional session path highlight

const API_BASE = window.location.origin + "/api";
const svgNS = "http://www.w3.org/2000/svg";

// Hand-crafted layout for 11 states — logical flow top-to-bottom
const STATE_POSITIONS = {
    "S1_GREETING":              { x: 120, y: 80,  w: 160, h: 50 },
    "S2_INDECISION_PROBE":      { x: 380, y: 80,  w: 200, h: 50 },
    "S2R_PROFILE_UPDATE":       { x: 680, y: 80,  w: 200, h: 50 },
    "S0_FALLBACK":              { x: 680, y: 220, w: 160, h: 50 },
    "S3_ARGUMENT_SELECTION":    { x: 380, y: 220, w: 200, h: 50 },
    "S4_ARGUMENT_DELIVERY":     { x: 380, y: 350, w: 200, h: 50 },
    "S5_RECEPTION_EVAL":        { x: 380, y: 480, w: 200, h: 50 },
    "S7_CONCERN_HANDLING":      { x: 120, y: 480, w: 200, h: 50 },
    "S6_RAG_DEEP_DIVE":         { x: 680, y: 480, w: 200, h: 50 },
    "S8_IDEAL_MATCH_SUMMARY":   { x: 380, y: 610, w: 220, h: 50 },
    "S9_CLOSING":               { x: 380, y: 730, w: 220, h: 50 },
};

const CANVAS_W = 1000;
const CANVAS_H = 830;

const TERMINAL_STATES = new Set(["S8_IDEAL_MATCH_SUMMARY", "S9_CLOSING"]);
const SAFETY_STATES = new Set(["S0_FALLBACK"]);

let currentState = null;
let visitedTransitions = new Set(); // "from|to" keys
let visitedStates = new Set();

document.getElementById("loadPathBtn").addEventListener("click", async () => {
    const sid = document.getElementById("sidInput").value.trim();
    if (!sid) { alert("Session ID gir."); return; }
    await loadSessionPath(sid);
});

async function loadFSM() {
    const res = await fetch(`${API_BASE}/fsm`);
    const data = await res.json();
    renderDiagram(data);
}

async function loadSessionPath(sid) {
    try {
        const res = await fetch(`${API_BASE}/fsm/session/${sid}`);
        if (!res.ok) {
            document.getElementById("pathList").innerHTML = `<p style="color:#dc2626">Session bulunamadı.</p>`;
            return;
        }
        const data = await res.json();
        currentState = data.current_state;
        visitedTransitions = new Set(data.path.map(p => `${p.from}|${p.to}`));
        visitedStates = new Set();
        data.path.forEach(p => { visitedStates.add(p.from); visitedStates.add(p.to); });
        renderPath(data);
        const fsmRes = await fetch(`${API_BASE}/fsm`);
        const fsmData = await fsmRes.json();
        renderDiagram(fsmData);
    } catch (err) {
        alert("Hata: " + err.message);
    }
}

function renderPath(data) {
    const list = document.getElementById("pathList");
    if (!data.path || data.path.length === 0) {
        list.innerHTML = `<p style="color:#9ca3af">Bu session'da henüz turn yok. Şu anki state: <code>${data.current_state}</code></p>`;
        return;
    }
    list.innerHTML = `
        <p style="margin-bottom:10px"><strong>Şu anki state:</strong> <code>${data.current_state}</code> · <strong>${data.path.length}</strong> turn</p>
    ` + data.path.map(p => `
        <div class="path-entry">
            <span class="turn-badge">Turn ${p.turn}</span>
            <div class="transition">${p.from} → ${p.to}</div>
            <div class="trigger">trigger: ${p.trigger}</div>
            <div class="argument">argument: ${p.argument || "-"}</div>
        </div>
    `).join("");
}

function renderDiagram(data) {
    const container = document.getElementById("diagramContainer");
    container.innerHTML = "";
    const svg = document.createElementNS(svgNS, "svg");
    svg.setAttribute("width", CANVAS_W);
    svg.setAttribute("height", CANVAS_H);
    svg.setAttribute("viewBox", `0 0 ${CANVAS_W} ${CANVAS_H}`);

    // Arrowhead marker definitions
    const defs = document.createElementNS(svgNS, "defs");
    defs.innerHTML = `
        <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" class="arrowhead"/>
        </marker>
        <marker id="arrow-visited" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" class="arrowhead visited"/>
        </marker>
    `;
    svg.appendChild(defs);

    // Group transitions by (from,to) so we can stack multiple triggers on same edge
    const edgeMap = new Map();
    data.transitions.forEach(t => {
        // Skip self-loops with "no_match" to reduce clutter (still draw one loop per state if it exists)
        const key = `${t.from}|${t.to}`;
        if (!edgeMap.has(key)) edgeMap.set(key, []);
        edgeMap.get(key).push(t);
    });

    // Draw edges first (under nodes)
    edgeMap.forEach((triggers, key) => {
        const [from, to] = key.split("|");
        const fromPos = STATE_POSITIONS[from];
        const toPos = STATE_POSITIONS[to];
        if (!fromPos || !toPos) return;

        const isVisited = visitedTransitions.has(key);
        const isSelfLoop = from === to;

        if (isSelfLoop) {
            drawSelfLoop(svg, fromPos, triggers, isVisited);
        } else {
            drawEdge(svg, fromPos, toPos, triggers, isVisited);
        }
    });

    // Draw nodes on top
    Object.entries(STATE_POSITIONS).forEach(([state, pos]) => {
        drawNode(svg, state, pos);
    });

    container.appendChild(svg);
}

function drawEdge(svg, fromPos, toPos, triggers, isVisited) {
    const fromCenter = { x: fromPos.x + fromPos.w/2, y: fromPos.y + fromPos.h/2 };
    const toCenter   = { x: toPos.x + toPos.w/2,     y: toPos.y + toPos.h/2 };

    // Find intersection points on rectangle edges
    const from = rectIntersect(fromPos, fromCenter, toCenter);
    const to   = rectIntersect(toPos, toCenter, fromCenter);

    const g = document.createElementNS(svgNS, "g");

    const path = document.createElementNS(svgNS, "path");
    path.setAttribute("d", `M ${from.x} ${from.y} L ${to.x} ${to.y}`);
    path.setAttribute("class", `edge forward ${isVisited ? "visited" : ""}`);
    path.setAttribute("marker-end", isVisited ? "url(#arrow-visited)" : "url(#arrow)");
    g.appendChild(path);

    // Label — put first trigger on midpoint (and (+N) if multiple)
    const mx = (from.x + to.x) / 2;
    const my = (from.y + to.y) / 2;
    const label = triggers.length === 1
        ? triggers[0].trigger
        : `${triggers[0].trigger} (+${triggers.length - 1})`;

    const labelBg = document.createElementNS(svgNS, "rect");
    const textWidth = label.length * 5.2 + 6;
    labelBg.setAttribute("x", mx - textWidth/2);
    labelBg.setAttribute("y", my - 8);
    labelBg.setAttribute("width", textWidth);
    labelBg.setAttribute("height", 12);
    labelBg.setAttribute("fill", "white");
    labelBg.setAttribute("opacity", "0.85");
    g.appendChild(labelBg);

    const text = document.createElementNS(svgNS, "text");
    text.setAttribute("x", mx);
    text.setAttribute("y", my + 1);
    text.setAttribute("class", `edge-label ${isVisited ? "visited" : ""}`);
    text.setAttribute("text-anchor", "middle");
    text.textContent = label;
    g.appendChild(text);

    // Tooltip via <title> — includes all triggers if multiple
    const title = document.createElementNS(svgNS, "title");
    title.textContent = triggers.map(t => `${t.trigger} (weight ${t.weight}, pred ${t.predicate})`).join("\n");
    g.appendChild(title);

    svg.appendChild(g);
}

function drawSelfLoop(svg, pos, triggers, isVisited) {
    const startX = pos.x + pos.w * 0.75;
    const startY = pos.y;
    const endX = pos.x + pos.w * 0.25;
    const endY = pos.y;
    const loopHeight = 30;

    const g = document.createElementNS(svgNS, "g");
    const path = document.createElementNS(svgNS, "path");
    path.setAttribute("d", `M ${startX} ${startY} C ${startX + 20} ${startY - loopHeight}, ${endX - 20} ${endY - loopHeight}, ${endX} ${endY}`);
    path.setAttribute("class", `edge self-loop ${isVisited ? "visited" : ""}`);
    path.setAttribute("marker-end", isVisited ? "url(#arrow-visited)" : "url(#arrow)");
    g.appendChild(path);

    const label = triggers.length === 1 ? triggers[0].trigger : `${triggers[0].trigger} (+${triggers.length - 1})`;
    const text = document.createElementNS(svgNS, "text");
    text.setAttribute("x", (startX + endX) / 2);
    text.setAttribute("y", startY - loopHeight - 4);
    text.setAttribute("class", `edge-label ${isVisited ? "visited" : ""}`);
    text.setAttribute("text-anchor", "middle");
    text.textContent = label;
    g.appendChild(text);

    const title = document.createElementNS(svgNS, "title");
    title.textContent = triggers.map(t => `${t.trigger} (weight ${t.weight})`).join("\n");
    g.appendChild(title);

    svg.appendChild(g);
}

function drawNode(svg, state, pos) {
    const g = document.createElementNS(svgNS, "g");
    let cls = "state-node";
    if (state === currentState) cls += " current";
    else if (visitedStates.has(state)) cls += " visited";
    if (TERMINAL_STATES.has(state)) cls += " terminal";
    if (SAFETY_STATES.has(state)) cls += " safety";
    g.setAttribute("class", cls);

    const rect = document.createElementNS(svgNS, "rect");
    rect.setAttribute("x", pos.x);
    rect.setAttribute("y", pos.y);
    rect.setAttribute("width", pos.w);
    rect.setAttribute("height", pos.h);
    rect.setAttribute("rx", 8);
    g.appendChild(rect);

    const text = document.createElementNS(svgNS, "text");
    text.setAttribute("x", pos.x + pos.w / 2);
    text.setAttribute("y", pos.y + pos.h / 2 + 4);
    text.setAttribute("text-anchor", "middle");
    text.textContent = state;
    g.appendChild(text);

    svg.appendChild(g);
}

function rectIntersect(rect, from, to) {
    // Find intersection of line (from → to) with rectangle edges
    const cx = rect.x + rect.w / 2;
    const cy = rect.y + rect.h / 2;
    const dx = to.x - cx;
    const dy = to.y - cy;
    if (dx === 0 && dy === 0) return { x: cx, y: cy };

    const halfW = rect.w / 2;
    const halfH = rect.h / 2;
    const scale = Math.min(
        Math.abs(halfW / dx) || Infinity,
        Math.abs(halfH / dy) || Infinity
    );
    return { x: cx + dx * scale, y: cy + dy * scale };
}

// Startup
loadFSM();

// If URL has ?session=..., auto-load
const urlParams = new URLSearchParams(window.location.search);
const initialSid = urlParams.get("session");
if (initialSid) {
    document.getElementById("sidInput").value = initialSid;
    loadSessionPath(initialSid);
}
