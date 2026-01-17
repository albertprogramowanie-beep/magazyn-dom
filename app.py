import streamlit as st
from supabase import create_client
from datetime import datetime

# --- POŁĄCZENIE ---
@st.cache_resource
def get_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        # Usuwamy ewentualne przypadkowe spacje z kluczy
        return create_client(url.strip(), key.strip())
    except Exception as e:
        st.error(f"Błąd konfiguracji kluczy: {e}")
        return None

supabase = get_supabase()

# --- LOGIKA BAZY ---
def pobierz_dane():
    if not supabase: return []
    try:
        # Pobieramy dane z nowej tabeli
        res = supabase.table("magazyn").select("*").order("data_dodania", ascending=False).execute()
        return res.data if res.data else []
    except Exception as e:
        st.warning(f"Błąd pobierania (próba bez sortowania): {e}")
        res = supabase.table("magazyn").select("*").execute()
        return res.data if res.data else []

def dodaj_dane(n, i, c, d):
    if supabase:
        supabase.table("magazyn").insert({
            "nazwa": n, "ilosc": i, "cena": c, "data_dodania": str(d)
        }).execute()

# --- INTERFEJS ---
st.set_page_config(page_title="Mój Magazyn", layout="wide")
st.title("📦 Mój Magazyn")

if supabase:
    with st.sidebar:
        st.header("Nowa Dostawa")
        with st.form("add_form", clear_on_submit=True):
            nazwa = st.text_input("Nazwa produktu")
            ilosc = st.number_input("Ilość", min_value=1)
            cena = st.number_input("Cena (zł)", min_value=0.0, format="%.2f")
            data = st.date_input("Data", value=datetime.now())
            if st.form_submit_button("Dodaj do magazynu"):
                if nazwa:
                    dodaj_dane(nazwa, ilosc, cena, data)
                    st.success("Dodano!")
                    st.rerun()

    produkty = pobierz_dane()
    if produkty:
        st.dataframe(produkty, use_container_width=True)
        suma = sum(p['ilosc'] * p['cena'] for p in produkty)
        st.metric("Łączna wartość", f"{suma:.2f} zł")
    else:
        st.info("Magazyn jest pusty. Dodaj pierwszy produkt w panelu bocznym.")
