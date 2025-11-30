// ========== CONFIG ==========
// For DEPLOYED backend (Render)
const API_URL = "https://phishing-detection-k2kh.onrender.com/predict";
const API_KEY = ""; // keep empty unless you use API_KEY and send header

// DOM
const urlEl = document.getElementById("url");
const checkBtn = document.getElementById("check");
const msg = document.getElementById("msg");
const historyEl = document.getElementById("history");
const rawEl = document.getElementById("raw");
const busyEl = document.getElementById("busy");

// Modal elements
const resultModal = document.getElementById("resultModal");
const modalBackdrop = document.getElementById("modalBackdrop");
const modalClose = document.getElementById("modalClose");
const modalTitle = document.getElementById("modalTitle");
const modalConfidence = document.getElementById("modalConfidence");
const modalContrib = document.getElementById("modalContrib");
const modalRaw = document.getElementById("modalRaw");

// util: show / hide modal
function openModal() {
    resultModal.style.display = "flex";
    resultModal.setAttribute("aria-hidden", "false");
}
function closeModal() {
    resultModal.style.display = "none";
    resultModal.setAttribute("aria-hidden", "true");
}
modalBackdrop.onclick = closeModal;
modalClose.onclick = closeModal;

// show busy spinner (we don't show right column now)
function setBusy(on){
    // busyEl may be missing in the compact UI; keep safe
    if (busyEl) busyEl.style.visibility = on ? "visible" : "hidden";
}

function loadHistory(){
    try { return JSON.parse(localStorage.getItem("phish_history") || "[]"); }
    catch { return []; }
}

function saveHistory(h){
    localStorage.setItem("phish_history", JSON.stringify(h.slice(0,30)));
    renderHistory();
}

function renderHistory(){
    const h = loadHistory();
    if(!h.length){
        historyEl.innerHTML = '<div class="muted">No history</div>';
        return;
    }

    historyEl.innerHTML = h.map((it,i)=>`
        <div class="history-item" data-i="${i}">
            <div style="font-weight:700">${it.url}</div>
            <div class="muted small">${new Date(it.t).toLocaleString()} — ${it.prediction} (${(it.confidence*100).toFixed(1)}%)</div>
        </div>
    `).join("");

    Array.from(historyEl.children).forEach(el=>{
        el.onclick = ()=>{ const idx = +el.dataset.i; const h = loadHistory(); urlEl.value = h[idx].url; runCheck(h[idx].url, true); };
    });
}

// render contributions into a given element
function renderContribList(targetEl, list){
    targetEl.innerHTML = "";
    if (Array.isArray(list) && list.length){
        const items = list.slice().sort((a,b)=> Math.abs(b.contribution||0)-Math.abs(a.contribution||0)).slice(0,8);
        items.forEach(c=>{
            const li = document.createElement("li");
            const val = (c.contribution==null?0:Number(c.contribution));
            let display = Math.abs(val) <= 1 ? (val*100).toFixed(2) + '%' : val.toFixed(4);
            li.innerHTML = `<div title="${c.feature}">${c.feature}</div><div class="last">${display}</div>`;
            targetEl.appendChild(li);
        });
    } else {
        targetEl.innerHTML = `<li class="muted">No contributions</li>`;
    }
}

// main check function: fetch API and open modal on success
async function runCheck(url, skipStore=false){
    if(!url){
        msg.textContent = "Enter a URL.";
        return;
    }
    msg.textContent = "";
    setBusy(true);

    try{
        const res = await fetch(API_URL, {
            method:"POST",
            headers:{
                "Content-Type":"application/json",
                ...(API_KEY ? {"x-api-key": API_KEY} : {})
            },
            body: JSON.stringify({ url })
        });

        if(!res.ok){
            const txt = await res.text();
            throw new Error("API Error: "+txt);
        }

        const data = await res.json();

        // open modal and populate content
        modalTitle.textContent = data.prediction || "Result";
        modalConfidence.textContent = (data.confidence == null) ? "Confidence: N/A" : "Confidence: " + (data.confidence*100).toFixed(1) + "%";
        renderContribList(modalContrib, data.top_contributions || []);
        modalRaw.textContent = JSON.stringify(data, null, 2);

        openModal();

        if(!skipStore){
            const h = loadHistory();
            h.unshift({url, t:Date.now(), prediction:data.prediction, confidence:data.confidence||0});
            saveHistory(h);
        }
    }catch(err){
        msg.textContent = "Error: " + err.message;
        console.error(err);
    }finally{
        setBusy(false);
    }
}

// events
checkBtn.onclick = ()=> runCheck(urlEl.value.trim());
document.getElementById("sample").onclick = ()=>{ urlEl.value = "http://paypal.com.security-checkupdate.com/login"; };

// initial render
renderHistory();
