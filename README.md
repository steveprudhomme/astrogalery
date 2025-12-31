# GNU Astro Galery

**Version : 0.8.0**

GNU Astro Galery est un générateur de galerie astrophotographique statique conçu pour les images produites par le télescope intelligent **Seestar S50**.  
Il analyse automatiquement les répertoires d’images, enrichit les objets astronomiques à l’aide de catalogues et de services open source, puis génère un site Web HTML5 moderne, documenté et pérenne.

---

## ✨ Fonctionnalités principales

- Génération automatique d’une galerie HTML5/CSS3 (Bootstrap)
- Page d’accueil chronologique (du plus récent au plus ancien)
- Pages objet détaillées avec :
  - Image principale
  - Auteur et licence (CC0 1.0)
  - Métadonnées FITS complètes
  - Caractéristiques astronomiques de l’objet
  - Astrométrie (WCS → PNG)
  - Carte stellaire de type atlas
  - **Bloc météo / conditions d’observation**
- Enrichissement automatique des objets via :
  - SIMBAD
  - Catalogue Messier (XLSX)
  - Catalogue objets divers (XLSX multi-feuilles)
- Cache local (astrométrie et météo)
- Sémantique Web (JSON‑LD, OpenGraph)
- Fonctionnement 100 % local (Windows natif)

---

## 🌤️ Bloc météo / conditions d’observation

Pour chaque objet, le script extrait depuis le fichier FITS source :

- DATE-OBS
- SITELAT
- SITELONG

À partir de ces données, le module `space_weather.py` récupère automatiquement :

- Température extérieure (°C)
- Humidité relative (%)
- Pression atmosphérique (hPa)
- Vitesse et direction du vent
- Date et heure UTC

Source : **Open‑Meteo (archive API)**  
Les résultats sont mis en cache localement.

---

## 🗂️ Organisation du projet

```
MyWorks/
├─ generate_gallery.py
├─ space_weather.py
├─ Objets Messiers..xlsx
├─ objetsdivers.xlsx
├─ MyWorks/
└─ site/
```

---

## ⚙️ Prérequis

- Python 3.10+
- Windows 10/11
- Bibliothèques :
  - astropy
  - pandas
  - numpy
  - requests
  - pillow

Installation :
```
pip install astropy pandas numpy requests pillow
```

---

## ▶️ Exécution

```
python generate_gallery.py
```

Un seul script est à lancer.

---

## 📜 Licence

Images : **Creative Commons CC0 1.0**  
Code : **GNU GPL v3**

---

## 👤 Auteur

**Steve Prud’Homme**
