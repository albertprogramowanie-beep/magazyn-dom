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
        # POPRAWKA: Zmieniono 'ascending=False' na 'desc=True'
        res = client.table("magazyn").select("*").order("data_dodania", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        st.warning(f"Błąd sortowania: {e}. Próba pobrania bez sortowania...")
        res = client.table("magazyn").select("*").execute()
        return res.data if res.data else []

def aktualizuj_stan(id_p, nowa_ilosc):
    if nowa_ilosc <= 0:
        client.table("magazyn").delete().eq("id", id_p).execute()
    else:
        client.table("magazyn").update({"ilosc": nowa_ilosc}).eq("id", id_p).execute()

# --- INTERFEJS ---
st.title("📦 Magazyn Domowy")

if client:
    with st.sidebar:
        st.header("➕ Dodaj produkt")
        with st.form("add_form", clear_on_submit=True):
            n = st.text_input("Nazwa")
            i = st.number_input("Ilość", min_value=1)
            c = st.number_input("Cena (zł)", min_value=0.0)
            d = st.date_input("Data", value=datetime.now())
            if st.form_submit_button("Zapisz"):
                if n:
                    client.table("magazyn").insert({
                        "nazwa": n, "ilosc": i, "cena": c, "data_dodania": str(d)
                    }).execute()
                    st.rerun()

    produkty = pobierz_produkty()
    if not produkty:
        st.info("Brak produktów w bazie.")
    else:
        for p in produkty:
            cols = st.columns([3, 2, 2, 2])
            cols[0].write(f"**{p['nazwa']}**")
            cols[1].write(f"{p['ilosc']} szt.")
            cols[2].write(f"{p.get('data_dodania', '---')}")
            
            with cols[3].popover("Zarządzaj"):
                ile = st.number_input("Ile odjąć?", 1, p['ilosc'], key=f"d_{p['id']}")
                if st.button("Odejmij", key=f"b_{p['id']}", use_container_width=True):
                    aktualizuj_stan(p['id'], p['ilosc'] - ile)
                    st.rerun()
                if st.button("Usuń wszystko", key=f"all_{p['id']}", type="primary", use_container_width=True):
                    aktualizuj_stan(p['id'], 0)
                    st.rerun()
else:
    st.error("Nie udało się połączyć. Sprawdź sekrety.")
