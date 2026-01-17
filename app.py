import streamlit as st
from supabase import create_client
from datetime import datetime

# --- KONFIGURACJA POŁĄCZENIA ---
try:
    URL = st.secrets["SUPABASE_URL"]
    KEY = st.secrets["SUPABASE_KEY"]
    supabase = create_client(URL, KEY)
except Exception:
    st.error("Błąd konfiguracji Secrets w Streamlit Cloud!")
    st.stop()

# --- FUNKCJE LOGICZNE ---
def pobierz_produkty():
    # Sortujemy od najnowszej daty dodania
    res = supabase.table("magazyn").select("*").order("data_dodania", ascending=False).execute()
    return res.data

def dodaj_produkt(nazwa, ilosc, cena, data):
    supabase.table("magazyn").insert({
        "nazwa": nazwa, 
        "ilosc": ilosc, 
        "cena": cena, 
        "data_dodania": str(data)
    }).execute()

def aktualizuj_stan(id_p, nowa_ilosc):
    if nowa_ilosc <= 0:
        supabase.table("magazyn").delete().eq("id", id_p).execute()
    else:
        supabase.table("magazyn").update({"ilosc": nowa_ilosc}).eq("id", id_p).execute()

# --- INTERFEJS ---
st.set_page_config(page_title="Magazyn Domowy", layout="wide")
st.title("📦 Magazyn z obsługą dat")

# Sidebar: Dodawanie
with st.sidebar:
    st.header("➕ Nowa dostawa")
    with st.form("dodaj_form", clear_on_submit=True):
        n = st.text_input("Nazwa")
        i = st.number_input("Ilość", min_value=1, step=1)
        c = st.number_input("Cena (zł)", min_value=0.0, format="%.2f")
        d = st.date_input("Data przychodu", value=datetime.now())
        if st.form_submit_button("Dodaj do bazy"):
            if n:
                dodaj_produkt(n, i, c, d)
                st.rerun()

# Widok główny
produkty = pobierz_produkty()

if not produkty:
    st.info("Magazyn jest pusty.")
else:
    # Poprawione nagłówki (Markdown zamiast .bold)
    naglowki = st.columns([1, 3, 2, 2, 2, 2])
    naglowki[0].markdown("**ID**")
    naglowki[1].markdown("**Nazwa**")
    naglowki[2].markdown("**Ilość**")
    naglowki[3].markdown("**Cena**")
    naglowki[4].markdown("**Data**")
    naglowki[5].markdown("**Akcje**")
    st.divider()

    for p in produkty:
        c1, c2, c3, c4, c5, c6 = st.columns([1, 3, 2, 2, 2, 2])
        c1.text(p['id'])
        c2.text(p['nazwa'])
        c3.text(f"{p['ilosc']} szt.")
        c4.text(f"{p['cena']:.2f} zł")
        c5.text(p.get('data_dodania', '---'))
        
        with c6.popover("⚙️ Edytuj"):
            ile = st.number_input("Ile sztuk zdjąć?", min_value=1, max_value=p['ilosc'], key=f"i_{p['id']}")
            if st.button(f"Usuń {ile} szt.", key=f"b_{p['id']}", use_container_width=True):
                aktualizuj_stan(p['id'], p['ilosc'] - ile)
                st.rerun()
            if st.button("🗑️ Usuń całość", key=f"all_{p['id']}", type="primary", use_container_width=True):
                aktualizuj_stan(p['id'], 0)
                st.rerun()

# Podsumowanie
st.divider()
total = sum(p['ilosc'] * p['cena'] for p in produkty)
st.metric("Wartość całkowita towarów", f"{total:.2f} PLN")
