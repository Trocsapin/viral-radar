import streamlit as st
from google import genai
import requests

# --- ARAYÜZ YAPILANDIRMASI ---
st.set_page_config(page_title="Viral İçerik Radarı", page_icon="📡", layout="centered")

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stButton>button {
    width: 100%; 
    border-radius: 8px; 
    font-weight: bold; 
    background-color: #FF4500; 
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("📡 Viral İçerik Radarı")
st.markdown("İnternetin arka sokaklarında son 24 saatte patlamış videoları bulur ve X (Twitter) için tamamen 'insan ağzıyla' doğal metinler yazar.")
st.markdown("---")

# --- API ANAHTARI (GÜVENLİ KASA BAĞLANTISI) ---
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# --- KULLANICI GİRDİSİ ---
st.markdown("#### 1. Ne Tür İçerikler Arıyoruz?")
kategori = st.selectbox(
    "",
    [
        "Mühendislik, Kaynak & Üretim (EngineeringPorn, Welding)",
        "Genel İlginç & Şaşırtıcı (interestingasfuck)",
        "Beklenmedik & Komik (Unexpected)"
    ]
)

st.markdown("---")

if st.button("📡 Radarı Çalıştır ve Viral İçerik Bul"):
    with st.spinner("İnternetin derinlikleri taranıyor... Bu işlem birkaç saniye sürebilir."):
        try:
            # Kategoriye göre subreddit seçimi
            if "Mühendislik" in kategori:
                subreddits = ["Welding", "EngineeringPorn"]
            elif "Beklenmedik" in kategori:
                subreddits = ["Unexpected"]
            else:
                subreddits = ["interestingasfuck"]
            
            # İlk subreddit'i alarak arama yapıyoruz
            secilen_sub = subreddits[0]
            url = f"https://www.reddit.com/r/{secilen_sub}/top.json?t=day&limit=10"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            response = requests.get(url, headers=headers)
            data = response.json()
            
            gonderiler = []
            for post in data['data']['children']:
                # Sadece video veya dışarıya giden medya linki olanları filtrele
                if post['data'].get('is_video') or post['data'].get('domain') not in ['reddit.com', 'self']:
                    baslik = post['data']['title']
                    link = "https://www.reddit.com" + post['data']['permalink']
                    skor = post['data']['score']
                    gonderiler.append({"baslik": baslik, "link": link, "skor": skor})
            
            if not gonderiler:
                st.warning("Şu an bu kategoride son 24 saate ait uygun formatta video bulunamadı. Lütfen başka bir kategori deneyin.")
            else:
                client = genai.Client(api_key=GEMINI_API_KEY)
                
                st.success(f"Radar {len(gonderiler)} adet potansiyel viral içerik tespit etti!")
                
                # Sadece en yüksek puanlı ilk 3 videoyu göster
                for icerik in gonderiler[:3]:
                    st.markdown(f"### 🔥 Skor: {icerik['skor']} Beğeni")
                    st.write(f"**Orijinal Yabancı Başlık:** {icerik['baslik']}")
                    st.write(f"🔗 **Videoyu Görmek ve İndirmek İçin:** [Buraya Tıklayın]({icerik['link']})")
                    
                    prompt_3 = f"""
                    Şu İngilizce Reddit gönderisi başlığına bak: "{icerik['baslik']}"
                    Bu çok izlenen bir video. Bunu X'te (Twitter) paylaşmak için Türkçe bir metin yaz.
                    
                    DİKKAT KURALI (EN ÖNEMLİSİ): Kesinlikle yapay zeka gibi konuşma! "Hey millet, şuna bakın", "İşte harika bir video", "Buna inanamayacaksınız" gibi sahte, pazarlamacı ve robotik ifadeler KULLANMA.
                    Sıradan bir Türk internet kullanıcısı ağzıyla yaz. Kadıköy'de bir kafede arkadaşına izletiyormuşsun gibi dümdüz, sade, samimi, bazen tek kelimelik veya kısa bir cümlelik gerçek bir insan tepkisi ver.
                    Hashtag KULLANMA. Maksimum 1 doğal emoji kullan (abartma).
                    Sadece tweet metnini ver, başka hiçbir açıklama yapma.
                    """
                    
                    res_3 = client.models.generate_content(model='gemini-2.5-flash', contents=[prompt_3])
                    
                    st.info(f"✍️ **X'te Paylaşmak İçin Hazır Tweet:**\n\n{res_3.text.strip()}")
                    st.markdown("---")
        
        except Exception as e:
            st.error(f"Radar çalışırken bir bağlantı engeli oluştu: {e}")