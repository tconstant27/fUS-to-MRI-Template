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

Chaque script a un rôle spécifique dans le pipeline de traitement des données neurovasculaires.

### 1. `brain.sh`
*   **Description** : Script Bash de prétraitement. Il effectue le *skull-stripping* (extraction du cerveau) sur les images T2 via l'outil FSL `bet` et propage les masques sur les images T1 pour isoler les tissus cérébraux.
*   **Input** : Images T1 et T2 brutes dans l'arborescence BIDS.
*   **Output** : Masques binaires (`_brain_mask.nii.gz`) et images extraites (`_brain_extracted.nii.gz`).

### 2. `Frangi_filter.py`
*   **Description** : Prépare les données vasculaires en inversant les contrastes des IRM et en appliquant un filtre de Frangi pour créer un squelette vasculaire. Il réalise ensuite le recalage rigide initial de l'angiographie (fUS) sur ce squelette.
*   **Input** : Angiographies brutes et IRM extraites (`_brain_extracted`).
*   **Output** : Images Frangi (`_desc-frangi.nii.gz`), images inversées et matrices de recalage `_TF1_fus_to_T1.mat`.

### 3. `recalage_angio_to_T2_star.py`
*   **Description** : Automatise le processus de recalage rigide pour l'ensemble de la cohorte patient.
*   **Input** : Angiographies et images Frangi traitées.
*   **Output** : Angio recalée (`_registered.nii.gz`) et copie des matrices `.mat`.

### 4. `matrice_TF1.py`
*   **Description** : Calcule la moyenne mathématique des matrices affines (Angio $\rightarrow$ IRM) sur l'ensemble de la cohorte pour obtenir une transformation globale robuste.
*   **Input** : Tous les fichiers `_TF1_fus_to_T1.mat`.
*   **Output** : `average_TF1_fus_to_T1.mat`.

### 5. `IRM_on_template.py`
*   **Description** : Calcule les déformations non-linéaires (`SyN`) entre chaque IRM native et le template anatomique de référence.
*   **Input** : IRM individuelles (T1/T2) et le `template_T2_brain.nii.gz`.
*   **Output** : Images alignées sur le template (`_aligned_to_template.nii.gz`) et fichiers de transformation (`_1Warp.nii.gz`, `_0GenericAffine.mat`).

### 6. `matrice_TF2.py`
*   **Description** : Calcule la matrice affine moyenne (IRM $\rightarrow$ Template) sur toute la cohorte.
*   **Input** : Tous les fichiers `_T2_to_template_0GenericAffine.mat`.
*   **Output** : `average_T2_to_template_Affine.mat`.

### 7. `apply_TF1_TF2.py`
*   **Description** : Projette une angiographie spécifique dans l'espace template en combinant les transformations moyennes calculées précédemment (Angio $\rightarrow$ IRM puis IRM $\rightarrow$ Template) en une seule passe.
*   **Input** : Angio native, `average_TF1_fus_to_T1.mat`, `average_T2_to_template_Affine.mat`.
*   **Output** : Angio projetée dans l'espace template (`_space-template_angio.nii.gz`).
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
