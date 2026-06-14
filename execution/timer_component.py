import json

def get_timer_html(esercizi, energia="Media"):
    # Costruisci l'array degli step
    steps = []
    
    for i, ex in enumerate(esercizi):
        nome = ex["nome"]
        serie = ex.get("serie", 1)
        reps = ex.get("reps")
        durata = ex.get("durata")
        
        # Semplificazione per il timer: trasformiamo le serie in step ripetuti
        for s in range(serie):
            if reps is not None:
                # Esercizio a ripetizioni: aspetta finché non si preme "Next"
                time_sec = 0
                desc = f"{reps} Reps"
                is_reps = True
            elif durata is not None:
                # Esercizio a tempo
                time_sec = durata
                desc = f"{durata} Secondi"
                is_reps = False
            else:
                time_sec = 30
                desc = "-"
                is_reps = False
            
            steps.append({
                "type": "exercise",
                "name": nome,
                "desc": desc,
                "time": time_sec,
                "is_reps": is_reps,
                "serie": f"{s+1}/{serie}"
            })
            
            # Calcola pausa
            if energia == "Alta":
                rest_time = 20
            elif energia == "Bassa":
                rest_time = 45
            else:
                rest_time = 30
            
            # Aggiungi pausa dopo ogni serie tranne l'ultimissima dell'ultimo esercizio
            if not (i == len(esercizi) - 1 and s == serie - 1):
                steps.append({
                    "type": "rest",
                    "name": "Riposo",
                    "desc": "Preparati per il prossimo",
                    "time": rest_time,
                    "is_reps": False,
                    "serie": ""
                })

    steps_json = json.dumps(steps)
    
    # HTML + JS + CSS del timer
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;600;700&display=swap');
        body {{
            margin: 0;
            padding: 0;
            background-color: #0a0a0a;
            color: #fff;
            font-family: 'Inter', sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            overflow: hidden;
        }}
        .player-container {{
            width: 100%;
            max-width: 400px;
            background: #1a1a1a;
            border-radius: 30px;
            padding: 2rem 1.5rem;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
            text-align: center;
            position: relative;
            box-sizing: border-box;
        }}
        .step-type {{
            color: #7ef2d5;
            font-size: 0.9rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 0.5rem;
        }}
        .step-name {{
            font-family: 'Anton', sans-serif;
            font-size: 3rem;
            line-height: 1.1;
            margin: 0 0 1rem 0;
            text-transform: uppercase;
        }}
        .step-desc {{
            color: #aaa;
            font-size: 1.1rem;
            margin-bottom: 2rem;
            font-weight: 600;
        }}
        .timer-display {{
            font-family: 'Anton', sans-serif;
            font-size: 6rem;
            margin: 1rem 0;
            color: #fff;
            line-height: 1;
        }}
        .controls {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1.5rem;
            margin-top: 2rem;
        }}
        .btn {{
            background: none;
            border: none;
            color: #fff;
            font-size: 1.5rem;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .btn:hover {{ transform: scale(1.1); color: #7ef2d5; }}
        .btn-play {{
            background-color: #7ef2d5;
            color: #000;
            width: 80px;
            height: 80px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            box-shadow: 0 4px 20px rgba(126, 242, 213, 0.4);
        }}
        .btn-play:hover {{ background-color: #5bd4b5; color: #000; }}
        .progress-bar {{
            width: 100%;
            height: 6px;
            background: #333;
            border-radius: 3px;
            margin-top: 2rem;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background: #7ef2d5;
            width: 0%;
            transition: width 1s linear;
        }}
        .done-msg {{
            font-family: 'Anton', sans-serif;
            font-size: 3rem;
            color: #7ef2d5;
        }}
    </style>
    </head>
    <body>
        <div class="player-container" id="player">
            <div class="step-type" id="stepType">GET READY</div>
            <h1 class="step-name" id="stepName">Loading...</h1>
            <div class="step-desc" id="stepDesc"></div>
            
            <div class="timer-display" id="timeDisplay">00:00</div>
            
            <div class="controls">
                <button class="btn" id="btnPrev" onclick="prevStep()">⏮</button>
                <button class="btn btn-play" id="btnPlay" onclick="togglePlay()">▶</button>
                <button class="btn" id="btnNext" onclick="nextStep()">⏭</button>
            </div>
            
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
        </div>

        <script>
            const steps = {steps_json};
            let currentStepIdx = 0;
            let timeLeft = 0;
            let isPlaying = false;
            let timerInterval = null;

            const stepTypeEl = document.getElementById('stepType');
            const stepNameEl = document.getElementById('stepName');
            const stepDescEl = document.getElementById('stepDesc');
            const timeDisplayEl = document.getElementById('timeDisplay');
            const btnPlay = document.getElementById('btnPlay');
            const progressFill = document.getElementById('progressFill');
            const playerEl = document.getElementById('player');

            function formatTime(sec) {{
                const m = Math.floor(sec / 60).toString().padStart(2, '0');
                const s = (sec % 60).toString().padStart(2, '0');
                return `${{m}}:${{s}}`;
            }}

            function loadStep(idx) {{
                if (idx >= steps.length) {{
                    // Finito
                    playerEl.innerHTML = `
                        <div class="done-msg">WORKOUT COMPLETE!</div>
                        <p style="color:#aaa; margin-top:1rem; font-weight:600;">Puoi chiudere questo timer e cliccare Segna come Completato!</p>
                    `;
                    return;
                }}
                
                const step = steps[idx];
                stepTypeEl.innerText = step.type === 'rest' ? 'RECOVERY' : `EXERCISE ${{step.serie}}`;
                stepTypeEl.style.color = step.type === 'rest' ? '#ff9f43' : '#7ef2d5';
                stepNameEl.innerText = step.name;
                stepDescEl.innerText = step.desc;
                
                if (step.is_reps) {{
                    timeLeft = 0;
                    timeDisplayEl.innerText = "DO REPS";
                    progressFill.style.width = '100%';
                    if(isPlaying) togglePlay(); // Metti in pausa automatica
                    btnPlay.style.display = 'none'; // Nascondi il tasto play/pausa
                }} else {{
                    btnPlay.style.display = 'flex';
                    timeLeft = step.time;
                    timeDisplayEl.innerText = formatTime(timeLeft);
                    updateProgress();
                    if(!isPlaying) togglePlay(); // Auto-start the timer
                }}
            }}

            function updateProgress() {{
                if(currentStepIdx >= steps.length) return;
                const step = steps[currentStepIdx];
                if(step.is_reps) return;
                const total = step.time;
                const pct = total > 0 ? ((total - timeLeft) / total) * 100 : 100;
                progressFill.style.width = pct + '%';
            }}

            function tick() {{
                if(currentStepIdx >= steps.length) return;
                if(steps[currentStepIdx].is_reps) return; // Ignore ticks for reps

                if (timeLeft > 0) {{
                    timeLeft--;
                    timeDisplayEl.innerText = formatTime(timeLeft);
                    updateProgress();
                }} else {{
                    nextStep();
                }}
            }}

            function togglePlay() {{
                isPlaying = !isPlaying;
                if (isPlaying) {{
                    btnPlay.innerText = "⏸";
                    timerInterval = setInterval(tick, 1000);
                }} else {{
                    btnPlay.innerText = "▶";
                    clearInterval(timerInterval);
                }}
            }}

            function nextStep() {{
                currentStepIdx++;
                loadStep(currentStepIdx);
                // auto-play
                if (!isPlaying) togglePlay();
            }}

            function prevStep() {{
                if (currentStepIdx > 0) {{
                    currentStepIdx--;
                    loadStep(currentStepIdx);
                }}
            }}

            // Init
            loadStep(0);
        </script>
    </body>
    </html>
    """
    return html
