from supabase import create_client
import ssl

# ✅ FIX SSL (compatibile con la tua versione)
ssl._create_default_https_context = ssl._create_unverified_context

url = "https://lmqbydfzqyolwsjjydye.supabase.co"
key = "sb_publishable__Mryk_lmsCyf6OZrfxzQ1w_j4tRTgLp"

supabase = create_client(url, key)
