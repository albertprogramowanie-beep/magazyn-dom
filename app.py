import streamlit as st
from supabase import create_client
from datetime import datetime

# --- POŁĄCZENIE ---
@st.cache_resource
def get_supabase():
    try:
        url = st.secrets["SUPABASE_URL"].strip()
        key = st.secrets["SUPABASE_KEY"].strip()
        return create_client(url, key)
    except Exception as e:
        st.error(f"Błąd konfiguracji: {e}")
        return None

client = get_supabase()

# --- FUNKCJE ---
def pobierz_produkty():
    if client is None: return []
    try:
        # Poprawka sortowania dla nowej wersji biblioteki
        res = client.table("magazyn").select("*").order("data_dodania", desc=True).execute()
        return res.data if res.data else []
    except Exception:
        res = client.table("magazyn").select("*").execute()
        return res.data if res.data else []

def aktualizuj_stan(id_p, nowa_ilosc):
    if nowa_ilosc <= 0:
        client.table("magazyn").delete().eq("id", id_p).execute()
    else:
        client.table("magazyn").update({"ilosc": nowa_ilosc}).eq("id", id_p).execute()

# --- INTERFEJS ---
st.set_page_config(page_title="Magazyn Domowy", layout="wide")
st.title("📦 System Zarządzania Magazynem")

if client:
    # --- PANEL BOCZNY (DODAWANIE) ---
    with st.sidebar:
        st.header("➕ Dodaj produkt")
        with st.form("add_form", clear_on_submit=True):
            n = st.text_input("Nazwa")
            i = st.number_input("Ilość", min_value=1)
            c = st.number_input("Cena za szt. (zł)", min_value=0.0, format="%.2f")
            d = st.date_input("Data", value=datetime.now())
            if st.form_submit_button("Zapisz w bazie"):
                if n:
                    client.table("magazyn").insert({
                        "nazwa": n, "ilosc": i, "cena": c, "data_dodania": str(d)
                    }).execute()
                    st.rerun()

    # --- POBIERANIE I OBLICZENIA ---
    produkty = pobierz_produkty()
    
    if produkty:
        # Obliczenia statystyk
        calkowita_liczba_sztuk = sum(p['ilosc'] for p in produkty)
        laczna_wartosc = sum(p['ilosc'] * p['cena'] for p in produkty)
        liczba_pozycji = len(produkty)

        # --- SEKCJA PODSUMOWANIA ---
        st.subheader("📊 Podsumowanie")
        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.metric("Wszystkich przedmiotów", f"{calkowita_liczba_sztuk} szt.")
        col_s2.metric("Łączna wartość", f"{laczna_wartosc:,.2f} zł")
        col_s3.metric("Liczba rodzajów produktów", liczba_pozycji)
        
        st.divider()

        # --- LISTA PRODUKTÓW ---
        st.subheader("📋 Lista towarów")
        for p in produkty:
            cols = st.columns([3, 2, 2, 2])
            cols[0].write(f"**{p['nazwa']}**")
            cols[1].write(f"{p['ilosc']} szt. x {p['cena']:.2f} zł")
            cols[2].write(f"Wartość: **{p['ilosc'] * p['cena']:.2f} zł**")
            
            with cols[3].popover("Zarządzaj"):
                ile = st.number_input("Ile odjąć?", 1, p['ilosc'], key=f"d_{p['id']}")
                if st.button("Odejmij sztuki", key=f"b_{p['id']}", use_container_width=True):
                    aktualizuj_stan(p['id'], p['ilosc'] - ile)
                    st.rerun()
                if st.button("Usuń całkowicie", key=f"all_{p['id']}", type="primary", use_container_width=True):
                    aktualizuj_stan(p['id'], 0)
                    st.rerun()
    else:
        st.info("Magazyn jest pusty. Dodaj pierwszy produkt w panelu bocznym.")
else:
    st.error("Brak połączenia z bazą danych.")
