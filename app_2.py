import streamlit as st
import os
import json
import pandas as pd
import re

# Pagina-configuratie
st.set_page_config(page_title="Tour déh France", page_icon="🚴", layout="wide")

# Styling
st.markdown("""
<style>
body, html, [class*="css"] {
    font-family: 'Barlow', sans-serif;
    background-color: #fffbea;
    color: black;
}
.stApp { background-color: #fffbea; }
h1, h2, h3 { color: #FFCC00; }
.stButton>button { background-color: #FFCC00; color: black; border-radius: 6px; padding: 0.5em; margin-bottom: 0.3em; text-align: left; width: 100%; border: none; }
#btn_Deelnemen button { background-color: #ff9900 !important; }
.strikethrough { color: red; text-decoration: line-through; }
</style>
""", unsafe_allow_html=True)

# Zijbalk met logo en knoppen
st.sidebar.image("https://logowik.com/content/uploads/images/tour-de-france6426.jpg", width=180)
TABS = ["Etappes", "Klassement", "Pronostiek", "Renners", "Reglement", "Deelnemen"]
if st.session_state.get("admin_access"):
    TABS.append("Admin")
if "active_page" not in st.session_state:
    st.session_state["active_page"] = "Etappes"
for tab in TABS:
    if st.sidebar.button(tab, key=f"btn_{tab}"):
        st.session_state["active_page"] = tab
page = st.session_state["active_page"]

# ------------------ TABS ------------------
if page == "Pronostiek":
    st.title("Overzicht Laatste Draw")
    draw_dir = "draws"
    os.makedirs(draw_dir, exist_ok=True)
    draw_files = sorted(
        [f for f in os.listdir(draw_dir) if f.endswith(".json")],
        key=lambda x: re.findall(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}", x)[0] if re.findall(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}", x) else "",
        reverse=True
    )
    if draw_files:
        path = os.path.join(draw_dir, draw_files[0])
        with open(path, "r") as f:
            data = json.load(f)

        styled_dfs = []
        colors = ["#fceabb", "#fff5cc", "#f8f4e3", "#fef9d7"]
        for i, entry in enumerate(data.get("assignments", [])):
            color = colors[i % len(colors)]
            player = entry["player"]
            riders = entry["riders"]
            rows = [{
                "Deelnemer": player,
                "Rugnummer": r["number"],
                "Renner": r["name"],
                "Team": r["team"]
            } for r in riders]
            df = pd.DataFrame(rows)
            styled = df.style.set_properties(**{
                'background-color': color,
                'border-color': 'black'
            })
            styled_dfs.append(styled)

        for styled_df in styled_dfs:
            st.write(styled_df)
    else:
        st.info("Nog geen draw-bestanden gevonden in de map 'draws'.")

elif page == "Etappes":
    st.title("Etappes")
    st.info("Toon hier per etappe de loting, uitslag en punten (placeholder).")

elif page == "Klassement":
    st.title("Klassement")
    optie = st.selectbox("Kies klassement:", ["Totaal", "Lotingklassement", "Pronostiekklassement", "Frikadellenklassement"])
    st.info(f"Toon hier het {optie.lower()} (placeholder).")

elif page == "Renners":
    st.title("Startlijst per Etappe")
    st.info("Toon hier de startlijst met opgevers in rood/doorgestreept (placeholder).")

elif page == "Reglement":
    st.title("Spelreglement")
    st.markdown("""
    ### 🟡 Pronostiek
    - Top 3 gele trui (3pt juist, 1pt verkeerde plaats)
    - Top 3 groene trui (zelfde)
    - Etappekoning (3pt bij juiste voorspelling)
    - Gewicht bolletjestruiwinnaar (3pt als exact)

    ### 🎲 Dagloterij
    - Elke dag 3 renners per deelnemer
    - 5/3/1 pt voor eerste drie gelootte renners in uitslag
    - Tiebreakers: 5pt wins → 3pt → 1pt

    ### 💰 Prijzenpot
    - €5 inleg, verdeling 60/30/10
    - Frikadellenprijs als extra
    """)

elif page == "Deelnemen":
    st.image("https://logowik.com/content/uploads/images/tour-de-france6426.jpg", width=200)
    st.title("Doe mee met de Tour déh France!")
    st.markdown("""
    Vul het deelnameformulier in vóór de Tour start:

    👉 [Open deelnameformulier](https://forms.gle/jouw-form-link-hier)

    Deelname: €5 per persoon. Je pronostiek verschijnt na verwerking in het tabblad 'Pronostiek'.
    """)

elif page == "Admin":
    st.title("🔒 Adminconsole")
    st.info("Beheer deelnemers en bestanden (placeholder).")

# ------------------ ADMIN LOGIN ------------------
if not st.session_state.get("admin_access"):
    with st.expander("Ben jij de organisator?"):
        pw = st.text_input("Voer admincode in:", type="password")
        if pw == "JULES2025":
            st.session_state["admin_access"] = True
            st.experimental_rerun()
