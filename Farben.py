import streamlit as st
import random
import json
import os
import pandas as pd
from matplotlib import colors as mcolors
from streamlit_extras.stylable_container import stylable_container
import warnings
warnings.filterwarnings("ignore")

st.set_option("client.showErrorDetails", False)

st.set_page_config(layout="wide")

st.title("Dss große Häkelrunden Farb-Duell")
show_name = st.checkbox("Farbname anzeigen", value=True)
# ---------- XKCD Farben laden ----------
colors = [c.replace("xkcd:", "") for c in mcolors.XKCD_COLORS.keys()]

FILE = "votes.json"

# ---------- Stimmen laden ----------
if os.path.exists(FILE):
    with open(FILE, "r") as f:
        scores = json.load(f)
else:
    scores = {}

# fehlende Farben automatisch hinzufügen
for c in colors:
    if c not in scores:
        scores[c] = 0

# ---------- Duell speichern ----------
if "duel" not in st.session_state:
    st.session_state.duel = random.sample(colors, 2)
if "duels" not in st.session_state:
    st.session_state.duels = {c: 0 for c in colors}
    
c1, c2 = st.session_state.duel

st.subheader("Welche Farbe gefällt dir besser?")

# ---------- Farb-Button Funktion ----------
def colored_button(label, key):
    hex_color = mcolors.XKCD_COLORS["xkcd:" + label]
    print(hex_color)
    if show_name:
        button_text = label
    else:
        button_text = " "

    with stylable_container(
        key,
        css_styles=f"""
        button {{
            background-color: {hex_color};
            color: black;
            height: 150px;
            font-size: 22px;
            font-weight: bold;
            border-radius: 20px;
        }}
        """,
    ):

       return st.button(button_text, key=key, use_container_width=True)

# ---------- Zwei große Farb-Buttons ----------
col1, col2 = st.columns(2)

with col1:
    vote1 = colored_button(c1, "btn1")

with col2:
    vote2 = colored_button(c2, "btn2")

# ---------- Abstimmen ----------
if vote1:
    scores[c1] += 1
    scores[c2] -= 1
    st.session_state.duels[c1] += 1
    st.session_state.duels[c2] += 1

    st.session_state.duel = random.sample(colors, 2)

    with open(FILE, "w") as f:
        json.dump(scores, f)

    st.rerun()

if vote2:
    scores[c2] += 1
    scores[c1] -= 1
    st.session_state.duels[c1] += 1
    st.session_state.duels[c2] += 1

    st.session_state.duel = random.sample(colors, 2)

    with open(FILE, "w") as f:
        json.dump(scores, f)

    st.rerun()

st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")

# ---------- Ranking anzeigen / verbergen ----------
if "show_ranking" not in st.session_state:
    st.session_state.show_ranking = False

if not st.session_state.show_ranking:
    if st.button("Ergebnisse einblenden"):
        st.session_state.show_ranking = True
        st.rerun()
else:
    if st.button("Ergebnisse ausblenden"):
        st.session_state.show_ranking = False
        st.rerun()

# ---------- Ranking ----------
if st.session_state.show_ranking:
    st.subheader("Aktuelles Ranking")

    ranking = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    for i, (color, score) in enumerate(ranking, 1):

        hex_color = mcolors.XKCD_COLORS["xkcd:" + color]
        duels = st.session_state.duels[color]
        if duels > 0:
            ratio = round((score + duels) / (2 * duels), 2)
        else:
            ratio = 0

        st.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:15px; margin-bottom:8px;">
                <div style="
                    width:25px;
                    height:25px;
                    background-color:{hex_color};
                    border-radius:6px;
                    border:1px solid black;
                "></div>

                    {i}. {color} – {score} Punkte – Gewinn-Quote: {ratio}
            </div>
            """,           
            unsafe_allow_html=True
        )

st.write("")
st.write("")
st.write("")
st.write("")

# ---------- CSV Export ganz unten ----------
st.markdown("---")
st.markdown("### Datenverwaltung")

df = pd.DataFrame(
    sorted(scores.items(), key=lambda x: x[1], reverse=True),
    columns=["Farbe", "Punkte"]
)

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Ergebnis als CSV herunterladen",
    data=csv,
    file_name="farben_ranking.csv",
    mime="text/csv",
)

if "confirm_reset" not in st.session_state:
    st.session_state.confirm_reset = False

if not st.session_state.confirm_reset:
    if st.button("Hard Reset starten"):
        st.session_state.confirm_reset = True
        st.rerun()

else:
    st.warning("Bist du sicher? Alle Stimmen werden gelöscht!")

    col1, col2 = st.columns(2)

    if col1.button("Ja, alles löschen"):
        if os.path.exists(FILE):
            os.remove(FILE)

        st.session_state.duel = random.sample(colors, 2)
        st.session_state.duels = {c: 0 for c in colors}
        st.session_state.show_ranking = False
        st.session_state.confirm_reset = False

        st.success("Alle Stimmen wurden gelöscht.")
        st.rerun()

    if col2.button("Abbrechen"):
        st.session_state.confirm_reset = False
        st.rerun()
