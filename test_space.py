import streamlit as st
import pystac_client
import planetary_computer
import stackstac
import matplotlib.pyplot as plt

# ページ設定
st.set_page_config(
    page_title="🔬 Laboratorio Spaziale - NDVI Mappatura",
    page_icon="🛰️",
    layout="wide"
)

st.title("🛰️ Monitoraggio Satellitare via Microsoft Planetary Computer (Sentinel-2)")
st.write("---")

st.subheader("🧪 Area Sperimentale Protetta: Calcolo NDVI")
st.write("Ambiente di test isolato per l'estrazione delle bande spettrali e la mappatura di Bologna.")

# 選択メニュー (Calderara di Reno 特化版)
area_scelta = st.radio(
    "Scegli l'estensione geografica per l'analisi del suolo:",
    [
        "📍 Calderara di Reno (Bologna) - Il Tuo Ground Truth", 
        "🌾 Emilia-Romagna (Carbon Farming Test)"
    ]
)

if st.button("Avvia il recupero ed elaborazione della Mappa NDVI 🚀"):
    with st.spinner("Estrazione delle bande spettrali in corso da Microsoft Azure..."):
        try:
            # 🌐 1. マイクロソフトの公開カタログに接続
            catalog = pystac_client.Client.open(
                "https://microsoft.com",
                modifier=planetary_computer.sign_inplace
            )
            
            # 📍 2. エリアの座標切り替え
            if area_scelta == "📍 Calderara di Reno (Bologna) - Il Tuo Ground Truth":
                bbox = [11.25, 44.53, 11.30, 44.57] # [west, south, east, north]
                st.success("🎯 Calderara di Reno agganciata: Iniziamo a scrutare il suolo.")
            else:
                bbox = [9.20, 43.70, 12.50, 45.00]
                st.info("🌾 Monitoraggio Regionale Emilia-Romagna attivato.")
            
            # 🛰️ 3. 雲が極めて少ない、直近（2026年秋）の最新 Sentinel-2 データを検索 [Temporal Consistency]
            search = catalog.search(
                collections=["sentinel-2-l2a"],
                bbox=bbox,
                datetime="2026-09-01/2026-10-05", 
                query={"eo:cloud_cover": {"lt": 5}} # 雲の割合5%未満
            )
            
            items = list(search.item_collection())
            
            if len(items) > 0:
                latest_item = items[0] # 一番新しい最新の1枚を取得
                
                # 📊 4. stackstacを使って、赤色(B04)と近赤外線(B08)のバンドをメモリに軽量抽出
                data = stackstac.stack(
                    latest_item, 
                    assets=["B04", "B08"], 
                    bbox=bbox, 
                    epsg=4326
                ).squeeze().compute()
                
                # 🧮 5. NDVI（植生指数）の自動計算: (近赤外 - 赤) / (近赤外 + 赤)
                red = data.sel(band="B04").astype("float32")
                nir = data.sel(band="B08").astype("float32")
                ndvi = (nir - red) / (nir + red)
                
                # 🎨 6. Matplotlibを使って、緑色の健康マップをレンダリング！
                st.write("---")
                st.markdown(f"### 🗺️ Mappa NDVI ({str(latest_item.properties['datetime'])[:10]})")
                
                fig, ax = plt.subplots(figsize=(8, 6))
                im = ax.imshow(
                    ndvi, 
                    cmap="RdYlGn", # 赤（不健康・土）〜黄色〜濃い緑（超健康！）のグラデーション
                    vmin=-0.1, 
                    vmax=0.9
                )
                ax.axis("off") # 周りの余計なピクセル目盛りを消す
                
                cbar = fig.colorbar(im, ax=ax, orientation="vertical", shrink=0.8)
                cbar.set_label("Indice NDVI (Salute della Vegetazione)")
                
                st.pyplot(fig)
                
                st.success("🌿 Mappatura completata! I pixel verde scuro indicano una vegetazione vigorosa ad alta attività fotosintetica.")
                st.info(f"☁️ Copertura nuvolosa registrata: {latest_item.properties['eo:cloud_cover']:.2f} %")
            else:
                st.warning("Nessuna immagine recente con poche nuvole trovata per il periodo selezionato.")
                
        except Exception as e:
            st.error(f"Errore durante l'elaborazione NDVI: {e}")
