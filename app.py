import streamlit as st
from supabase import create_client
from datetime import datetime

# --- KONFIGURACJA POŁĄCZENIA ---
@st.cache_resource
def get_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Problem z kluczami API: {e}")
        return None

supabase = get_supabase()

# --- LOGIKA BAZY ---
def pobierz_dane():
    if supabase is None: return []
    try:
        # Próba pobrania z sortowaniem po dacie
        res = supabase.table("magazyn").select("*").order("data_dodania", ascending=False).execute()
        return res.data if res.data else []
    except Exception:
        # Awaryjne pobranie bez sortowania
        res = supabase.table("magazyn").select("*").execute()
        return res.data if res.data else []

def dodaj_dane(n, i, c, d):
    if supabase:
        supabase.table("magazyn").insert({
            "nazwa": n, "ilosc": i, "cena": c, "data_dodania": str(d)
        }).execute()

# --- INTERFEJS ---
st.title("📦 Mój Magazyn")

if supabase:
    # Formularz w Sidebarze
    with st.sidebar:
        st.header("Nowy Produkt")
        with st.form("add", clear_on_submit=True):
            nazwa = st.text_input("Nazwa")
            ilosc = st.number_input("Ilość", min_value=1)
            cena = st.number_input("Cena (zł)", min_value=0.0)
            data = st.date_input("Data", value=datetime.now())
            if st.form_submit_button("Dodaj"):
                if nazwa:
                    dodaj_dane(nazwa, ilosc, cena, data)
                    st.rerun()

    # Wyświetlanie
    produkty = pobierz_dane()
    if produkty:
        st.write("### Lista towarów:")
        st.dataframe(produkty, use_container_width=True)
    else:
        st.info("Magazyn jest pusty.")
