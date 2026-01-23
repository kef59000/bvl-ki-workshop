# Dateiname: utils.py
import micropip
import pyodide_http
import requests
import json
import ipywidgets as widgets
from IPython.display import display, HTML

async def setup_environment():
    """Installiert Bibliotheken und patcht das Netzwerk für Browser-Requests."""
    # Patch aktivieren, damit requests im Browser funktioniert
    pyodide_http.patch_all()
    # Styling: Macht die Output-Area etwas hübscher
    display(HTML("<style>.widget-output { background-color: #f9f9f9; padding: 10px; border-radius: 5px; }</style>"))
    print("✅ System bereit: Netzwerk gepatcht & Bibliotheken geladen.")

def call_gemini_api(api_key, prompt, model="gemini-1.5-flash"):
    """
    Sendet den Prompt an die Google Gemini API via REST.
    Versteckt die Komplexität von JSON und Headern vor den Teilnehmern.
    """
    if not api_key or "DEIN_" in api_key:
        return "FEHLER: Bitte erst einen gültigen API-Key eingeben!"

    url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    # Safety Settings auf Permissive setzen, damit Logistik-Daten nicht geblockt werden
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code != 200:
            return f"API Fehler ({response.status_code}): {response.text}"
            
        data = response.json()
        try:
            return data['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError):
            return "Keine Antwort vom Modell erhalten (Filter oder leere Antwort)."
            
    except Exception as e:
        return f"Verbindungsfehler: {str(e)}"

def extract_json(text):
    """Hilft, JSON aus der KI-Antwort zu fischen, auch wenn Markdown drumrum ist."""
    try:
        clean = text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except:
        return None