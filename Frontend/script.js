// ========== CONFIG ==========
// For DEPLOYED backend (Render)
const API_URL = "https://phishing-detection-k2kh.onrender.com/predict";
const API_KEY = ""; // or "YOUR_SECRET_API_KEY" if you set one on Render

// // For LOCAL backend
// const API_URL = "http://127.0.0.1:5000/predict";
// const API_KEY = ""; // or "YOUR_SECRET_API_KEY" if you set one on your local server


// DOM
const urlEl = document.getElementById("url");
const checkBtn = document.getElementById("check");
const msg = document.getElementById("msg");
const historyEl = document.getElementById("history");
const resultLabel = document.getElementById("resultLabel");
const confidenceEl = document.getElementById("confidence");
const contribEl = document.getElementById("contrib");
const rawEl = document.getElementById("raw");
const busyEl = document.getElementById("busy");


// ===== UTIL =====
function setBusy(on){
    busyEl.style.visibility = on ? "visible" : "hidden";
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
            <div style="font-weight:600">${it.url}</div>
            <div class="muted">${new Date(it.t).toLocaleString()} — ${it.prediction} (${(it.confidence*100).toFixed(1)}%)</div>
        </div>
    `).join("");

    Array.from(historyEl.children).forEach(el=>{
        el.onclick = ()=>{
            const idx = +el.dataset.i;
            const h = loadHistory();
            urlEl.value = h[idx].url;
            runCheck(h[idx].url, true);
        };
    });
}


// ===== MAIN CHECK FUNCTION =====
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

        // show results
        resultLabel.textContent = data.prediction;
        confidenceEl.textContent = "Confidence: "+((data.confidence||0)*100).toFixed(1)+"%";
        rawEl.textContent = JSON.stringify(data, null, 2);

        contribEl.innerHTML = "";
        if(data.top_contributions?.length){
            data.top_contributions.slice(0,8).forEach(c=>{
                const li = document.createElement("li");
                li.innerHTML = `<div>${c.feature}</div><div class="muted">${(c.contribution || 0).toFixed(4)}</div>`;
                contribEl.appendChild(li);
            });
        } else {
            contribEl.innerHTML = `<li class="muted">No contributions</li>`;
        }

        if(!skipStore){
            const h = loadHistory();
            h.unshift({url, t:Date.now(), prediction:data.prediction, confidence:data.confidence});
            saveHistory(h);
        }

    }catch(err){
        rawEl.textContent = "Error: "+err.message;
        resultLabel.textContent = "Error";
        confidenceEl.textContent = "";
    }
    finally{
        setBusy(false);
    }
}


// ===== EVENT LISTENERS =====
checkBtn.onclick = ()=> runCheck(urlEl.value.trim());
document.getElementById("sample").onclick = ()=>{
    urlEl.value = "http://paypal.com.security-checkupdate.com/login";
};

renderHistory();
