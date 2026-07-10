import ants
import os
import gc
import shutil  # <-- Nouvel import pour copier la matrice

# ---------------------------------------------------------
# 1. CONFIGURATION DES CHEMINS
# ---------------------------------------------------------
base_root = '/home/thomas/DATASET_TEMPLATE_FINAL/'
base_deriv_root = os.path.join(base_root, 'derivatives')

# ---------------------------------------------------------
# 2. BOUCLE DE TRAITEMENT (RECALAGE)
# ---------------------------------------------------------
# On liste les patients à la racine du dataset (en excluant le dossier derivatives)
patients = [d for d in os.listdir(base_root) if os.path.isdir(os.path.join(base_root, d)) and d != 'derivatives']

for patient in sorted(patients):
    print(f"\n--- Recalage pour le patient : {patient} ---")
    
    # -----------------------------------------------------
    # A. Récupération de l'image MOBILE (Angio fUS)
    # -----------------------------------------------------
    patient_dir = os.path.join(base_root, patient)
    moving_path = None
    
    for root, dirs, files in os.walk(patient_dir):
        for file in files:
            # On cherche "angio" soit dans le nom du fichier, soit dans le nom du dossier
            if ("angio" in file.lower() or "angio" in os.path.basename(root).lower()) and file.endswith(('.nii', '.nii.gz')):
                moving_path = os.path.join(root, file)
                break
        if moving_path:
            break
            
    if not moving_path:
        print(f"Fichier Angio brut introuvable pour {patient} dans {patient_dir}. Passage au suivant.")
        continue

    # -----------------------------------------------------
    # B. Récupération de l'image FIXE (Frangi)
    # -----------------------------------------------------
    patient_deriv_dir = os.path.join(base_deriv_root, patient)
    fixed_path = None
    
    if os.path.exists(patient_deriv_dir):
        for root, dirs, files in os.walk(patient_deriv_dir):
            for file in files:
                if "frangi" in file.lower() and file.endswith(('.nii', '.nii.gz')):
                    fixed_path = os.path.join(root, file)
                    break
            if fixed_path:
                break
                
    if not fixed_path:
        print(f"Image Frangi introuvable pour {patient} dans derivatives. Passage au suivant.")
        continue
        
    # -----------------------------------------------------
    # C. Exécution du recalage ANTs
    # -----------------------------------------------------
    try:
        print(f"Chargement FIXE (Frangi) : {os.path.basename(fixed_path)}")
        print(f"Chargement MOBILE (Angio) : {os.path.basename(moving_path)}")
        
        fixed_vessels = ants.image_read(fixed_path)
        moving_angio = ants.image_read(moving_path)
        
        print("Lancement du recalage rigide...")
        mytx = ants.registration(
            fixed=fixed_vessels,
            moving=moving_angio,
            type_of_transform='Rigid',
            iterations=(2000, 2000, 2000), 
            metric='mattes',
            grad_step=0.05
        )
        
        # -----------------------------------------------------
        # D. Sauvegarde du résultat et de la matrice
        # -----------------------------------------------------
        # S'assurer que le dossier derivatives/patient existe bien
        os.makedirs(patient_deriv_dir, exist_ok=True)
        
        # 1. Sauvegarde de l'image recalée
        save_img_path = os.path.join(patient_deriv_dir, f"{patient}_angio_registered.nii.gz")
        ants.image_write(mytx['warpedmovout'], save_img_path)
        print(f"Succès ! Angio recalée sauvegardée ici : {save_img_path}")
        
        # 2. Sauvegarde de la matrice de transformation
        # 'fwdtransforms' contient une liste des transformations appliquées (ici une seule matrice .mat pour du rigide)
        transform_files = mytx['fwdtransforms']
        if transform_files and len(transform_files) > 0:
            temp_mat_path = transform_files[0]
            save_mat_path = os.path.join(patient_deriv_dir, f"{patient}_TF1_fus_to_T1.mat")
            
            shutil.copy(temp_mat_path, save_mat_path)
            print(f"Matrice de transformation sauvegardée ici : {save_mat_path}")
        
        # Nettoyage mémoire
        del fixed_vessels, moving_angio, mytx
        gc.collect()
        
    except Exception as e:
        print(f"Échec du recalage pour le patient {patient} : {e}")

print("\nRecalage global terminé.")