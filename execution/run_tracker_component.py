import os
import streamlit.components.v1 as components

# Registra il custom component. 
# La cartella deve contenere il file index.html che usa streamlit-component-lib.
_component_func = components.declare_component(
    "run_tracker",
    path=os.path.join(os.path.dirname(__file__), "run_tracker_ui")
)

def render_run_tracker(peso_utente=70, key=None):
    """
    Renderizza il tracker GPS.
    Restituisce None finché l'utente non clicca 'FINE CORSA E SALVA'.
    Quando cliccato, restituisce un dizionario:
    {
        'distance': '...',
        'time_sec': ...,
        'pace': '...',
        'steps': ...,
        'kcal': ...,
        'path': [[lon, lat], [lon, lat], ...]
    }
    """
    component_value = _component_func(peso_utente=peso_utente, key=key)
    return component_value
