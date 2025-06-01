import streamlit as st
import pandas as pd
from datetime import date
from utils.io import load_data, save_data

DATA_PATH = "data/teslimatlar.csv"

st.set_page_config(page_title="Plan Ekle", layout="centered")
st.title("➕ Yeni Teslimat Planı Ekle")

# 🔽 Tarih ve Gün Seçimi
tarih = st.date_input("📅 Tarih", value=date.today())
gun = tarih.strftime("%A")  # örnek: Monday

# 📦 Tur ve Açıklama Bilgisi
tur_adi = st.text_input("🚚 Tur Adı (örn: 1. Tur, Sabah Turu)", max_chars=50)
aciklama = st.text_input("📝 Açıklama", max_chars=100)

# 🧾 Müşteri Bilgileri
musteri_listesi = []
max_musteri = 20

st.markdown("### 👤 Müşteri Listesi")

for i in range(max_musteri):
    musteri = st.text_input(f"{i+1}. Müşteri", key=f"musteri_{i}")
    if musteri.strip():
        notu = st.text_input(f"↪️ Not (isteğe bağlı)", key=f"not_{i}", placeholder="örn: Tahsilat yapılacak")
        musteri_listesi.append({
            "musteri": musteri.strip(),
            "not": notu.strip()
        })
    else:
        break

if st.button("💾 Kaydet"):
    if not tur_adi:
        st.error("Lütfen tur adını girin.")
    elif len(musteri_listesi) == 0:
        st.error("Lütfen en az bir müşteri girin.")
    else:
        df = load_data(DATA_PATH)
        for sira_no, m in enumerate(musteri_listesi, start=1):
            yeni_kayit = {
                "tarih": tarih,
                "gun": gun,
                "tur": tur_adi,
                "aciklama": aciklama,
                "sira": sira_no,
                "musteri": m["musteri"],
                "not": m["not"]
            }
            df = pd.concat([df, pd.DataFrame([yeni_kayit])], ignore_index=True)
        save_data(df, DATA_PATH)
        st.success("Teslimat planı başarıyla kaydedildi.")
