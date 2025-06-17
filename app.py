import streamlit as st
import json
import os
import csv
from datetime import date

# Pagina-configuratie en stijl
st.set_page_config(page_title="Tour déh France", page_icon="🚴", layout="wide")

# Custom styling
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Barlow', sans-serif;
            background-color: #fffbea;
            color: #000000;
        }

        .stApp {
            background-color: #fffbea;
        }

        h1, h2, h3, h4 {
            color: #FFCC00;
        }

        .stButton>button {
            background-color: #FFCC00;
            color: black;
            border-radius: 6px;
            padding: 0.6em 1.2em;
            font-weight: bold;
            border: none;
            width: 100%;
            margin-bottom: 0.25em;
            text-align: left;
        }

        .stButton#btn_Deelnemen button {
            background-color: #ff9900;
        }

        .stSelectbox>div>div {
            background-color: white;
            border-radius: 4px;
            padding: 0.25em;
        }

        .stTextInput>div>div>input {
            border: 1px solid #FFCC00;
        }

        .block-container {
            padding-top: 2rem;
        }

        .strikethrough {
            color: red;
            text-decoration: line-through;
        }
    </style>
""", unsafe_allow_html=True)

# Betrouwbare versie van het logo in PNG-formaat
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Tour_de_France_logo.svg/320px-Tour_de_France_logo.svg.png", width=180)

if "admin_access" not in st.session_state:
    st.session_state["admin_access"] = False

if not st.session_state["admin_access"]:
    tabs = ["Etappes", "Klassement", "Pronostiek", "Renners", "Reglement", "Deelnemen"]
else:
    tabs = ["Etappes", "Klassement", "Pronostiek", "Renners", "Reglement", "Deelnemen", "Admin"]

if "active_page" not in st.session_state:
    st.session_state["active_page"] = "Etappes"

for tab in tabs:
    if st.sidebar.button(tab, key=f"btn_{tab}"):
        st.session_state["active_page"] = tab

page = st.session_state["active_page"]

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
DEELNEMERS_FILE = os.path.join(DATA_DIR, "deelnemers.json")
STARTLIJST_DIR = os.path.join(DATA_DIR, "startlijsten")
os.makedirs(STARTLIJST_DIR, exist_ok=True)


def load_deelnemers():
    if os.path.exists(DEELNEMERS_FILE):
        with open(DEELNEMERS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_deelnemers(data):
    with open(DEELNEMERS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_startlijst(etappe_nummer):
    bestand = os.path.join(STARTLIJST_DIR, f"etappe_{etappe_nummer}.json")
    if os.path.exists(bestand):
        with open(bestand, "r") as f:
            return json.load(f)
    return []

# ------------------ TABS ------------------

if page == "Deelnemen":
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Tour_de_France_logo.svg/320px-Tour_de_France_logo.svg.png", width=200)
    st.title("Doe mee met de Tour déh France!")
    st.markdown("""
    Wil je meespelen met het familie-pronostiekspel? Vul dan het formulier in via onderstaande knop:

    👉 [Open het deelnameformulier](https://forms.gle/jouw-form-link-hier)

    - Deelnamekost: €5
    - Deadline: dag vóór de start van de Tour
    - Ingevulde pronostiek wordt later zichtbaar onder 'Pronostiek'
    """)

# overige tabbladen blijven behouden zoals ze zijn

elif page == "Admin":
    st.title("🔒 Adminconsole")

    st.subheader("1. Registraties beheren")
    deelnemers = load_deelnemers()
    new_name = st.text_input("Voeg een deelnemer toe:")
    if st.button("Toevoegen") and new_name:
        deelnemers[new_name] = {}
        save_deelnemers(deelnemers)
        st.success(f"{new_name} toegevoegd!")
        st.experimental_rerun()

    if deelnemers:
        delete_name = st.selectbox("Verwijder deelnemer:", ["-- Selecteer --"] + list(deelnemers.keys()))
        if delete_name != "-- Selecteer --" and st.button("Verwijder"):
            del deelnemers[delete_name]
            save_deelnemers(deelnemers)
            st.success(f"{delete_name} verwijderd.")
            st.experimental_rerun()

    st.subheader("2. Upload pronostiek CSV (Google Forms export)")
    csv_file = st.file_uploader("Upload CSV", type=["csv"])
    if csv_file:
        try:
            csv_reader = csv.DictReader(csv_file.read().decode("utf-8").splitlines())
            for row in csv_reader:
                naam = row.get("Naam")
                if not naam:
                    continue
                deelnemers[naam] = {
                    "gele_trui": [row.get("gele_trui_1"), row.get("gele_trui_2"), row.get("gele_trui_3")],
                    "groene_trui": [row.get("groene_trui_1"), row.get("groene_trui_2"), row.get("groene_trui_3")],
                    "etappekoning": row.get("etappekoning"),
                    "frikadellengewicht": int(row.get("frikadellengewicht", 0))
                }
            save_deelnemers(deelnemers)
            st.success("Pronostiekgegevens succesvol toegevoegd aan deelnemers.json")
        except Exception as e:
            st.error(f"Fout bij verwerken van CSV: {e}")

# ------------------ TOEGANGSCODE ------------------
if not st.session_state["admin_access"]:
    with st.expander("Ben jij de organisator?"):
        code = st.text_input("Voer admincode in:", type="password")
        if code == "JULES2025":
            st.session_state["admin_access"] = True
            st.experimental_rerun()
