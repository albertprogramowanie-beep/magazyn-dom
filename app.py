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
        # Sortowanie od najnowszych
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
            d = st.date_input("Data przychodu", value=datetime.now())
            if st.form_submit_button("Zapisz w bazie"):
                if n:
                    client.table("magazyn").insert({
                        "nazwa": n, "ilosc": i, "cena": c, "data_dodania": str(d)
                    }).execute()
                    st.rerun()

    # --- POBIERANIE I OBLICZENIA ---
    produkty = pobierz_produkty()
    
    if produkty:
        # Statystyki
        calkowita_liczba_sztuk = sum(p['ilosc'] for p in produkty)
        laczna_wartosc = sum(p['ilosc'] * p['cena'] for p in produkty)

        st.subheader("📊 Podsumowanie")
        col_s1, col_s2 = st.columns(2)
        col_s1.metric("Wszystkich przedmiotów", f"{calkowita_liczba_sztuk} szt.")
        col_s2.metric("Łączna wartość magazynu", f"{laczna_wartosc:,.2f} zł")
        
        st.divider()

        # --- LISTA PRODUKTÓW Z DATĄ ---
        st.subheader("📋 Lista towarów")
        
        # Nagłówki tabeli dla lepszej czytelności
        h1, h2, h3, h4, h5 = st.columns([3, 2, 2, 2, 2])
        h1.markdown("**Nazwa produktu**")
        h2.markdown("**Data dodania**")
        h3.markdown("**Ilość i cena**")
        h4.markdown("**Wartość**")
        h5.markdown("**Akcje**")
        st.write("")

        for p in produkty:
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 2])
            
            col1.write(f"**{p['nazwa']}**")
            # Wyświetlanie daty dodania
            col2.write(f"📅 {p.get('data_dodania', '---')}")
            col3.write(f"{p['ilosc']} szt. x {p['cena']:.2f} zł")
            col4.write(f"**{p['ilosc'] * p['cena']:.2f} zł**")
            
            with col5.popover("⚙️"):
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
    st.error("Brak połączenia z bazą danych. Sprawdź sekrety.")
