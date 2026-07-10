import os
import ants

# ---------------------------------------------------------
# 1. CONFIGURATION DES CHEMINS
# ---------------------------------------------------------
base_deriv_root = '/home/thomas/DATASET_TEMPLATE_FINAL/derivatives/'
template_path = '/home/thomas/DATASET_TEMPLATE_FINAL/derivatives/template_T2_brain.nii.gz'

print("==================================================")
print(f"[TEMPLATE UTILISÉ] : {template_path}")
print("==================================================\n")

print("Chargement du template T2 en mémoire...")
template = ants.image_read(template_path)

# ---------------------------------------------------------
# 2. BOUCLE DE TRAITEMENT
# ---------------------------------------------------------
patients = [d for d in os.listdir(base_deriv_root) if os.path.isdir(os.path.join(base_deriv_root, d))]

for patient in sorted(patients):
    print(f"\n--------------------------------------------------")
    print(f"--- Traitement du patient : {patient}")
    print(f"--------------------------------------------------")
    
    patient_deriv_dir = os.path.join(base_deriv_root, patient)
    
    t1_target_path = None
    t2_target_path = None
    
    # === RECHERCHE DES FICHIERS (AVEC EXCLUSIONS STRICTES) ===
    for root, dirs, files in os.walk(patient_deriv_dir):
        for file in files:
            f_lower = file.lower()
            
            # Filtres communs pour exclure les masques et les cartes quantitatives
            is_valid_nifti = file.endswith(('.nii', '.nii.gz'))
            is_excluded = "mask" in f_lower or "map" in f_lower
            
            if is_valid_nifti and not is_excluded:
                
                # Détection T1 SWI
                if "t1" in f_lower and "swi" in f_lower and "brain_extracted" in f_lower:
                    t1_target_path = os.path.join(root, file)
                    
                # Détection T2
                elif "t2" in f_lower and "brain" in f_lower:
                    if file != 'template_T2_brain.nii.gz': 
                        t2_target_path = os.path.join(root, file)
                
    # === RESUME DES FICHIERS TROUVÉS ===
    if t1_target_path or t2_target_path:
        print("Recherche terminée. Fichiers identifiés pour ce patient :")
        if t1_target_path:
            print(f"  -> [TROUVÉ] T1 SWI : {t1_target_path}")
        if t2_target_path:
            print(f"  -> [TROUVÉ] T2     : {t2_target_path}")
    else:
        print("  -> Aucun fichier T1 SWI ou T2 correspondant n'a été trouvé.")
        
    # === EXECUTION DU RECALAGE ===
    
    # 1. Traitement du T1 SWI
    if t1_target_path:
        print(f"\n[ÉTAPE 1] Recalage (SyN) du T1 SWI sur le template en cours...")
        moving_t1 = ants.image_read(t1_target_path)
        t1_out_prefix = os.path.join(patient_deriv_dir, f"{patient}_T1_SWI_to_template_")
        
        reg_t1 = ants.registration(
            fixed=template, 
            moving=moving_t1, 
            type_of_transform='SyN',
            outprefix=t1_out_prefix
        )
        
        aligned_t1_path = os.path.join(patient_deriv_dir, f"{patient}_T1_SWI_aligned_to_template.nii.gz")
        ants.image_write(reg_t1['warpedmovout'], aligned_t1_path)
        print(f"  -> [SUCCÈS] Image alignée sauvegardée : {aligned_t1_path}")
        print(f"  -> [SUCCÈS] Matrices T1 sauvegardées sous : {t1_out_prefix}")

    # 2. Traitement du T2 individuel
    if t2_target_path:
        print(f"\n[ÉTAPE 2] Recalage (SyN) du T2 sur le template en cours...")
        moving_t2 = ants.image_read(t2_target_path)
        t2_out_prefix = os.path.join(patient_deriv_dir, f"{patient}_T2_to_template_")
        
        reg_t2 = ants.registration(
            fixed=template, 
            moving=moving_t2, 
            type_of_transform='SyN',
            outprefix=t2_out_prefix
        )
        
        aligned_t2_path = os.path.join(patient_deriv_dir, f"{patient}_T2_aligned_to_template.nii.gz")
        ants.image_write(reg_t2['warpedmovout'], aligned_t2_path)
        print(f"  -> [SUCCÈS] Image alignée sauvegardée : {aligned_t2_path}")
        print(f"  -> [SUCCÈS] Matrices T2 sauvegardées sous : {t2_out_prefix}")

print("\n==================================================")
print("Fin du traitement pour tous les patients.")
print("==================================================")