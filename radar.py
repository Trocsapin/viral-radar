import streamlit as st
from google import genai
import tempfile
import os
import time

# --- ARAYÜZ YAPILANDIRMASI ---
st.set_page_config(page_title="Viral İçerik Motoru", page_icon="👁️", layout="centered")

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stButton>button {
    width: 100%; 
    border-radius: 8px; 
    font-weight: bold; 
    background-color: #FF0000; 
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("👁️ Videodan X (Twitter) Gönderisine")
st.markdown("İndirdiğiniz herhangi bir videoyu yükleyin. Yapay zeka videoyu kare kare izlesin, konuyu anlasın ve X'te en çok etkileşim alacak o 'doğal insan' metnini anında yazsın.")
st.markdown("---")

# --- API ANAHTARI ---
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# --- KULLANICI GİRDİSİ ---
st.markdown("#### 1. Videoyu Yükleyin")
yuklenen_video = st.file_uploader("📹 MP4 veya MOV dosyanızı buraya sürükleyin", type=["mp4", "mov", "avi"])

st.markdown("#### 2. Nasıl Bir Gönderi İstiyorsunuz?")
format_secimi = st.radio(
    "",
    ["Tekli Vurucu Tweet (Kısa ve öz merak uyandırıcı)", "Bilgi Seli / Flood (Detaylı, okuması keyifli maddeler)"]
)

st.markdown("---")

if st.button("🚀 Videoyu İzle ve Gönderiyi Yaz"):
    if not yuklenen_video:
        st.warning("Lütfen yapay zekanın izlemesi için bir video yükleyin.")
    else:
        with st.spinner("Yapay zeka videoyu baştan sona izliyor, detayları analiz ediyor... (Bu işlem videonun uzunluğuna göre 30-60 saniye sürebilir)"):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                    tmp_file.write(yuklenen_video.read())
                    tmp_file_path = tmp_file.name
                
                client = genai.Client(api_key=GEMINI_API_KEY)
                video_dosyasi = client.files.upload(file=tmp_file_path)
                
                while True:
                    dosya_durumu = client.files.get(name=video_dosyasi.name)
                    if dosya_durumu.state.name == "ACTIVE":
                        break
                    elif dosya_durumu.state.name == "FAILED":
                        raise Exception("Video yapay zeka tarafından işlenemedi.")
                    time.sleep(3)
                
                # --- GÜNCELLENEN PROMPT (BAŞLIK KÖRLÜĞÜ VE HASHTAG EKLENDİ) ---
                prompt = f"""
                GÖREV: Sana yüklediğim bu videoyu çok dikkatlice izle. Videonun dosya adına KESİNLİKLE aldırış etme, yanıltıcı olabilir. Sadece kendi gözlerinle gördüğün görsel ve işitsel detaylara odaklanarak içeriğinde tam olarak ne olduğunu, yapılan işlemi (hangi teknik, metod veya mühendislik uygulaması olduğunu) harika bir şekilde analiz et.
                
                Şimdi, bu videoyu X'te (Twitter) paylaşmak için Türkçe bir metin hazırla.
                Format tercihi: {format_secimi}
                
                DİKKAT KURALI (EN ÖNEMLİSİ): Kesinlikle yapay zeka gibi konuşma! "Hey millet, şuna bakın", "İşte harika bir video" gibi sahte, pazarlamacı ve robotik ifadeler KULLANMA.
                Sıradan bir Türk internet kullanıcısı ağzıyla yaz. Kadıköy'de bir kafede masadaki arkadaşına izletiyormuşsun gibi dümdüz, sade, samimi ve gerçek bir insan tepkisi ver.
                Eğer format "Tekli Tweet" ise, videoyu izlemeye teşvik eden merak uyandırıcı tek bir cümle kur.
                Eğer format "Bilgi Seli" ise, videodaki olayı gereksiz uzatmadan kısa flood maddeleri halinde anlat.
                Metnin en sonuna, konuya tam uygun (özellikle endüstriyel veya teknikse o alana yönelik) 2 veya 3 adet popüler hashtag ekle.
                Maksimum 1 veya 2 doğal emoji kullan. Sadece X metnini ve hashtagleri ver.
                """
                
                res = client.models.generate_content(
                    model='gemini-2.5-flash', 
                    contents=[video_dosyasi, prompt]
                )
                
                st.success("İşte paylaşmaya hazır, %100 doğal içerik!")
                st.info(res.text.strip())
                
                os.remove(tmp_file_path)
                
            except Exception as e:
                st.error(f"Beklenmeyen bir hata oluştu: {e}")
