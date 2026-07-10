import ants
import os
import numpy as np

# ---------------------------------------------------------
# 1. CONFIGURATION DES CHEMINS
# ---------------------------------------------------------
base_root = '/home/thomas/DATASET_TEMPLATE_FINAL/'
base_deriv_root = os.path.join(base_root, 'derivatives')

# Fichier de sortie global pour la matrice moyenne
output_mat_path = os.path.join(base_deriv_root, 'average_T2_to_template_Affine.mat')

# ---------------------------------------------------------
# 2. COLLECTE DES MATRICES 
# ---------------------------------------------------------
mat_paths = []

# On parcourt tous les sous-dossiers pour trouver les matrices affines du recalage
for root, dirs, files in os.walk(base_deriv_root):
    for file in files:
        # On cible exactement le suffixe généré par le script ANTs précédent
        if file.endswith("_T2_to_template_0GenericAffine.mat"):
            full_path = os.path.join(root, file)
            mat_paths.append(full_path)

# On trie la liste pour l'ordre d'affichage
mat_paths = sorted(mat_paths)

# ---------------------------------------------------------
# 3. CALCUL DE LA MOYENNE
# ---------------------------------------------------------
if not mat_paths:
    print("\nAucune matrice trouvée. As-tu bien fait tourner le script de recalage avant ?")
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
        all_params.append(tx.parameters)             
        all_fixed_params.append(tx.fixed_parameters) 
        
    # Moyenne mathématique (Numpy) sur l'axe 0
    avg_params = np.mean(all_params, axis=0)
    avg_fixed_params = np.mean(all_fixed_params, axis=0)
    
    # ---------------------------------------------------------
    # 4. CRÉATION ET SAUVEGARDE DE LA MATRICE MOYENNE
    # ---------------------------------------------------------
    # On conserve le format AffineTransform pour absorber la perte d'orthogonalité
    avg_tx = ants.create_ants_transform(transform_type="AffineTransform", dimension=3)
    
    # Application des paramètres moyens calculés
    avg_tx.set_parameters(avg_params)
    avg_tx.set_fixed_parameters(avg_fixed_params)
    
    # Sauvegarde sur le disque
    ants.write_transform(avg_tx, output_mat_path)
    
    print(f"\nSuccès ! Matrice moyenne globale sauvegardée ici :")
    print(f"-> {output_mat_path}")