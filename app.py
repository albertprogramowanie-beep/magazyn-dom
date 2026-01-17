import streamlit as st
from supabase import create_client
from datetime import datetime

# --- POŁĄCZENIE ---
@st.cache_resource # Zapamiętuje połączenie, by nie tworzyć go co sekundę
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()

# --- FUNKCJE ---
def pobierz_produkty():
    try:
        # Próba pobrania z sortowaniem
        res = supabase.table("magazyn").select("*").order("data_dodania", ascending=False).execute()
        return res.data if res.data is not None else []
    except Exception:
        # Jeśli sortowanie zawiedzie, pobierz bez niego
        res = supabase.table("magazyn").select("*").execute()
        return res.data if res.data is not None else []

def dodaj_produkt(nazwa, ilosc, cena, data):
    # Ważne: str(data) zamienia obiekt daty na format tekstowy YYYY-MM-DD
    supabase.table("magazyn").insert({
        "nazwa": nazwa, 
        "ilosc": ilosc, 
        "cena": cena, 
        "data_dodania": str(data)
    }).execute()

# --- INTERFEJS ---
st.title("📦 Magazyn z obsługą dat")

# Formularz w Sidebarze
with st.sidebar:
    st.header("➕ Nowa dostawa")
    with st.form("add_form", clear_on_submit=True):
        n = st.text_input("Nazwa")
        i = st.number_input("Ilość", min_value=1)
        c = st.number_input("Cena (zł)", min_value=0.0)
        d = st.date_input("Data przychodu", value=datetime.now())
        if st.form_submit_button("Dodaj do bazy"):
            if n:
                dodaj_produkt(n, i, c, d)
                st.success("Dodano!")
                st.rerun()

# Wyświetlanie tabeli
dane = pobierz_produkty()

if not dane:
    st.info("Brak towarów w bazie.")
else:
    # Wyświetlamy jako prostą tabelę Streamlit (najbezpieczniejsza opcja)
    st.table(dane)

    # Podsumowanie wartości
    suma = sum(p['ilosc'] * p['cena'] for p in dane)
    st.metric("Całkowita wartość", f"{suma:.2f} zł")
