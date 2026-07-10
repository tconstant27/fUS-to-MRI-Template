import ants
import os
import gc
import numpy as np
from skimage.filters import frangi

# ---------------------------------------------------------
# 1. CONFIGURATION DES CHEMINS
# ---------------------------------------------------------
base_deriv_root = '/home/thomas/DATASET_TEMPLATE_FINAL/derivatives/'

# ---------------------------------------------------------
# 2. BOUCLE DE TRAITEMENT
# ---------------------------------------------------------
# On itère directement sur les dossiers patients présents dans 'derivatives'
patients = [d for d in os.listdir(base_deriv_root) if os.path.isdir(os.path.join(base_deriv_root, d))]

for patient in sorted(patients):
    print(f"\n--- Traitement du patient : {patient} ---")
    
    patient_deriv_dir = os.path.join(base_deriv_root, patient)
    
    # Recherche du fichier T1 + SWI + brain_extracted (insensible à la casse et au séparateur)
    target_path = None
    for root, dirs, files in os.walk(patient_deriv_dir):
        for file in files:
            # On met le nom de fichier en minuscules pour s'affranchir des problèmes de casse (SWI vs SWi)
            f_lower = file.lower()
            if "t1" in f_lower and "swi" in f_lower and "brain_extracted" in f_lower and file.endswith(('.nii', '.nii.gz')):
                target_path = os.path.join(root, file)
                break
        if target_path:
            break
            
    if not target_path:
        print(f"Fichier T1*SWI brain_extracted introuvable pour {patient}. Passage au suivant.")
        continue
        
    try:
        print(f"Chargement de : {os.path.basename(target_path)}")
        img = ants.image_read(target_path)
        
        # --- ÉTAPE 1 : EXTRACTION DES VAISSEAUX (Filtre de Frangi) ---
        print("Extraction du réseau vasculaire (Filtre de Frangi)...")
        
        # Inversion de l'IRM (pour que les vaisseaux sombres du SWI deviennent blancs)
        img_inv_numpy = (img.max() - img).numpy()
        img_inverted = img.new_image_like(img_inv_numpy)
        
        # Application du filtre de Frangi
        vessels_numpy = frangi(img_inv_numpy, sigmas=range(1, 4), black_ridges=False)
        vessels_img = img.new_image_like(vessels_numpy)
        
        # --- SAUVEGARDE DES DÉRIVÉS ---
        # On peut garder un nom standardisé pour les fichiers de sortie
        save_inv_path = os.path.join(patient_deriv_dir, f"{patient}_T1_SWI_desc-inverted.nii.gz")
        save_frangi_path = os.path.join(patient_deriv_dir, f"{patient}_T1_SWI_desc-frangi.nii.gz")
        
        ants.image_write(img_inverted, save_inv_path)
        ants.image_write(vessels_img, save_frangi_path)
        print(f"Succès ! Sauvegardé sous : {save_frangi_path}")
        
        # --- NETTOYAGE MÉMOIRE ---
        del img, img_inv_numpy, img_inverted
        del vessels_numpy, vessels_img
        gc.collect()
        
    except Exception as e:
        print(f"Échec pour le patient {patient} : {e}")

print("\nTraitement global terminé.")