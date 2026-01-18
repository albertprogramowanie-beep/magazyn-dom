import streamlit as st
from supabase import create_client
from datetime import datetime

# --- POŁĄCZENIE (Zabezpieczone przed ucięciem klucza) ---
@st.cache_resource
def get_supabase():
    url = st.secrets["SUPABASE_URL"].strip()
    key = st.secrets["SUPABASE_KEY"].strip()
    return create_client(url, key)

supabase = get_supabase()

# --- FUNKCJE LOGICZNE ---
def pobierz_produkty():
    res = supabase.table("magazyn").select("*").order("data_dodania", ascending=False).execute()
    return res.data if res.data else []

def dodaj_produkt(n, i, c, d):
    supabase.table("magazyn").insert({"nazwa": n, "ilosc": i, "cena": c, "data_dodania": str(d)}).execute()

def aktualizuj_stan(id_p, nowa_ilosc):
    if nowa_ilosc <= 0:
        supabase.table("magazyn").delete().eq("id", id_p).execute()
    else:
        supabase.table("magazyn").update({"ilosc": nowa_ilosc}).eq("id", id_p).execute()

# --- INTERFEJS ---
st.set_page_config(page_title="Magazyn Domowy", layout="wide")
st.title("📦 System Zarządzania Magazynem")

# Pasek boczny: Dodawanie
with st.sidebar:
    st.header("➕ Dodaj produkt")
    with st.form("form_add", clear_on_submit=True):
        n = st.text_input("Nazwa")
        i = st.number_input("Ilość", min_value=1, step=1)
        c = st.number_input("Cena (PLN)", min_value=0.0, format="%.2f")
        d = st.date_input("Data dostawy", value=datetime.now())
        if st.form_submit_button("Zapisz w bazie"):
            if n:
                dodaj_produkt(n, i, c, d)
                st.rerun()

# Widok główny
produkty = pobierz_produkty()

if not produkty:
    st.info("Magazyn jest pusty.")
else:
    # Wyświetlanie tabeli
    cols = st.columns([1, 3, 2, 2, 2, 2])
    cols[0].write("**ID**"); cols[1].write("**Nazwa**"); cols[2].write("**Ilość**")
    cols[3].write("**Cena**"); cols[4].write("**Data**"); cols[5].write("**Akcje**")
    st.divider()

    for p in produkty:
        c1, c2, c3, c4, c5, c6 = st.columns([1, 3, 2, 2, 2, 2])
        c1.text(p['id'])
        c2.text(p['nazwa'])
        c3.text(f"{p['ilosc']} szt.")
        c4.text(f"{p['cena']:.2f} zł")
        c5.text(p.get('data_dodania', '---'))
        
        with c6.popover("⚙️"):
            ile = st.number_input("Ile sztuk odjąć?", 1, p['ilosc'], key=f"del_{p['id']}")
            if st.button("Zdejmij", key=f"btn_{p['id']}", use_container_width=True):
                aktualizuj_stan(p['id'], p['ilosc'] - ile)
                st.rerun()
            if st.button("Usuń całość", key=f"all_{p['id']}", type="primary", use_container_width=True):
                aktualizuj_stan(p['id'], 0)
                st.rerun()
