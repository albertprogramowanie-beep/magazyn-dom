import streamlit as st
from supabase import create_client
from datetime import datetime

# --- POŁĄCZENIE ---
@st.cache_resource
def get_supabase():
    try:
        url = st.secrets["SUPABASE_URL"].strip()
        key = st.secrets["SUPABASE_KEY"].strip()
        if len(key) < 60:
            st.warning(f"Klucz jest za krótki ({len(key)} znaków). Skopiuj go ponownie!")
            return None
        return create_client(url, key)
    except Exception as e:
        st.error(f"Błąd konfiguracji: {e}")
        return None

client = get_supabase()

# --- FUNKCJE ---
def pobierz_produkty():
    if client is None: return []
    try:
        res = client.table("magazyn").select("*").order("data_dodania", ascending=False).execute()
        return res.data if res.data else []
    except Exception as e:
        st.error(f"Błąd bazy: {e}")
        return []

def aktualizuj_stan(id_p, nowa_ilosc):
    if nowa_ilosc <= 0:
        client.table("magazyn").delete().eq("id", id_p).execute()
    else:
        client.table("magazyn").update({"ilosc": nowa_ilosc}).eq("id", id_p).execute()

# --- INTERFEJS ---
st.title("📦 Magazyn Domowy")

if client:
    # Panel boczny: Dodawanie
    with st.sidebar:
        st.header("➕ Dodaj produkt")
        with st.form("add_form", clear_on_submit=True):
            n = st.text_input("Nazwa")
            i = st.number_input("Ilość", 1)
            c = st.number_input("Cena", 0.0)
            d = st.date_input("Data", datetime.now())
            if st.form_submit_button("Zapisz"):
                client.table("magazyn").insert({"nazwa":n, "ilosc":i, "cena":c, "data_dodania":str(d)}).execute()
                st.rerun()

    # Tabela
    produkty = pobierz_produkty()
    if not produkty:
        st.info("Brak produktów.")
    else:
        for p in produkty:
            cols = st.columns([3, 2, 2, 2])
            cols[0].write(f"**{p['nazwa']}**")
            cols[1].write(f"{p['ilosc']} szt.")
            cols[2].write(f"{p.get('data_dodania', '---')}")
            
            with cols[3].popover("Odejmij"):
                ile = st.number_input("Ile sztuk?", 1, p['ilosc'], key=f"d_{p['id']}")
                if st.button("Zatwierdź", key=f"b_{p['id']}"):
                    aktualizuj_stan(p['id'], p['ilosc'] - ile)
                    st.rerun()
else:
    st.error("Nie udało się połączyć z bazą danych. Sprawdź klucze w Secrets.")
