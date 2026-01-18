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
        st.error(f"Problem z kluczami API: {e}")
        return None

supabase = get_supabase()

# --- LOGIKA BAZY ---
def pobierz_dane():
    try:
        res = supabase.table("magazyn").select("*").order("data_dodania", ascending=False).execute()
        return res.data if res.data else []
    except Exception:
        res = supabase.table("magazyn").select("*").execute()
        return res.data if res.data else []

def dodaj_produkt(n, i, c, d):
    supabase.table("magazyn").insert({
        "nazwa": n, "ilosc": i, "cena": c, "data_dodania": str(d)
    }).execute()

def aktualizuj_ilosc(id_p, nowa_ilosc):
    if nowa_ilosc <= 0:
        supabase.table("magazyn").delete().eq("id", id_p).execute()
    else:
        supabase.table("magazyn").update({"ilosc": nowa_ilosc}).eq("id", id_p).execute()

# --- INTERFEJS ---
st.set_page_config(page_title="Magazyn Domowy", layout="wide")
st.title("📦 System Zarządzania Magazynem")

if supabase:
    # Panel boczny: Dodawanie
    with st.sidebar:
        st.header("➕ Nowa dostawa")
        with st.form("add_form", clear_on_submit=True):
            n = st.text_input("Nazwa produktu")
            i = st.number_input("Ilość", min_value=1, step=1)
            c = st.number_input("Cena (zł)", min_value=0.0, format="%.2f")
            d = st.date_input("Data przychodu", value=datetime.now())
            if st.form_submit_button("Dodaj do bazy"):
                if n:
                    dodaj_produkt(n, i, c, d)
                    st.rerun()

    # Widok główny: Tabela
    produkty = pobierz_dane()
    if not produkty:
        st.info("Magazyn jest pusty.")
    else:
        # Nagłówki
        cols = st.columns([1, 3, 2, 2, 2, 2])
        cols[0].markdown("**ID**"); cols[1].markdown("**Nazwa**"); cols[2].markdown("**Ilość**")
        cols[3].markdown("**Cena**"); cols[4].markdown("**Data**"); cols[5].markdown("**Akcje**")
        st.divider()

        for p in produkty:
            c1, c2, c3, c4, c5, c6 = st.columns([1, 3, 2, 2, 2, 2])
            c1.text(p['id'])
            c2.text(p['nazwa'])
            c3.text(f"{p['ilosc']} szt.")
            c4.text(f"{p['cena']:.2f} zł")
            c5.text(p.get('data_dodania', '---'))
            
            with c6.popover("⚙️ Zarządzaj"):
                ile = st.number_input("Ile sztuk usunąć?", min_value=1, max_value=p['ilosc'], key=f"i_{p['id']}")
                if st.button(f"Zdejmij {ile} szt.", key=f"b_{p['id']}", use_container_width=True):
                    aktualizuj_ilosc(p['id'], p['ilosc'] - ile)
                    st.rerun()
                if st.button("🗑️ Usuń wszystko", key=f"all_{p['id']}", type="primary", use_container_width=True):
                    aktualizuj_ilosc(p['id'], 0)
                    st.rerun()

    # Podsumowanie
    st.divider()
    total = sum(p['ilosc'] * p['cena'] for p in produkty) if produkty else 0
    st.metric("Całkowita wartość", f"{total:.2f} PLN")
