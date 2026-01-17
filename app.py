import streamlit as st
from supabase import create_client

# --- KONFIGURACJA POŁĄCZENIA ---
try:
    URL = st.secrets["SUPABASE_URL"]
    KEY = st.secrets["SUPABASE_KEY"]
    supabase = create_client(URL, KEY)
except Exception as e:
    st.error("Błąd konfiguracji Secrets!")
    st.stop()

# --- LOGIKA BIZNESOWA (FUNKCJE PYTHON) ---
def pobierz_wszystkie_produkty():
    response = supabase.table("magazyn").select("*").order("nazwa").execute()
    return response.data

def dodaj_nowy_produkt(nazwa, ilosc, cena):
    supabase.table("magazyn").insert({"nazwa": nazwa, "ilosc": ilosc, "cena": cena}).execute()

def aktualizuj_ilosc(id_produktu, nowa_ilosc):
    """Zmienia ilość produktu na nową wartość."""
    if nowa_ilosc <= 0:
        # Jeśli ilość spadnie do 0, usuwamy produkt całkowicie
        supabase.table("magazyn").delete().eq("id", id_produktu).execute()
    else:
        # W przeciwnym razie tylko aktualizujemy liczbę
        supabase.table("magazyn").update({"ilosc": nowa_ilosc}).eq("id", id_produktu).execute()

# --- INTERFEJS UŻYTKOWNIKA (STREAMLIT) ---
st.set_page_config(page_title="Magazyn Domowy", layout="wide", page_icon="📦")
st.title("📦 System Zarządzania Magazynem")

# --- PANEL BOCZNY: DODAWANIE ---
with st.sidebar:
    st.header("➕ Dodaj nowy przedmiot")
    with st.form("formularz_dodawania", clear_on_submit=True):
        nazwa_input = st.text_input("Nazwa przedmiotu")
        ilosc_input = st.number_input("Ilość (szt.)", min_value=1, step=1)
        cena_input = st.number_input("Cena (PLN)", min_value=0.0, format="%.2f")
        if st.form_submit_button("Zapisz w magazynie"):
            if nazwa_input:
                dodaj_nowy_produkt(nazwa_input, ilosc_input, cena_input)
                st.rerun()

# --- GŁÓWNY WIDOK: TABELA ---
st.subheader("📋 Aktualny stan zapasów")
produkty = pobierz_wszystkie_produkty()

if not produkty:
    st.info("Magazyn jest pusty.")
else:
    # Nagłówki
    naglowki = st.columns([1, 4, 2, 2, 2])
    naglowki[0].markdown("**ID**")
    naglowki[1].markdown("**Nazwa produktu**")
    naglowki[2].markdown("**Ilość**")
    naglowki[3].markdown("**Cena**")
    naglowki[4].markdown("**Akcje**")
    st.divider()

    for p in produkty:
        c1, c2, c3, c4, c5 = st.columns([1, 4, 2, 2, 2])
        c1.text(p['id'])
        c2.text(p['nazwa'])
        c3.text(f"{p['ilosc']} szt.")
        c4.text(f"{p['cena']:.2f} zł")
        
        # --- NOWA FUNKCJA USUWANIA CZĘŚCIOWEGO ---
        with c5.popover("⚙️ Zarządzaj"):
            st.write(f"Produkt: **{p['nazwa']}**")
            ile_odjac = st.number_input(
                "Ile sztuk usunąć?", 
                min_value=1, 
                max_value=p['ilosc'], 
                key=f"val_{p['id']}"
            )
            
            if st.button(f"Zdejmij {ile_odjac} szt.", key=f"btn_{p['id']}", use_container_width=True):
                nowa_ilosc = p['ilosc'] - ile_odjac
                aktualizuj_ilosc(p['id'], nowa_ilosc)
                st.toast(f"Zaktualizowano {p['nazwa']}")
                st.rerun()
            
            st.divider()
            if st.button("🗑️ Usuń wszystko", key=f"del_all_{p['id']}", type="primary", use_container_width=True):
                aktualizuj_ilosc(p['id'], 0) # Przesłanie 0 usunie rekord
                st.rerun()

# --- STOPKA ---
st.divider()
total_wartosc = sum(p['ilosc'] * p['cena'] for p in produkty)
st.metric("Całkowita wartość magazynu", f"{total_wartosc:.2f} PLN")
