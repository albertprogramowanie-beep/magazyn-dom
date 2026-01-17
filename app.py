import streamlit as st
from supabase import create_client

# --- KONFIGURACJA POŁĄCZENIA ---
try:
    URL = st.secrets["SUPABASE_URL"]
    KEY = st.secrets["SUPABASE_KEY"]
    supabase = create_client(URL, KEY)
except Exception as e:
    st.error("Błąd konfiguracji Secrets! Upewnij się, że dodałeś SUPABASE_URL i SUPABASE_KEY.")
    st.stop()

# --- LOGIKA BIZNESOWA (FUNKCJE PYTHON) ---
def pobierz_wszystkie_produkty():
    """Pobiera listę produktów posortowaną alfabetycznie."""
    response = supabase.table("magazyn").select("*").order("nazwa").execute()
    return response.data

def dodaj_nowy_produkt(nazwa, ilosc, cena):
    """Dodaje rekord do bazy danych."""
    nowy_towar = {"nazwa": nazwa, "ilosc": ilosc, "cena": cena}
    supabase.table("magazyn").insert(nowy_towar).execute()

def usun_produkt_z_bazy(id_produktu):
    """Usuwa rekord na podstawie unikalnego ID."""
    supabase.table("magazyn").delete().eq("id", id_produktu).execute()

# --- INTERFEJS UŻYTKOWNIKA (STREAMLIT) ---
st.set_page_config(page_title="Magazyn Domowy", layout="wide", page_icon="📦")
st.title("📦 System Zarządzania Magazynem")

# --- PANEL BOCZNY: DODAWANIE ---
with st.sidebar:
    st.header("➕ Dodaj nowy przedmiot")
    with st.form("formularz_dodawania", clear_on_submit=True):
        nazwa_input = st.text_input("Nazwa przedmiotu", placeholder="np. Młotek")
        ilosc_input = st.number_input("Ilość (szt.)", min_value=0, step=1)
        cena_input = st.number_input("Cena jednostkowa (PLN)", min_value=0.0, format="%.2f")
        
        przycisk_wyslij = st.form_submit_button("Zapisz w magazynie")
        
        if przycisk_wyslij:
            if nazwa_input:
                dodaj_nowy_produkt(nazwa_input, ilosc_input, cena_input)
                st.success(f"Dodano: {nazwa_input}")
                st.rerun()
            else:
                st.warning("Musisz podać nazwę produktu!")

# --- GŁÓWNY WIDOK: TABELA ---
st.subheader("📋 Aktualny stan zapasów")
produkty = pobierz_wszystkie_produkty()

if not produkty:
    st.info("Twój magazyn jest obecnie pusty. Skorzystaj z panelu bocznego, aby dodać towary.")
else:
    # Nagłówki tabeli (Naprawione: używamy .markdown zamiast nieistniejącego .bold)
    naglowki = st.columns([1, 4, 2, 2, 2])
    naglowki[0].markdown("**ID**")
    naglowki[1].markdown("**Nazwa produktu**")
    naglowki[2].markdown("**Ilość**")
    naglowki[3].markdown("**Cena**")
    naglowki[4].markdown("**Akcje**")
    st.divider()

    # Wyświetlanie wierszy danych
    for p in produkty:
        c1, c2, c3, c4, c5 = st.columns([1, 4, 2, 2, 2])
        
        c1.text(p['id'])
        c2.text(p['nazwa'])
        c3.text(f"{p['ilosc']} szt.")
        c4.text(f"{p['cena']:.2f} zł")
        
        # Przycisk usuwania
        if c5.button("🗑️ Usuń", key=f"usun_{p['id']}"):
            usun_produkt_z_bazy(p['id'])
            st.toast(f"Usunięto przedmiot: {p['nazwa']}")
            st.rerun()

# --- STOPKA Z PODSUMOWANIEM ---
st.divider()
total_wartosc = sum(p['ilosc'] * p['cena'] for p in produkty)
st.metric("Całkowita wartość magazynu", f"{total_wartosc:.2f} PLN")
