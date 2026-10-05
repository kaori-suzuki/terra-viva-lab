import streamlit as st
import openeo

# ページ設定
st.set_page_config(
    page_title="🔬 Laboratorio Spaziale - Terra Viva Lab",
    page_icon="🛰️",
    layout="wide"
)

st.title("🛰️ Monitoraggio Satellitare in Tempo Reale (Sentinel-2)")
st.write("---")

st.subheader("🧪 Area Sperimentale Protetta (In corso...)")
st.write("Questo modulo è attivo in ambiente di test per lo sviluppo del framework MRV.")

# 💡 ボタンを押すと、Streamlitの金庫（Secrets）から自動でパスワードを読み込んで宇宙へ接続します！
if st.button("Avvia il recupero dei dati spaziali 🚀"):
    with st.spinner("Connessione con i satelliti ESA in corso..."):
        try:
            # Streamlitの金庫（Secrets）から安全に認証情報を取得
            cdse_user = st.secrets["copernicus"]["user"]
            cdse_pass = st.secrets["copernicus"]["password"]
            
            # 1. 宇宙のサーバーに接続
            connection = openeo.connect("https://copernicus.eu")
            connection.authenticate_basic(username=cdse_user, password=cdse_pass)
            
            # ==========================================
            # 🎯 2. エリアの選択肢を作って、自動で4つの数字（座標）を切り替える
            # ==========================================
            st.write("---")
            st.markdown("#### 📍 Seleziona l'Area di Monitoraggio Spaziale")
            
            area_scelta = st.radio(
                "Scegli l'estensione geografica per il test:",
                ["Bologna (Calderara di Reno) - Area di Test", "Emilia-Romagna (Intera Regione)", "Italia (Copertura Nazionale)"]
            )
            
            # 選んだエリアによって座標を切り替え
            if area_scelta == "Bologna (Calderara di Reno) - Area di Test":
                bbox = {"west": 11.25, "east": 11.30, "south": 44.53, "north": 44.57}
                st.success("📍 Area di Test selezionata: Perfetta per il Ground Truth locale.")
                
            elif area_scelta == "Emilia-Romagna (Intera Regione)":
                bbox = {"west": 9.20, "east": 12.50, "south": 43.70, "north": 45.00}
                st.info("🌾 Monitoraggio Regionale: Ottimo per analizzare il potenziale di Carbon Farming su vasta scala.")
                
            elif area_scelta == "Italia (Copertura Nazionale)":
                bbox = {"west": 6.60, "east": 18.50, "south": 35.40, "north": 47.10}
                st.warning("⚠️ Monitoraggio Nazionale: L'elaborazione richiede maggior tempo di calcolo.")

            st.success(f"✅ Connessione riuscita! Configurazione completata per: {area_scelta}")
            st.info("I satelliti Sentinel-2 sono agganciati e pronti per l'estrazione delle bande NDVI.")
            
        except Exception as e:
            st.error(f"Errore durante la connessione: {e}")
