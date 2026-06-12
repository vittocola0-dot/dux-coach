Coach Fitness Dinamico — App Streamlit
========================================
Applicazione principale con 3 sezioni (Tab):
1. Il Tuo Profilo — Configurazione iniziale
2. Allenamento di Oggi — Generatore on-demand + tracciamento
3. Diario & Progressi — Analisi settimanale e storico

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
    /* --- Font moderno --- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* --- Header principale --- */
    .main-header {
        background: linear-gradient(135deg, #0f9b8e 0%, #0d7377 50%, #14532d 100%);
        padding: 1.8rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(15, 155, 142, 0.25);
    }
    .main-header h1 {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: rgba(255,255,255,0.85);
        font-size: 1rem;
        margin: 0.3rem 0 0 0;
        font-weight: 300;
    }

    /* --- Card per le opzioni di allenamento --- */
    .workout-card {
        background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid rgba(15, 155, 142, 0.3);
        border-radius: 14px;
        padding: 1.4rem;
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .workout-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(15, 155, 142, 0.2);
    }
    .workout-card h3 {
        color: #0f9b8e;
        font-size: 1.15rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(15, 155, 142, 0.2);
    }
    .workout-card .exercise-item {
        color: #e0e0e0;
        font-size: 0.95rem;
        padding: 0.35rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        display: flex;
        justify-content: space-between;
    }
    .workout-card .exercise-item:last-child {
        border-bottom: none;
    }
    .exercise-name {
        font-weight: 500;
    }
    .exercise-volume {
        color: #0f9b8e;
        font-weight: 600;
        font-family: 'Inter', monospace;
    }

    /* --- Card profilo --- */
    .profile-card {
        background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid rgba(15, 155, 142, 0.2);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .profile-card h3 {
        color: #0f9b8e;
        margin-bottom: 0.8rem;
    }
    .profile-stat {
        display: flex;
        justify-content: space-between;
        padding: 0.4rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        color: #e0e0e0;
    }
    .profile-stat .label {
        color: #9ca3af;
        font-size: 0.9rem;
    }
    .profile-stat .value {
        font-weight: 600;
        color: #ffffff;
    }

    /* --- Feedback del coach --- */
    .coach-feedback {
        background: linear-gradient(145deg, #1a1a2e 0%, #0d3b2e 100%);
        border: 1px solid rgba(15, 155, 142, 0.4);
        border-radius: 14px;
        padding: 1.5rem;
        margin: 1rem 0;
        font-size: 1rem;
        line-height: 1.6;
        color: #e0e0e0;
    }
    .coach-feedback strong {
        color: #0f9b8e;
    }

    /* --- Migliora aspetto dei tab --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
    }

    /* --- Nascondi footer streamlit --- */
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# HEADER
# =============================================================================

st.markdown("""
<div class="main-header">
    <h1>🏋️ Coach Fitness Dinamico</h1>
    <p>Il tuo personal trainer AI — Allenamenti su misura, progressi reali</p>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# TAB PRINCIPALI
# =============================================================================

tab1, tab2, tab3 = st.tabs([
    "👤 Il Tuo Profilo",
    "🏋️ Allenamento di Oggi",
    "📊 Diario & Progressi",
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

            st.markdown("---")
            st.markdown(f"**Allenamento per {tempo_sel} minuti — Energia: {energia_sel_val}**")

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

                    st.markdown(f"#### {emoji} {label}")
                    st.markdown(f"**{opt['nome']}**")

                    # Lista esercizi in formato card
                    for i, ex in enumerate(opt["esercizi"]):
                        nome = ex["nome"]
                        serie = ex.get("serie", ex["serie_default"])
                        if ex.get("reps") is not None:
                            volume = f"{serie}×{ex['reps']}"
                        elif ex.get("durata") is not None:
                            volume = f"{serie}×{ex['durata']}s"
                        else:
                            volume = "-"

                        st.markdown(
                            f'<div class="exercise-item">'
                            f'<span class="exercise-name">{nome}</span>'
                            f'<span class="exercise-volume">{volume}</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                    st.markdown("")  # Spacer

                    # Pulsante completamento
                    btn_key = f"completa_{lettera}_{tempo_sel}_{energia_sel_val}"
                    if st.button(
                        f"✅ Segna come Completato",
                        key=btn_key,
                        use_container_width=True,
                    ):
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
            st.info("📭 Nessun allenamento registrato negli ultimi 7 giorni.")
        else:
            for _, row in allenamenti_recenti.iterrows():
                opz_emoji = {"A": "🔥", "B": "💪", "C": "🧘"}.get(row["opzione"], "📋")
                st.markdown(
                    f"**{row['data']}** — {opz_emoji} Opzione {row['opzione']} "
                    f"({row['nome_opzione']}) — {row['tempo_minuti']} min — "
                    f"Energia: {row['energia']}"
                )
