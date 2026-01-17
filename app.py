import streamlit as st
from supabase import create_client

# --- KONFIGURACJA POŁĄCZENIA ---
# Dane pobierane z Secrets w Streamlit Cloud dla bezpieczeństwa
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(URL, KEY)

# --- LOGIKA MAGAZYNOWA (PYTHON) ---
def pobierz_produkty():
    """Pobiera wszystkie przedmioty z bazy danych."""
    response = supabase.table("magazyn").select("*").order("nazwa").execute()
    return response.data

def dodaj_produkt(nazwa, ilosc, cena):
    """Wstawia nowy rekord do tabeli."""
    data = {"nazwa": nazwa, "ilosc": ilosc, "cena": cena}
    return supabase.table("magazyn").insert(data).execute()

def usun_produkt(id_produktu):
    """Usuwa rekord na podstawie ID."""
    supabase.table("magazyn").delete().eq("id", id_produktu).execute()

def aktualizuj_stan(id_produktu, nowa_ilosc):
    """Zmienia ilość wybranego produktu."""
    supabase.table("magazyn").update({"ilosc": nowa_ilosc}).eq("id", id_produktu).execute()

# --- INTERFEJS UŻYTKOWNIKA (STREAMLIT) ---
st.set_page_config(page_title="System Magazynowy Pro", layout="wide")
st.title("📦 Magazyn 2.0")

# Sidebar - Dodawanie produktów
with st.sidebar:
    st.header("Dodaj nowy towar")
    with st.form("form_dodawania", clear_on_submit=True):
        nowa_nazwa = st.text_input("Nazwa przedmiotu")
        nowa_ilosc = st.number_input("Ilość", min_value=0, step=1)
        nowa_cena = st.number_input("Cena (PLN)", min_value=0.0, step=0.01)
        przycisk_dodaj = st.form_submit_button("Dodaj do bazy")
        
        if przycisk_dodaj and nowa_nazwa:
            dodaj_produkt(nowa_nazwa, nowa_ilosc, nowa_cena)
            st.success(f"Dodano: {nowa_nazwa}")
            st.rerun()

# Główny panel - Wyświetlanie i Zarządzanie
produkty = pobierz_produkty()

if not produkty:
    st.info("Magazyn jest pusty. Dodaj pierwszy produkt w panelu bocznym.")
else:
    # Wyświetlanie danych w formie czytelnej tabeli
    cols = st.columns([1, 3, 2, 2, 2])
    cols[0].bold("ID")
    cols[1].bold("Nazwa")
    cols[2].bold("Ilość")
    cols[3].bold("Cena")
    cols[4].bold("Akcje")
    st.divider()

    for p in produkty:
        c1, c2, c3, c4, c5 = st.columns([1, 3, 2, 2, 2])
        c1.text(p['id'])
        c2.text(p['nazwa'])
        c3.text(p['ilosc'])
        c4.text(f"{p['cena']} zł")
        
        # Przycisk usuwania dla każdego wiersza
        if c5.button("Usuń", key=f"del_{p['id']}"):
            usun_produkt(p['id'])
            st.toast(f"Usunięto {p['nazwa']}")
            st.rerun()
