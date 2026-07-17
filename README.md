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

Tous les scripts de ce pipeline utilisent le dossier DATASET_TEMPLATE_FINAL/derivatives/ comme point d'entrée central. Chaque programme est conçu pour parcourir automatiquement cette arborescence afin de sélectionner lui-même les fichiers et matrices nécessaires à son exécution.

### 1. `brain.sh`
Script Bash de prétraitement. Il effectue le *skull-stripping* (extraction du cerveau) sur les images T2 via l'outil FSL `bet` et propage les masques sur les images T1 pour isoler les tissus cérébraux.
*   **Input** : Images T1 et T2 brutes dans l'arborescence BIDS.
*   **Output** : Masques binaires (`_brain_mask.nii.gz`) et images extraites (`_brain_extracted.nii.gz`).

### 2. `Frangi_filter.py`
Prépare les données vasculaires en inversant les contrastes des IRM et en appliquant un filtre de Frangi pour créer un squelette vasculaire. Il réalise ensuite le recalage rigide initial de l'angiographie (fUS) sur ce squelette.
*   **Input** : Angiographies brutes et IRM extraites (`_brain_extracted`).
*   **Output** : Images Frangi (`_desc-frangi.nii.gz`), images inversées et matrices de recalage `_TF1_fus_to_T1.mat`.

### 3. `recalage_angio_to_T2_star.py`
Automatise le processus de recalage rigide pour l'ensemble de la cohorte patient.
*   **Input** : Angiographies et images Frangi traitées.
*   **Output** : Angio recalée (`_registered.nii.gz`) et copie des matrices `.mat`.


### 5. `Template_T2.py`
Construit un template anatomique robuste. Il effectue un recalage rigide de toutes les images sur une référence, puis génère le template final via une approche non-linéaire (`SyN`) itérative.
*   **Input** : Ensemble des fichiers T2 extraits (`*_brain.nii.gz`) dans `derivatives/`.
*   **Output** : `template_T2_brain.nii.gz`.

### 6. `IRM_on_template.py`
Calcule les déformations non-linéaires (`SyN`) entre chaque IRM native et le template anatomique de référence.
*   **Input** : IRM individuelles (T1/T2) et le `template_T2_brain.nii.gz`.
*   **Output** : Images alignées sur le template (`_aligned_to_template.nii.gz`) et fichiers de transformation (`_1Warp.nii.gz`, `_0GenericAffine.mat`).

### 8. `angio_on_template_angio.py`
Réalise le recalage non-linéaire (**SyN**) des images angiographiques fUS natives vers l'espace du template moyen. Cette étape assure la mise en correspondance spatiale des données vasculaires avec le template IRM/fUS de référence, garantissant que toutes les données sont superposables à l'anatomie standardisée.
*   **Input** : Angiographies fUS natives et template moyen `average_template_space_angio.nii.gz`.
*   **Output** : Images angio-fUS recalées (`_on_MRI_space.nii.gz`) sauvegardées dans le répertoire `derivatives`.

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


Add paramètres séquences, protocoles détaillés etc
conseils visualisations, logiciel itk snap
