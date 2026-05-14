from supabase import create_client
import ssl

# ✅ FIX SSL (compatibile con la tua versione)
ssl._create_default_https_context = ssl._create_unverified_context

url = "https://lmqbydfzqyolwsjjydye.supabase.co"
key = "METTI_QUI_LA_TUA_API_KEY"

supabase = create_client(url, key)
