import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Fullscreen, MeasureControl, Draw
import pandas as pd
import plotly.express as px

# --- 1. CONFIGURATION & STYLE CSS TYPE "GIS DASHBOARD" ---
st.set_page_config(page_title="méchackpro03 Africa Data | GIS", layout="wide", page_icon="🌍")

st.markdown("""
    <style>
    /* Fond global sombre et typographie moderne */
    .stApp {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    
    /* Animation pour les zones sélectionnées */
    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.8; stroke-width: 2; }
        50% { transform: scale(1.5); opacity: 0.4; stroke-width: 10; }
        100% { transform: scale(1); opacity: 0.8; stroke-width: 2; }
    }
    .blink {
        animation: pulse 1.5s infinite;
    }
    
    /* Style de la barre latérale ArcGIS Style */
    section[data-testid="stSidebar"] {
        background-color: #262626;
        border-right: 1px solid #404040;
    }

    /* Conteneur de la carte avec bordure lumineuse */
    .map-container {
        border: 2px solid #3b82f6;
        border-radius: 10px;
        overflow: hidden;
    }

    /* KPIs flottants */
    .css-1r6slb0 {
        background-color: #333333;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #4facfe;
    }
    
    .main-title {
        font-size: 28px;
        font-weight: 700;
        color: #4facfe;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 20px;
        border-bottom: 2px solid #4facfe;
        padding-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)


# --- 2. GESTION DES DONNÉES (COMPLET : 54 PAYS) ---
if 'df_africa' not in st.session_state:
    data = {
        "Pays": [
            "Algérie", "Angola", "Bénin", "Botswana", "Burkina Faso", "Burundi", "Cabo Verde", "Cameroun", 
            "Centrafrique", "Tchad", "Comores", "Congo-Brazzaville", "Congo-Kinshasa (RDC)", "Côte d'Ivoire", 
            "Djibouti", "Égypte", "Guinée Équatoriale", "Érythrée", "Eswatini", "Éthiopie", "Gabon", "Gambie", 
            "Ghana", "Guinée", "Guinée-Bissau", "Kenya", "Lesotho", "Libéria", "Libye", "Madagascar", 
            "Malawi", "Mali", "Mauritanie", "Maurice", "Maroc", "Mozambique", "Namibie", "Niger", 
            "Nigeria", "Rwanda", "Sao Tomé-et-Principe", "Sénégal", "Seychelles", "Sierra Leone", 
            "Somalie", "Afrique du Sud", "Soudan du Sud", "Soudan", "Tanzanie", "Togo", "Tunisie", 
            "Ouganda", "Zambie", "Zimbabwe"
        ],
        "Capitale": [
            "Alger", "Luanda", "Porto-Novo", "Gaborone", "Ouagadougou", "Gitega", "Praia", "Yaoundé", 
            "Bangui", "N'Djamena", "Moroni", "Brazzaville", "Kinshasa", "Yamoussoukro", 
            "Djibouti", "Le Caire", "Malabo", "Asmara", "Mbabane", "Addis-Abeba", "Libreville", "Banjul", 
            "Accra", "Conakry", "Bissau", "Nairobi", "Maseru", "Monrovia", "Tripoli", "Antananarivo", 
            "Lilongwe", "Bamako", "Nouakchott", "Port-Louis", "Rabat", "Maputo", "Windhoek", "Niamey", 
            "Abuja", "Kigali", "Sao Tomé", "Dakar", "Victoria", "Freetown", 
            "Mogadiscio", "Pretoria", "Juba", "Khartoum", "Dodoma", "Lomé", "Tunis", 
            "Kampala", "Lusaka", "Harare"
        ],
        "Population_M": [
            45.0, 34.5, 13.0, 2.6, 22.1, 12.6, 0.6, 28.0, 5.5, 17.2, 0.9, 6.1, 99.0, 28.1, 
            1.1, 111.0, 1.6, 3.6, 1.2, 123.0, 2.4, 2.6, 33.0, 13.9, 2.1, 54.0, 2.3, 5.3, 6.8, 29.6, 
            20.4, 22.6, 4.9, 1.3, 37.5, 33.0, 2.6, 26.0, 218.5, 13.8, 0.2, 17.3, 0.1, 8.6, 
            17.6, 60.0, 11.0, 46.0, 65.5, 8.8, 12.4, 47.0, 20.0, 16.0
        ],
        "PIB_Mds": [
            191.9, 106.7, 17.1, 17.6, 18.8, 3.3, 2.3, 45.3, 2.5, 12.7, 1.2, 14.4, 58.4, 70.1, 
            3.5, 476.7, 11.8, 2.0, 4.8, 126.8, 21.0, 2.2, 72.8, 21.2, 1.6, 113.4, 2.5, 4.0, 67.3, 14.9, 
            13.1, 18.8, 10.3, 12.9, 142.9, 17.8, 12.6, 13.9, 477.4, 13.3, 0.5, 27.6, 1.6, 4.1, 
            8.1, 405.9, 12.0, 34.3, 75.7, 8.1, 46.6, 45.5, 29.7, 20.6
        ],
        "Lat": [
            28.03, -11.20, 9.30, -22.32, 12.23, -3.37, 16.00, 3.84, 6.61, 15.45, -11.64, -4.26, -4.03, 7.53, 
            11.82, 26.82, 1.65, 15.17, -26.52, 9.14, -0.80, 13.44, 7.94, 9.94, 11.80, -1.28, -29.60, 6.42, 26.33, -18.76, 
            -13.25, 17.57, 21.00, -20.34, 31.79, -18.66, -22.95, 17.60, 9.08, -1.94, 0.18, 14.49, -4.67, 8.46, 
            5.15, -30.55, 6.87, 12.86, -6.36, 8.61, 33.88, 1.37, -13.13, -19.01
        ],
        "Lon": [
            1.65, 17.87, 2.31, 24.68, -1.56, 29.91, -24.01, 11.50, 20.42, 18.73, 43.33, 15.28, 21.75, -5.54, 
            42.59, 30.80, 10.26, 39.78, 31.46, 40.48, 11.60, -15.31, -1.02, -9.69, -15.18, 36.82, 28.23, -9.42, 17.22, 46.86, 
            34.30, -3.99, -10.94, 57.55, -7.09, 35.52, 18.49, 8.08, 8.67, 30.06, 6.73, -14.45, 55.49, -11.77, 
            46.19, 22.93, 31.30, 30.21, 34.88, 0.82, 9.53, 32.29, 27.84, 29.15
        ]
    }
    st.session_state.df_africa = pd.DataFrame(data)
    st.session_state.df_africa = pd.DataFrame(data)

# --- 3. SIDEBAR (PANNEAU DE CONTRÔLE ARCGIS) ---
with st.sidebar:
    st.markdown('<p style="font-size: 20px; font-weight: bold; color: #4facfe;">🛠️ ArcGIS Layers</p>', unsafe_allow_html=True)
    
    # Sélecteur de fonds de carte professionnels
    basemap_options = {
        "Sombre (CartoDB)": "CartoDB dark_matter",
        "Satellite (Esri)": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "Topographique": "OpenStreetMap"
    }
    theme_choice = st.selectbox("Fond de carte", list(basemap_options.keys()))
    
    st.markdown("---")
    st.subheader("📊 Filtres & Animations")
    show_labels = st.checkbox("Afficher les étiquettes", value=True)
    
    # Nouvelle option pour les animations dynamiques
    animated_zones = st.multiselect("Zones avec animation (Pulse)", st.session_state.df_africa["Pays"].tolist())
    
    min_pib = st.slider("Filtrer par PIB (Mds $)", 0, 500, 0)
    
    st.markdown("---")
    st.subheader("📂 Données")
    edited_df = st.data_editor(st.session_state.df_africa, num_rows="dynamic")
    st.session_state.df_africa = edited_df

# Filtrage dynamique
filtered_df = edited_df[edited_df['PIB_Mds'] >= min_pib]

# --- 4. INTERFACE PRINCIPALE (DASHBOARD) ---
st.markdown('<p class="main-title">🌍 méchackpro03 Africa Data</p>', unsafe_allow_html=True)

# Ligne supérieure : Statistiques rapides (KPIs)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Pays affichés", len(filtered_df))
m2.metric("Population Totale", f"{filtered_df['Population_M'].sum():.1f} M")
m3.metric("PIB Total", f"{filtered_df['PIB_Mds'].sum():.1f} Mds $")
m4.metric("Moyenne PIB", f"{filtered_df['PIB_Mds'].mean():.1f} Mds $")

st.markdown("<br>", unsafe_allow_html=True)

# Corps principal : Carte et Graphique
col_map, col_stats = st.columns([2, 1])

with col_map:
    st.markdown("##### 📍 Visionneuse Spatiale")
    
    # Logique pour le fond de carte
    attr = "Esri" if "Satellite" in theme_choice else None
    tiles = basemap_options[theme_choice]
    
    m = folium.Map(location=[2.0, 16.0], zoom_start=3, tiles=tiles, attr=attr)
    
    # Ajout d'outils ArcGIS-like
    Fullscreen().add_to(m)
    MeasureControl(primary_length_unit='kilometers').add_to(m)
    Draw(export=True).add_to(m)

    # Ajout des données sur la carte
    for _, row in filtered_df.iterrows():
        # Taille du cercle proportionnelle au PIB
        radius = row['PIB_Mds'] / 10 if row['PIB_Mds'] > 50 else 5
        
        # Vérification de l'animation
        className = "blink" if row['Pays'] in animated_zones else ""
        
        folium.CircleMarker(
            location=[row['Lat'], row['Lon']],
            radius=radius,
            color="#ff4b4b" if className == "blink" else "#4facfe",
            fill=True,
            fill_color="#ff4b4b" if className == "blink" else "#00f2fe",
            fill_opacity=0.6,
            className=className,
            tooltip=f"<b>{row['Pays']}</b><br>PIB: {row['PIB_Mds']} Mds $"
        ).add_to(m)
        
        if show_labels:
            folium.Marker(
                [row['Lat'], row['Lon']],
                icon=folium.DivIcon(html=f"""<div style="font-family: sans-serif; color: white; font-weight: bold; font-size: 10pt; text-shadow: 1px 1px #000;">{row['Pays']}</div>""")
            ).add_to(m)

    st_folium(m, width="100%", height=550)

with col_stats:
    st.markdown("##### 📈 Analyse Comparative")
    
    # Graphique de répartition du PIB
    fig_pib = px.bar(
        filtered_df.sort_values("PIB_Mds"), 
        x="PIB_Mds", 
        y="Pays", 
        orientation='h',
        color="PIB_Mds",
        color_continuous_scale="Blues",
        template="plotly_dark"
    )
    fig_pib.update_layout(margin=dict(l=0, r=0, t=20, b=0), height=250)
    st.plotly_chart(fig_pib, use_container_width=True)
    
    # Graphique de Population
    fig_pop = px.scatter(
        filtered_df,
        x="Population_M",
        y="PIB_Mds",
        size="PIB_Mds",
        color="Pays",
        hover_name="Pays",
        template="plotly_dark"
    )
    fig_pop.update_layout(margin=dict(l=0, r=0, t=20, b=0), height=250)
    st.plotly_chart(fig_pop, use_container_width=True)

st.info("💡 Conseil : Utilisez les outils à gauche de la carte pour mesurer des distances ou dessiner des zones d'intérêt.")