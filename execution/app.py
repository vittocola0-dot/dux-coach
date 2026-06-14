"""
Coach Fitness Dinamico -- App Streamlit
========================================
Applicazione principale con 3 sezioni (Tab):
1. Il Tuo Profilo -- Configurazione iniziale
2. Allenamento di Oggi -- Generatore on-demand + tracciamento
3. Diario & Progressi -- Analisi settimanale e storico

Lanciare con: streamlit run execution/app.py
"""

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# Aggiungi la directory execution/ al path per gli import dei moduli
_EXEC_DIR = Path(__file__).resolve().parent
if str(_EXEC_DIR) not in sys.path:
    sys.path.insert(0, str(_EXEC_DIR))

import data_manager as dm
import workout_generator as wg
import coach_feedback as cf
import streamlit.components.v1 as components
import pydeck as pdk
from run_tracker_component import render_run_tracker
from timer_component import get_timer_html

# =============================================================================
# CONFIGURAZIONE PAGINA
# =============================================================================

st.set_page_config(
    page_title="Coach Fitness Dinamico",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# STILE CSS PERSONALIZZATO
# =============================================================================

st.markdown("""
<style>
    /* --- Font da video Dribbble --- */
    @import url('https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;500;600;700&display=swap');

    /* Sfondo scuro e testo chiaro per replicare il dark mode */
    .stApp {
        background-color: #0a0a0a;
        color: #f0f0f0;
    }
    
    html, body, [class*="st-"], [class*="css"], p, span, div {
        font-family: 'Inter', sans-serif !important;
    }

    h1, h2, h3, h1 *, h2 *, h3 * {
        font-family: 'Anton', sans-serif !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }

    /* --- Header principale (Stile WORKOUT) --- */
    .main-header {
        padding: 1rem 0 2rem 0;
        margin-bottom: 1rem;
    }
    .main-header h1 {
        color: #ffffff;
        font-size: 5.5rem;
        font-weight: 400;
        margin: 0;
        line-height: 0.9;
        letter-spacing: 1px;
    }
    .main-header .subtitle-container {
        margin-top: 0.8rem;
    }
    .main-header .level {
        font-size: 1.8rem;
        font-weight: 600;
        color: #ffffff;
    }
    .main-header .dropdown {
        color: #7ef2d5;
        font-size: 1.4rem;
        vertical-align: middle;
        margin-left: 5px;
    }
    .main-header .fitness-level {
        font-size: 0.85rem;
        color: #888;
        letter-spacing: 1.5px;
        margin-top: 0.2rem;
        text-transform: uppercase;
        font-weight: 500;
    }

    /* --- Card opzioni allenamento (Stile Black Card) --- */
    .workout-card {
        background-color: #111111;
        border-radius: 24px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
        color: #ffffff;
        box-shadow: 0 8px 30px rgba(0,0,0,0.6);
        border: 1px solid #333;
    }
    .workout-card-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    .workout-card-header .icon {
        background-color: #222222;
        width: 60px;
        height: 60px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        margin-right: 1rem;
    }
    .workout-card-header .title-area h3 {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        font-weight: 700;
        margin: 0;
        color: #ffffff;
        text-transform: none;
        letter-spacing: 0;
        line-height: 1.2;
    }
    .workout-card-header .workouts-count {
        font-size: 0.75rem;
        color: #888;
        font-weight: 600;
        text-transform: uppercase;
        margin-top: 0.2rem;
    }
    .workout-card-header .arrow {
        margin-left: auto;
        font-size: 1.5rem;
        color: #7ef2d5;
    }

    .workout-card .exercise-item {
        color: #d0d0d0;
        font-size: 0.95rem;
        padding: 0.5rem 0;
        border-bottom: 1px solid #333;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: 500;
    }
    .workout-card .exercise-item:last-child {
        border-bottom: none;
    }
    .exercise-volume {
        color: #111;
        font-weight: 700;
        background: #7ef2d5;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.85rem;
    }

    /* --- Stile Pulsanti Moderni --- */
    .stButton > button, .stButton > button * {
        font-family: 'Anton', sans-serif !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        font-size: 1.2rem !important;
    }
    /* Primary (Avvia Allenamento) - Solido Verde Menta */
    .stButton > button[kind="primary"] {
        background-color: #7ef2d5 !important;
        color: #000000 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(126, 242, 213, 0.2);
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #5bd4b5 !important;
        transform: translateY(-2px);
    }
    
    /* Secondary (Segna come completato) - Outlined Suro / Trasparente */
    .stButton > button[kind="secondary"] {
        background-color: transparent !important;
        color: #7ef2d5 !important;
        border-radius: 12px !important;
        border: 2px solid #333 !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.3s ease;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: #7ef2d5 !important;
        background-color: rgba(126, 242, 213, 0.1) !important;
        transform: translateY(-2px);
    }

    /* --- Input e form dark --- */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        border: 1px solid #333 !important;
    }
    
    /* --- Tabs --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #222222 !important;
        border-radius: 20px !important;
        border: 1px solid #333 !important;
        padding: 0.5rem 1.5rem !important;
        color: #ffffff !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #7ef2d5 !important;
        color: #000000 !important;
        font-weight: 700 !important;
        border-color: #7ef2d5 !important;
    }

    /* --- Feedback del coach --- */
    .coach-feedback {
        background: #1a1a1a;
        border-left: 4px solid #7ef2d5;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        font-size: 1.05rem;
        line-height: 1.6;
    }
    .coach-feedback strong {
        color: #7ef2d5;
    }

    /* --- Metriche --- */
    [data-testid="stMetricValue"] {
        font-family: 'Anton', sans-serif;
        color: #7ef2d5;
        font-size: 2.5rem;
    }

    /* Nascondi header standard */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# HEADER
# =============================================================================

st.markdown("""
<div class="main-header">
    <h1 style="color: #7ef2d5;">TRAINING HUB</h1>
    <div class="subtitle-container">
        <span class="level">Coach AI </span><span class="dropdown">▼</span>
        <div class="fitness-level">IL TUO PERSONAL TRAINER</div>
    </div>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# TAB PRINCIPALI
# =============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "👤 Il Tuo Profilo",
    "🏋️ Allenamento di Oggi",
    "📊 Diario & Progressi",
    "🏃‍♂️ Corsa Live",
])


# =============================================================================
# TAB 1: IL TUO PROFILO
# =============================================================================

with tab1:
    st.markdown("### 📝 Configurazione del Tuo Profilo")
    st.markdown("Inserisci i tuoi dati per personalizzare gli allenamenti.")

    # Carica profilo esistente (se presente)
    profilo_salvato = dm.carica_profilo()

    col_form, col_preview = st.columns([3, 2])

    with col_form:
        with st.form("profilo_form", clear_on_submit=False):
            st.markdown("#### 📏 Dati Antropometrici")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                peso = st.number_input(
                    "Peso (kg)", min_value=30.0, max_value=250.0,
                    value=float(profilo_salvato.get("peso", 70.0)) if profilo_salvato else 70.0,
                    step=0.5, format="%.1f"
                )
            with col_b:
                altezza = st.number_input(
                    "Altezza (cm)", min_value=100, max_value=250,
                    value=int(profilo_salvato.get("altezza", 170)) if profilo_salvato else 170,
                    step=1
                )
            with col_c:
                eta = st.number_input(
                    "Età", min_value=14, max_value=100,
                    value=int(profilo_salvato.get("eta", 30)) if profilo_salvato else 30,
                    step=1
                )

            sesso = st.selectbox(
                "Sesso",
                options=["Maschio", "Femmina"],
                index=["Maschio", "Femmina"].index(profilo_salvato.get("sesso", "Maschio")) if profilo_salvato else 0
            )

            st.markdown("#### 🏢 Stile di Vita")
            tipo_lavoro = st.selectbox(
                "Tipo di lavoro",
                options=["Sedentario (ufficio)", "Moderatamente attivo", "Molto attivo (fisico)"],
                index=["Sedentario (ufficio)", "Moderatamente attivo", "Molto attivo (fisico)"].index(
                    profilo_salvato.get("tipo_lavoro", "Sedentario (ufficio)")
                ) if profilo_salvato else 0
            )

            alimentazione = st.selectbox(
                "Tipo di alimentazione",
                options=["Libera", "Controllata/Bilanciata", "Vegetariana", "Vegana"],
                index=["Libera", "Controllata/Bilanciata", "Vegetariana", "Vegana"].index(
                    profilo_salvato.get("alimentazione", "Libera")
                ) if profilo_salvato else 0
            )

            st.markdown("#### 🏠 Attrezzatura Disponibile")
            attr_defaults = profilo_salvato.get("attrezzatura", []) if profilo_salvato else []
            col_attr1, col_attr2 = st.columns(2)
            with col_attr1:
                attr_manubri = st.checkbox("🏋️ Manubri", value="manubri" in attr_defaults)
                attr_elastici = st.checkbox("🪢 Elastici / Bande", value="elastici" in attr_defaults)
            with col_attr2:
                attr_tappetino = st.checkbox("🧘 Tappetino", value="tappetino" in attr_defaults)
                attr_sbarra = st.checkbox("🪜 Sbarra per trazioni", value="sbarra" in attr_defaults)

            st.markdown("#### ⚽ Attività Occasionali")
            attivita_opzioni = ["Calcetto", "Padel", "Corsa", "Nuoto", "Ciclismo", "Altro"]
            attivita_defaults = profilo_salvato.get("attivita_occasionali", []) if profilo_salvato else []
            attivita = st.multiselect(
                "Seleziona le attività che pratichi occasionalmente",
                options=attivita_opzioni,
                default=[a for a in attivita_defaults if a in attivita_opzioni]
            )

            submitted = st.form_submit_button("💾 Salva Profilo", use_container_width=True)

            if submitted:
                # Costruisci la lista attrezzatura
                attrezzatura = []
                if attr_manubri:
                    attrezzatura.append("manubri")
                if attr_elastici:
                    attrezzatura.append("elastici")
                if attr_tappetino:
                    attrezzatura.append("tappetino")
                if attr_sbarra:
                    attrezzatura.append("sbarra")
                if not attrezzatura:
                    attrezzatura.append("nessuna")

                profilo_dati = {
                    "peso": peso,
                    "altezza": altezza,
                    "eta": eta,
                    "sesso": sesso,
                    "tipo_lavoro": tipo_lavoro,
                    "alimentazione": alimentazione,
                    "attrezzatura": attrezzatura,
                    "attivita_occasionali": attivita,
                }

                dm.salva_profilo(profilo_dati)
                st.success("✅ Profilo salvato con successo!")
                st.rerun()

    with col_preview:
        if profilo_salvato:
            st.markdown("#### 📋 Profilo Attuale")

            # BMI
            altezza_m = profilo_salvato.get("altezza", 170) / 100
            peso_val = profilo_salvato.get("peso", 70)
            bmi = round(peso_val / (altezza_m ** 2), 1)

            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric("Peso", f"{peso_val} kg")
                st.metric("Età", f"{profilo_salvato.get('eta', '-')} anni")
            with col_m2:
                st.metric("Altezza", f"{profilo_salvato.get('altezza', '-')} cm")
                st.metric("BMI", f"{bmi}")

            st.markdown(f"**Sesso:** {profilo_salvato.get('sesso', '-')}")
            st.markdown(f"**Lavoro:** {profilo_salvato.get('tipo_lavoro', '-')}")
            st.markdown(f"**Alimentazione:** {profilo_salvato.get('alimentazione', '-')}")

            attr_list = profilo_salvato.get("attrezzatura", ["nessuna"])
            attr_icons = {
                "manubri": "🏋️", "elastici": "🪢",
                "tappetino": "🧘", "sbarra": "🪜", "nessuna": "❌"
            }
            attr_display = ", ".join([f"{attr_icons.get(a, '')} {a.capitalize()}" for a in attr_list])
            st.markdown(f"**Attrezzatura:** {attr_display}")

            attivita_list = profilo_salvato.get("attivita_occasionali", [])
            if attivita_list:
                st.markdown(f"**Attività occasionali:** {', '.join(attivita_list)}")

            ultimo_agg = profilo_salvato.get("ultimo_aggiornamento", "")
            if ultimo_agg:
                try:
                    dt = datetime.fromisoformat(ultimo_agg)
                    st.caption(f"Ultimo aggiornamento: {dt.strftime('%d/%m/%Y %H:%M')}")
                except ValueError:
                    pass
        else:
            st.info("👈 Compila il form a sinistra per creare il tuo profilo.")


# =============================================================================
# TAB 2: ALLENAMENTO DI OGGI
# =============================================================================

with tab2:
    profilo = dm.carica_profilo()

    if not profilo:
        st.warning("⚠️ **Profilo non configurato!** Vai nella scheda '👤 Il Tuo Profilo' per inserire i tuoi dati.")
    else:
        st.markdown("### 🎯 Genera il tuo allenamento di oggi")

        col_input1, col_input2 = st.columns(2)
        with col_input1:
            tempo = st.slider(
                "⏱️ Tempo disponibile oggi (minuti)",
                min_value=10, max_value=60, value=30, step=5,
            )
        with col_input2:
            energia_map = {"🔋 Alta": "Alta", "⚡ Media": "Media", "🪫 Bassa": "Bassa"}
            energia_sel = st.select_slider(
                "💪 Livello di energia",
                options=list(energia_map.keys()),
                value="⚡ Media"
            )
            energia = energia_map[energia_sel]

        if st.button("🎲 Genera Allenamento", use_container_width=True, type="primary"):
            st.session_state["opzioni_generate"] = wg.genera_opzioni(tempo, energia, profilo)
            st.session_state["tempo_selezionato"] = tempo
            st.session_state["energia_selezionata"] = energia

        # Mostra le opzioni generate
        if "opzioni_generate" in st.session_state:
            opzioni = st.session_state["opzioni_generate"]
            tempo_sel = st.session_state.get("tempo_selezionato", 30)
            energia_sel_val = st.session_state.get("energia_selezionata", "Media")

            active_timer = st.session_state.get("active_timer")
            
            if active_timer:
                lettera = active_timer
                opt = opzioni[lettera]
                
                col_title, col_close = st.columns([3, 1])
                with col_title:
                    st.markdown(f"### ⏱️ {opt['nome']}")
                with col_close:
                    if st.button("CHIUDI TIMER", use_container_width=True):
                        st.session_state["active_timer"] = None
                        st.rerun()

                # Render HTML component
                html_code = get_timer_html(opt["esercizi"], energia_sel_val)
                components.html(html_code, height=650)
                
                # Render "Completato"
                if st.button(f"TERMINA E SALVA", use_container_width=True, type="primary"):
                    oggi = datetime.now().strftime("%Y-%m-%d")
                    esercizi_str = " | ".join(opt["esercizi_formattati"])
                    dm.registra_allenamento(
                        data=oggi,
                        opzione=lettera,
                        nome_opzione=opt["nome"],
                        esercizi=esercizi_str,
                        tempo_minuti=tempo_sel,
                        energia=energia_sel_val,
                    )
                    st.session_state["active_timer"] = None
                    st.success(f"✅ **{opt['nome']}** registrato per oggi!")
                    st.balloons()
                    st.rerun()
            else:
                st.markdown("---")
                st.markdown(f"**Allenamento per {tempo_sel} minuti - Energia: {energia_sel_val}**")

                col_a, col_b, col_c = st.columns(3)

                opzione_labels = {
                    "A": ("🔥", "Opzione A", "#e74c3c"),
                    "B": ("💪", "Opzione B", "#3498db"),
                    "C": ("🧘", "Opzione C", "#2ecc71"),
                }

                for col, lettera in zip([col_a, col_b, col_c], ["A", "B", "C"]):
                    with col:
                        emoji, label, colore = opzione_labels[lettera]
                        opt = opzioni[lettera]

                        # Costruiamo la card HTML stile Dribbble
                        card_html = f'''<div class="workout-card">
<div class="workout-card-header">
<div class="icon">{emoji}</div>
<div class="title-area">
<h3>{opt['nome']}</h3>
<div class="workouts-count">{len(opt['esercizi'])} WORKOUTS</div>
</div>
<div class="arrow">→</div>
</div>
'''

                        for ex in opt["esercizi"]:
                            nome = ex["nome"]
                            serie = ex.get("serie", ex["serie_default"])
                            if ex.get("reps") is not None:
                                volume = f"{serie}×{ex['reps']}"
                            elif ex.get("durata") is not None:
                                volume = f"{serie}×{ex['durata']}s"
                            else:
                                volume = "-"

                            card_html += f'''<div class="exercise-item">
<span class="exercise-name">{nome}</span>
<span class="exercise-volume">{volume}</span>
</div>
'''

                        card_html += '</div>'
                        
                        st.markdown(card_html, unsafe_allow_html=True)

                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("AVVIA TIMER", key=f"avvia_{lettera}_{tempo_sel}_{energia_sel_val}", use_container_width=True, type="primary"):
                                st.session_state["active_timer"] = lettera
                                st.rerun()
                        with col_btn2:
                            # Pulsante completamento
                            btn_key = f"completa_{lettera}_{tempo_sel}_{energia_sel_val}"
                            if st.button("FATTO", key=btn_key, use_container_width=True, type="secondary"):
                                oggi = datetime.now().strftime("%Y-%m-%d")
                                esercizi_str = " | ".join(opt["esercizi_formattati"])
                                dm.registra_allenamento(
                                    data=oggi,
                                    opzione=lettera,
                                    nome_opzione=opt["nome"],
                                    esercizi=esercizi_str,
                                    tempo_minuti=tempo_sel,
                                    energia=energia_sel_val,
                                )
                                st.success(f"✅ **{opt['nome']}** registrato per oggi!")
                                st.balloons()


# =============================================================================
# TAB 3: DIARIO & PROGRESSI
# =============================================================================

with tab3:
    profilo = dm.carica_profilo()

    if not profilo:
        st.warning("⚠️ **Profilo non configurato!** Vai nella scheda '👤 Il Tuo Profilo' per inserire i tuoi dati.")
    else:
        st.markdown("### 📊 Diario Settimanale & Progressi")

        # --- Sezione input ---
        col_peso, col_note = st.columns([1, 2])

        with col_peso:
            storico = dm.carica_storico_peso()
            ultimo_peso = float(storico.iloc[-1]["peso"]) if not storico.empty else float(profilo.get("peso", 70.0))

            nuovo_peso = st.number_input(
                "⚖️ Nuovo Peso (kg)",
                min_value=30.0, max_value=250.0,
                value=ultimo_peso,
                step=0.1, format="%.1f",
            )

        with col_note:
            note = st.text_area(
                "📝 Note (opzionale)",
                placeholder="Es. Mi sentivo stanco, dolore alla schiena, settimana stressante...",
                height=100,
            )

        if st.button("📋 Salva e Valuta Settimana", use_container_width=True, type="primary"):
            # 1. Salva il peso
            dm.salva_peso(nuovo_peso, note)

            # 2. Calcola variazione
            peso_att, peso_prec, delta = dm.variazione_peso()

            # 3. Allenamenti ultimi 7 giorni
            allenamenti_7g = dm.allenamenti_ultimi_7_giorni()
            num_allenamenti = len(allenamenti_7g)
            tipi = dm.conta_allenamenti_per_tipo(allenamenti_7g)

            # 4. Numero settimana
            storico_aggiornato = dm.carica_storico_peso()
            settimana_num = len(storico_aggiornato)

            # 5. Genera feedback
            feedback = cf.genera_feedback(delta, num_allenamenti, tipi, settimana_num)

            st.session_state["ultimo_feedback"] = feedback
            st.session_state["ultimo_delta"] = delta
            st.session_state["ultimo_num_all"] = num_allenamenti
            st.session_state["ultimo_tipi"] = tipi

            st.success("✅ Settimana salvata!")

        # --- Mostra feedback ---
        if "ultimo_feedback" in st.session_state:
            st.markdown("---")
            st.markdown("#### 🗣️ Il Tuo Coach Dice:")
            st.markdown(
                f'<div class="coach-feedback">{st.session_state["ultimo_feedback"]}</div>',
                unsafe_allow_html=True,
            )

            # Metriche rapide
            col_m1, col_m2, col_m3 = st.columns(3)
            delta = st.session_state.get("ultimo_delta")
            with col_m1:
                if delta is not None:
                    st.metric("Variazione Peso", f"{delta:+.1f} kg")
                else:
                    st.metric("Variazione Peso", "Baseline")
            with col_m2:
                st.metric("Allenamenti (7gg)", st.session_state.get("ultimo_num_all", 0))
            with col_m3:
                tipi = st.session_state.get("ultimo_tipi", {})
                st.metric("Tipi Svolti", f"A:{tipi.get('A',0)} B:{tipi.get('B',0)} C:{tipi.get('C',0)}")

        # --- Storico e Grafici ---
        st.markdown("---")
        st.markdown("#### 📈 Storico Peso")

        storico = dm.carica_storico_peso()

        if storico.empty:
            st.info("📭 Nessun dato registrato. Inserisci il tuo primo peso qui sopra!")
        else:
            # Grafico peso
            storico_chart = storico.copy()
            storico_chart["data"] = pd.to_datetime(storico_chart["data"])
            storico_chart = storico_chart.set_index("data")
            storico_chart["peso"] = pd.to_numeric(storico_chart["peso"])

            st.line_chart(storico_chart["peso"], use_container_width=True)

            # Tabella riassuntiva
            st.markdown("#### 📋 Riepilogo Settimanale")

            riepilogo = []
            for i, row in storico.iterrows():
                delta_val = "-"
                if i > 0:
                    try:
                        delta_val = f"{float(row['peso']) - float(storico.iloc[i-1]['peso']):+.1f} kg"
                    except (ValueError, TypeError):
                        delta_val = "-"

                # Conta allenamenti nella settimana di questa registrazione
                data_reg = pd.to_datetime(row["data"]).date()
                registro = dm.carica_registro()
                if not registro.empty:
                    registro["data_dt"] = pd.to_datetime(registro["data"]).dt.date
                    from datetime import timedelta
                    inizio_sett = data_reg - timedelta(days=7)
                    all_sett = registro[
                        (registro["data_dt"] > inizio_sett) & (registro["data_dt"] <= data_reg)
                    ]
                    num_all = len(all_sett)
                else:
                    num_all = 0

                riepilogo.append({
                    "Settimana": i + 1,
                    "Data": row["data"],
                    "Peso (kg)": row["peso"],
                    "Δ Peso": delta_val,
                    "N° Allenamenti": num_all,
                })

            df_riepilogo = pd.DataFrame(riepilogo)
            st.dataframe(df_riepilogo, use_container_width=True, hide_index=True)

        # --- Registro allenamenti recenti ---
        st.markdown("---")
        st.markdown("#### 🗓️ Allenamenti Recenti (ultimi 7 giorni)")

        allenamenti_recenti = dm.allenamenti_ultimi_7_giorni()

        if allenamenti_recenti.empty:
            st.warning("⚠️ **Non ci sono ancora allenamenti registrati.** Inizia ad allenarti per vedere i tuoi progressi!")
        else:
            for _, row in allenamenti_recenti.iterrows():
                opz_emoji = {"A": "🔥", "B": "💪", "C": "🧘"}.get(row["opzione"], "📋")
                st.markdown(
                    f"**{row['data']}** - {opz_emoji} Opzione {row['opzione']} "
                    f"({row['nome_opzione']}) - {row['tempo_minuti']} min - "
                    f"Energia: {row['energia']}"
                )
                
        # --- Registro Corse GPS ---
        st.markdown("---")
        st.markdown("#### 🏃‍♂️ Corse Registrate (GPS)")
        corse = dm.carica_corse()
        if not corse:
            st.info("Nessuna corsa registrata con il GPS.")
        else:
            for corsa in reversed(corse[-5:]): # Mostriamo solo le ultime 5
                # Formatta la data dal formato ISO
                try:
                    dt = pd.to_datetime(corsa['data']).strftime("%d %b %Y - %H:%M")
                except:
                    dt = corsa['data']
                    
                st.markdown(f"**{dt}** — 🛣️ {corsa['distanza']} km | ⏱️ {corsa['pace']} min/km | 🔥 {corsa['kcal']} kcal")
                
                path = corsa.get('gps_path', [])
                if path and len(path) > 1:
                    path_data = [{"path": path}]
                    layer = pdk.Layer(
                        "PathLayer",
                        data=path_data,
                        get_path="path",
                        get_color=[126, 242, 213, 255], # Neon mint green come Dribbble
                        width_scale=20,
                        width_min_pixels=6,
                        get_width=5,
                    )
                    # Centra la mappa sul punto medio approssimativo
                    mid_idx = len(path) // 2
                    center_lon, center_lat = path[mid_idx]
                    
                    view_state = pdk.ViewState(
                        longitude=center_lon,
                        latitude=center_lat,
                        zoom=14.5,
                        pitch=50, # Inclinazione 3D cinematica
                        bearing=0
                    )
                    
                    st.pydeck_chart(pdk.Deck(
                        layers=[layer],
                        initial_view_state=view_state,
                        map_style="mapbox://styles/mapbox/dark-v10",
                    ))


# =============================================================================
# TAB 4: CORSA LIVE (GPS)
# =============================================================================

with tab4:
    profilo = dm.carica_profilo()
    
    if not profilo:
        st.warning("⚠️ **Profilo non configurato!** Vai nella scheda '👤 Il Tuo Profilo' per inserire i tuoi dati, così potremo calcolare le calorie.")
    else:
        peso_utente = profilo.get("peso", 70)
        
        st.markdown("### 🏃‍♂️ Traccia la tua Corsa (GPS)")
        st.markdown("Questa dashboard usa il GPS del tuo dispositivo per calcolare distanza, tempo e passo reale. Al termine, clicca su 'Fine Corsa e Salva'.")
        
        run_data = render_run_tracker(peso_utente)
        
        if run_data is not None:
            # run_data è il dizionario restituito dal componente JS
            dm.registra_corsa(
                distanza=float(run_data.get("distance", 0)),
                tempo_sec=int(run_data.get("time_sec", 0)),
                pace=run_data.get("pace", "0:00"),
                passi=int(run_data.get("steps", 0)),
                kcal=int(run_data.get("kcal", 0)),
                gps_path=run_data.get("path", [])
            )
            st.success("✅ **Corsa salvata con successo!** Vai nella scheda 'Diario & Progressi' per vedere la mappa del tracciato.")
            # st.balloons()

# Forza ricaricamento cache
