import streamlit as st
from supabase import create_client

# --- DEBUGOWANIE ---
try:
    url = st.secrets["SUPABASE_URL"].strip()
    key = st.secrets["SUPABASE_KEY"].strip()
    
    # Wyświetlamy info dla nas (pomoże nam to sprawdzić czy klucz nie jest ucięty)
    st.write(f"🔍 Diagnoza: URL zaczyna się od: `{url[:15]}...`")
    st.write(f"🔍 Diagnoza: Długość klucza: `{len(key)}` znaków")
    
    supabase = create_client(url, key)
    
    # Próba prostego zapytania
    test = supabase.table("magazyn").select("count", count="exact").limit(1).execute()
    st.success("✅ Połączenie nawiązane pomyślnie!")
    
except Exception as e:
    st.error(f"❌ Błąd: {e}")
    st.info("Jeśli długość klucza jest mniejsza niż 80 znaków, prawdopodobnie jest on ucięty.")

# Reszta Twojego kodu...
st.title("📦 Magazyn - Test Połączenia")
