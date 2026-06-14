import os
import streamlit.components.v1 as components

# =============================================================================
# AUTO-GENERAZIONE DEL FRONTEND (Per supporto a Streamlit Cloud / GitHub)
# =============================================================================
# Siccome su GitHub/Streamlit Cloud potrebbe mancare la cartella run_tracker_ui, 
# la creiamo dinamicamente in modo che l'app sia 100% autonoma.

_FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "run_tracker_ui")
_INDEX_PATH = os.path.join(_FRONTEND_DIR, "index.html")

if not os.path.exists(_FRONTEND_DIR):
    os.makedirs(_FRONTEND_DIR)

# Contenuto HTML fisso del componente GPS
_HTML_CONTENT = """<!DOCTYPE html>
<html>
<head>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;600;700&display=swap');
    body {
        margin: 0;
        padding: 0;
        background-color: transparent;
        color: #fff;
        font-family: 'Inter', sans-serif;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        box-sizing: border-box;
        padding: 1rem;
    }
    .dashboard {
        width: 100%;
        max-width: 400px;
        background: #111111;
        border-radius: 30px;
        padding: 2rem 1.5rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.6);
        border: 1px solid #333;
        text-align: center;
        position: relative;
    }
    .status-badge {
        display: inline-block;
        background-color: #222;
        color: #888;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 1.5rem;
        border: 1px solid #333;
    }
    .status-badge.active {
        background-color: rgba(126, 242, 213, 0.2);
        color: #7ef2d5;
        border-color: #7ef2d5;
    }
    .main-metric {
        margin-bottom: 2rem;
    }
    .main-metric .value {
        font-family: 'Anton', sans-serif;
        font-size: 5.5rem;
        line-height: 1;
        color: #7ef2d5;
    }
    .main-metric .unit {
        font-size: 1.2rem;
        color: #888;
        font-weight: 600;
        text-transform: uppercase;
    }
    .grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    .grid-card {
        background: #1a1a1a;
        border-radius: 16px;
        padding: 1rem;
        border: 1px solid #2a2a2a;
    }
    .grid-card .title {
        font-size: 0.8rem;
        color: #888;
        text-transform: uppercase;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .grid-card .val {
        font-family: 'Anton', sans-serif;
        font-size: 2rem;
        color: #fff;
    }
    .controls {
        display: flex;
        gap: 1rem;
        justify-content: center;
    }
    .btn {
        flex: 1;
        font-family: 'Anton', sans-serif;
        font-size: 1.2rem;
        padding: 1rem;
        border-radius: 16px;
        border: none;
        cursor: pointer;
        text-transform: uppercase;
        transition: all 0.2s;
    }
    .btn-start {
        background-color: #7ef2d5;
        color: #000;
        box-shadow: 0 4px 15px rgba(126, 242, 213, 0.2);
    }
    .btn-stop {
        background-color: #e74c3c;
        color: #fff;
        display: none;
    }
    .btn-resume {
        background-color: #f39c12;
        color: #fff;
        display: none;
    }
    .btn-finish {
        background-color: #3498db;
        color: #fff;
        display: none;
        margin-top: 1rem;
        width: 100%;
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
    }
    .btn:hover {
        transform: translateY(-2px);
        opacity: 0.9;
    }
    #errorMsg {
        color: #e74c3c;
        font-size: 0.85rem;
        margin-top: 1rem;
        font-weight: 600;
        display: none;
    }
</style>
</head>
<body>
    <div class="dashboard">
        <div class="status-badge" id="statusBadge">READY TO RUN</div>
        
        <div class="main-metric">
            <div class="value" id="distVal">0.00</div>
            <div class="unit">Kilometers</div>
        </div>

        <div class="grid">
            <div class="grid-card">
                <div class="title">Time</div>
                <div class="val" id="timeVal">00:00</div>
            </div>
            <div class="grid-card">
                <div class="title">Pace (min/km)</div>
                <div class="val" id="paceVal">--:--</div>
            </div>
            <div class="grid-card">
                <div class="title">Steps</div>
                <div class="val" id="stepsVal">0</div>
            </div>
            <div class="grid-card">
                <div class="title">Kcal</div>
                <div class="val" id="kcalVal">0</div>
            </div>
        </div>

        <div class="controls">
            <button class="btn btn-start" id="btnStart" onclick="startRun()">START RUN</button>
            <button class="btn btn-resume" id="btnResume" onclick="resumeRun()">RESUME</button>
            <button class="btn btn-stop" id="btnStop" onclick="stopRun()">PAUSE</button>
        </div>
        
        <button class="btn btn-finish" id="btnFinish" onclick="finishRun()">FINE CORSA E SALVA</button>
        
        <div id="errorMsg"></div>
    </div>

    <script>
        let pesoUtente = 70; // default
        
        // --- Streamlit Custom Component Native API ---
        function sendValueToStreamlit(value) {
            window.parent.postMessage({
                isStreamlitMessage: true,
                type: "setComponentValue",
                value: value
            }, "*");
        }

        function setFrameHeight(height) {
            window.parent.postMessage({
                isStreamlitMessage: true,
                type: "setFrameHeight",
                height: height
            }, "*");
        }

        window.addEventListener("message", function(event) {
            if (event.data.type === "streamlit:render") {
                const args = event.data.args;
                if (args && args.peso_utente) {
                    pesoUtente = args.peso_utente;
                }
                setFrameHeight(750);
            }
        });

        // Avvisa Streamlit che il componente è pronto
        window.parent.postMessage({
            isStreamlitMessage: true,
            type: "streamlit:componentReady",
            apiVersion: 1
        }, "*");
        
        // Imposta altezza iniziale sicura
        setFrameHeight(750);
        // ---------------------------------------------

        let isRunning = false;
        let watchId = null;
        let timerInterval = null;
        
        let elapsedTime = 0; // secondi
        let totalDistance = 0; // km
        let totalSteps = 0;
        let totalKcal = 0;
        
        let lastLat = null;
        let lastLon = null;
        
        // Array of coordinates [lon, lat] per pydeck
        let gpsPath = [];
        
        const btnStart = document.getElementById('btnStart');
        const btnStop = document.getElementById('btnStop');
        const btnResume = document.getElementById('btnResume');
        const btnFinish = document.getElementById('btnFinish');
        const statusBadge = document.getElementById('statusBadge');
        const errorMsg = document.getElementById('errorMsg');
        
        const distVal = document.getElementById('distVal');
        const timeVal = document.getElementById('timeVal');
        const paceVal = document.getElementById('paceVal');
        const stepsVal = document.getElementById('stepsVal');
        const kcalVal = document.getElementById('kcalVal');

        function calculateDistance(lat1, lon1, lat2, lon2) {
            const R = 6371;
            const dLat = (lat2 - lat1) * Math.PI / 180;
            const dLon = (lon2 - lon1) * Math.PI / 180;
            const a = 
                Math.sin(dLat/2) * Math.sin(dLat/2) +
                Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
                Math.sin(dLon/2) * Math.sin(dLon/2);
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
            return R * c; 
        }

        function formatTime(sec) {
            const m = Math.floor(sec / 60).toString().padStart(2, '0');
            const s = (sec % 60).toString().padStart(2, '0');
            return `${m}:${s}`;
        }

        function formatPace(paceSec) {
            if (paceSec <= 0 || !isFinite(paceSec)) return "--:--";
            const m = Math.floor(paceSec / 60);
            const s = Math.floor(paceSec % 60).toString().padStart(2, '0');
            return `${m}:${s}`;
        }

        function updateUI() {
            distVal.innerText = totalDistance.toFixed(2);
            timeVal.innerText = formatTime(elapsedTime);
            
            const avgPaceSec = totalDistance > 0 ? (elapsedTime / totalDistance) : 0;
            paceVal.innerText = formatPace(avgPaceSec);
            
            totalSteps = Math.floor(totalDistance * 1300);
            stepsVal.innerText = totalSteps;
            
            totalKcal = Math.floor(totalDistance * pesoUtente * 1.03);
            kcalVal.innerText = totalKcal;
        }

        function tick() {
            if (isRunning) {
                elapsedTime++;
                updateUI();
            }
        }

        function successPosition(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const accuracy = position.coords.accuracy;
            
            if (accuracy > 30) return;
            
            // Registra ogni punto valido nel percorso per la mappa
            gpsPath.push([lon, lat]);
            
            if (lastLat !== null && lastLon !== null) {
                const dist = calculateDistance(lastLat, lastLon, lat, lon);
                if (dist > 0.002 && dist < 0.2) {
                    totalDistance += dist;
                    updateUI();
                }
            }
            
            lastLat = lat;
            lastLon = lon;
        }

        function errorPosition(err) {
            errorMsg.style.display = 'block';
            if (err.code === 1) {
                errorMsg.innerText = "Accesso al GPS negato. Assicurati di aver dato i permessi al browser.";
            } else if (err.code === 2) {
                errorMsg.innerText = "Posizione GPS non disponibile al momento.";
            } else {
                errorMsg.innerText = "Timeout o errore sconosciuto del GPS.";
            }
        }

        function startRun() {
            if (!navigator.geolocation) {
                errorMsg.style.display = 'block';
                errorMsg.innerText = "Il tuo browser non supporta il GPS.";
                return;
            }
            
            errorMsg.style.display = 'none';
            isRunning = true;
            
            btnStart.style.display = 'none';
            btnResume.style.display = 'none';
            btnStop.style.display = 'block';
            btnFinish.style.display = 'none';
            
            statusBadge.innerText = '● RECORDING GPS';
            statusBadge.classList.add('active');
            
            lastLat = null;
            lastLon = null;
            gpsPath = [];
            
            timerInterval = setInterval(tick, 1000);
            
            watchId = navigator.geolocation.watchPosition(
                successPosition, 
                errorPosition, 
                {
                    enableHighAccuracy: true,
                    maximumAge: 0,
                    timeout: 10000
                }
            );
        }

        function stopRun() {
            isRunning = false;
            clearInterval(timerInterval);
            if (watchId !== null) {
                navigator.geolocation.clearWatch(watchId);
            }
            
            btnStop.style.display = 'none';
            btnResume.style.display = 'block';
            btnFinish.style.display = 'block';
            
            statusBadge.innerText = 'PAUSED';
            statusBadge.classList.remove('active');
        }

        function resumeRun() {
            errorMsg.style.display = 'none';
            isRunning = true;
            
            btnResume.style.display = 'none';
            btnStop.style.display = 'block';
            btnFinish.style.display = 'none';
            
            statusBadge.innerText = '● RECORDING GPS';
            statusBadge.classList.add('active');
            
            lastLat = null; 
            lastLon = null;
            
            timerInterval = setInterval(tick, 1000);
            watchId = navigator.geolocation.watchPosition(
                successPosition, 
                errorPosition, 
                {
                    enableHighAccuracy: true,
                    maximumAge: 0,
                    timeout: 10000
                }
            );
        }

        function finishRun() {
            btnFinish.innerText = 'SALVATAGGIO...';
            btnFinish.disabled = true;
            
            const runData = {
                distance: totalDistance.toFixed(2),
                time_sec: elapsedTime,
                pace: formatPace(totalDistance > 0 ? (elapsedTime / totalDistance) : 0),
                steps: totalSteps,
                kcal: totalKcal,
                path: gpsPath
            };
            
            // Invia i dati a Streamlit (Python) tramite l'API nativa
            sendValueToStreamlit(runData);
        }

    </script>
</body>
</html>"""

# Rigenera il file ad ogni avvio (così se viene pushato su GitHub senza cartella, si ri-crea)
with open(_INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(_HTML_CONTENT)

# Registra il custom component in modo sicuro
_component_func = components.declare_component(
    "run_tracker",
    path=_FRONTEND_DIR
)

def render_run_tracker(peso_utente=70, key=None):
    """
    Renderizza il tracker GPS.
    Restituisce None finché l'utente non clicca 'FINE CORSA E SALVA'.
    Quando cliccato, restituisce un dizionario con i dati.
    """
    component_value = _component_func(peso_utente=peso_utente, key=key)
    return component_value
