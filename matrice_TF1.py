import ants
import os
import numpy as np

# ---------------------------------------------------------
# 1. CONFIGURATION DES CHEMINS
# ---------------------------------------------------------
base_root = '/home/thomas/DATASET_TEMPLATE_FINAL/'
base_deriv_root = os.path.join(base_root, 'derivatives')

# Fichier de sortie global pour la matrice moyenne
output_mat_path = os.path.join(base_deriv_root, 'average_TF1_fus_to_T1.mat')

# ---------------------------------------------------------
# 2. COLLECTE DES MATRICES (MÉTHODE FORTE)
# ---------------------------------------------------------
mat_paths = []

# On parcourt tous les sous-dossiers de 'derivatives' pour trouver les matrices
for root, dirs, files in os.walk(base_deriv_root):
    for file in files:
        if file.endswith("_TF1_fus_to_T1.mat"):
            full_path = os.path.join(root, file)
            mat_paths.append(full_path)

# On trie la liste pour l'ordre d'affichage (optionnel mais plus propre)
mat_paths = sorted(mat_paths)

# ---------------------------------------------------------
# 3. CALCUL DE LA MOYENNE
# ---------------------------------------------------------
if not mat_paths:
    print("\nAucune matrice trouvée. Vérifie le chemin du dossier derivatives.")
else:
    print(f"\nSuper ! {len(mat_paths)} matrices trouvées :")
    for p in mat_paths:
        print(f" - {os.path.basename(p)}")
        
    print("\nCalcul de la moyenne en cours...")
    
    all_params = []
    all_fixed_params = []
    
    # Lecture de chaque transformation
    for path in mat_paths:
        tx = ants.read_transform(path)
        all_params.append(tx.parameters)             # La matrice 3x3 et le vecteur de translation
        all_fixed_params.append(tx.fixed_parameters) # Le centre de rotation
        
    # Moyenne mathématique (Numpy) sur l'axe 0
    avg_params = np.mean(all_params, axis=0)
    avg_fixed_params = np.mean(all_fixed_params, axis=0)
    
    # ---------------------------------------------------------
    # 4. CRÉATION ET SAUVEGARDE DE LA MATRICE MOYENNE
    # ---------------------------------------------------------
    # On utilise "AffineTransform" car la moyenne mathématique pure de matrices rigides
    # perd sa stricte orthogonalité. ANTs a besoin du format Affine pour l'accepter.
    avg_tx = ants.create_ants_transform(transform_type="AffineTransform", dimension=3)
    
    # Application des paramètres moyens calculés
    avg_tx.set_parameters(avg_params)
    avg_tx.set_fixed_parameters(avg_fixed_params)
    
    # Sauvegarde sur le disque
    ants.write_transform(avg_tx, output_mat_path)
    
    print(f"\nSuccès ! Matrice moyenne globale sauvegardée ici :")
    print(f"-> {output_mat_path}")