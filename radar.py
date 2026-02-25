import streamlit as st
from google import genai

# --- ARAYÜZ YAPILANDIRMASI ---
st.set_page_config(page_title="Viral İçerik Motoru", page_icon="✍️", layout="centered")

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

st.title("✍️ YouTube & IG -> X İçerik Motoru")
st.markdown("YouTube veya Instagram'da gördüğünüz ilginç bir videonun konusunu yazın, yapay zeka onu X'te (Twitter) en çok etkileşim alacak 'doğal insan' ağzıyla anında tweete çevirsin.")
st.markdown("---")

# --- API ANAHTARI ---
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# --- KULLANICI GİRDİSİ ---
st.markdown("#### Ne İzlediniz?")
video_linki = st.text_input("🔗 İsteğe Bağlı: Videonun Linki (YouTube veya Instagram):", placeholder="https://youtube.com/...")

video_ozeti = st.text_area(
    "📝 Videonun olayı ne? (Kısaca kendi kelimelerinizle yazın):", 
    height=120,
    placeholder="Örn: Adamlar su altında boru kaynağı yapıyor, basınçtan dolayı çok tehlikeli bir yöntemmiş ama harika görünüyor."
)

format_secimi = st.radio(
    "Nasıl bir X gönderisi istiyorsunuz?",
    ["Tekli Vurucu Tweet (Kısa ve öz)", "Bilgi Seli / Flood (Detaylı, 3-4 tweetlik zincir)"]
)

st.markdown("---")

if st.button("🚀 X İçin Doğal Metne Çevir"):
    if not video_ozeti:
        st.warning("Lütfen videonun içeriğini kısaca anlatan birkaç kelime yazın ki yapay zeka neyi çevireceğini bilsin.")
    else:
        with st.spinner("İnsansı tweet yazılıyor..."):
            try:
                client = genai.Client(api_key=GEMINI_API_KEY)
                
                prompt = f"""
                GÖREV: Kullanıcı YouTube veya Instagram'da şöyle bir video izledi: "{video_ozeti}"
                {f"Videonun linki de şu: {video_linki}" if video_linki else ""}
                
                Bu içeriği X'te (Twitter) paylaşmak için Türkçe bir metin hazırla.
                Format tercihi: {format_secimi}
                
                DİKKAT KURALI (EN ÖNEMLİSİ): Kesinlikle yapay zeka gibi konuşma! "Hey millet, şuna bakın", "İşte harika bir video", "Buna inanamayacaksınız", "Sizce de öyle değil mi?" gibi sahte, pazarlamacı ve robotik ifadeler KULLANMA.
                Sıradan bir Türk internet kullanıcısı ağzıyla yaz. Kadıköy'de bir kafede masadaki arkadaşına bir şey anlatıyormuşsun gibi dümdüz, sade, samimi ve gerçek bir insan tepkisi ver.
                Eğer format "Tekli Tweet" ise, videoyu izlemeye teşvik eden merak uyandırıcı tek bir cümle kur.
                Eğer format "Bilgi Seli" ise, konuyu gereksiz uzatmadan, okuması keyifli kısa flood maddeleri halinde yaz.
                Hashtag KULLANMA. Maksimum 1-2 doğal emoji kullan.
                Sadece X metnini ver, "İşte metniniz" gibi giriş cümleleri yazma.
                """
                
                res = client.models.generate_content(model='gemini-2.5-flash', contents=[prompt])
                
                st.success("İşte paylaşmaya hazır, doğal içerik!")
                st.info(res.text.strip())
                
                if video_linki:
                    st.markdown(f"*(Tweeti atarken bu linki eklemeyi unutmayın: {video_linki} )*")
                    
            except Exception as e:
                st.error(f"Beklenmeyen bir hata oluştu: {e}")
