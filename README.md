# Neurovascular Alignment Pipeline

Ce projet contient une suite de scripts Python et Bash conçus pour le recalage automatique d'images angiographiques (fUS) sur des volumes IRM, puis vers un espace template commun.

## Structure des données (BIDS)

Ce projet adopte une organisation rigoureuse inspirée du standard **BIDS** (Brain Imaging Data Structure). Voici comment les répertoires sont structurés :

*   **`DATASET_TEMPLATE_FINAL/`** : Dossier racine du dataset.
    *   **`sub-<ID>/`** : Dossiers de chaque sujet (ex: `sub-1885-03`).
        *   **`ses-<ID>/`** : Sous-dossiers de session (ex: `ses-01`, `ses-02`).
            *   **`angio/`** : Contient les données d'angiographie brutes (`.nii`).
            *   **`T1/`** : Données T1 FLASH brutes (`.nii.gz` et fichiers `.json` associés).
            *   **`T1_SWI/`** : Données T1 SWI brutes (`.nii.gz` et fichiers `.json` associés).
            *   **`T2/`** : Données T2 TurboRARE brutes (`.nii.gz` et fichiers `.json` associés).
            *   **`ULM/`** : Dossier complémentaire pour les données d'échographie ultra-rapide.
    *   **`derivatives/`** : Dossier contenant les données traitées et les résultats du pipeline.
        *   **`sub-<ID>/ses-<ID>/`** : Contient les outputs spécifiques par sujet/session (masques extraits, images alignées, matrices de recalage `_Warp.nii.gz` et `_Affine.mat`).
        *   **`Racine de derivatives/`** : Contient les fichiers globaux du template et les matrices moyennes calculées :
            *   `template_T2_brain.nii.gz` : Template anatomique de référence.
            *   `average_T2_to_template_Affine.mat` : Matrice moyenne globale IRM vers template.
            *   `average_TF1_fus_to_T1.mat` : Matrice moyenne globale Angio vers IRM.
            *   `average_template_space_angio.nii.gz` : Résultat final du cerveau moyen vasculaire.

## Contenu du projet

Le pipeline est divisé en scripts autonomes pour une meilleure reproductibilité :

1.  **`01_frangi_registration.py`** : Effectue le prétraitement (inversion, filtre de Frangi) sur les IRM et réalise le recalage rigide initial de l'angiographie sur le squelette IRM.
2.  **`02_build_template.py`** : Construit un template anatomique moyen à partir de l'ensemble de la cohorte en utilisant `ants.build_template`.
3.  **`03_evaluate_metrics.py`** : Calcule les performances du recalage via des métriques comme le NMI (Normalized Mutual Information) et le Dice score, avec visualisation (Overlay).
4.  **`04_register_irm_to_template.py`** : Calcule les transformations non-linéaires (`SyN`) entre chaque IRM native et le template global.
5.  **`05_apply_T3_combination.py`** : Combine les transformations pour projeter les angiographies dans l'espace du template en une seule passe.
6.  **`06_compute_average_angio.py`** : Calcule le cerveau moyen vasculaire final dans l'espace du template.
7.  **`preprocess_bids.sh`** : Script Bash pour le *Skull-Stripping* (BET) et le masquage des T1 sur toute l'arborescence.

## 🛠 Prérequis et Bibliothèques

### 1. Environnement Python
Le projet utilise principalement **ANTsPy** pour le traitement d'images.

**Bibliothèques nécessaires :**
* `antspyx`
* `scikit-image`
* `numpy`
* `matplotlib`
* `scipy`

**Installation rapide :**
```bash
pip install antspyx scikit-image numpy matplotlib scipy
