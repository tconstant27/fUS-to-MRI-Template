import ants
import os

# ---------------------------------------------------------
# 1. CONFIGURATION DES CHEMINS
# ---------------------------------------------------------
base_root = '/home/thomas/DATASET_TEMPLATE_FINAL/'
base_deriv_root = os.path.join(base_root, 'derivatives')

patient = "sub-1867-01"

# 1. L'image qu'on veut déplacer (ton angio brute)
moving_path = os.path.join(base_root, patient, 'ses-02', 'angio', 'sub-R11867.nii')

# 2. L'image de référence (Ton template global)
fixed_path = '/home/thomas/DATASET_TEMPLATE_FINAL/derivatives/template_T2_brain.nii.gz'

# 3. Les matrices moyennes globales
mat_angio_to_t2 = os.path.join(base_deriv_root, 'average_TF1_fus_to_T1.mat')
mat_t2_to_template = os.path.join(base_deriv_root, 'average_T2_to_template_Affine.mat')

# 4. Le fichier de sortie (on le place dans derivatives/.../ses-02/)
output_dir = os.path.join(base_deriv_root, patient, 'ses-02')
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, "sub-R11867_space-template_angio.nii.gz")

# ---------------------------------------------------------
# 2. APPLICATION DES MATRICES
# ---------------------------------------------------------
if not os.path.exists(moving_path):
    print(f"Erreur : L'image angio est introuvable ici : {moving_path}")
elif not os.path.exists(fixed_path):
    print(f"Erreur : Le template de référence est introuvable : {fixed_path}")
elif not os.path.exists(mat_angio_to_t2):
    print(f"Erreur : La matrice Angio -> T1/T2 est introuvable : {mat_angio_to_t2}")
elif not os.path.exists(mat_t2_to_template):
    print(f"Erreur : La matrice T2 -> Template est introuvable : {mat_t2_to_template}")
else:
    print(f"Chargement du template de référence : {os.path.basename(fixed_path)}")
    fixed_img = ants.image_read(fixed_path)
    
    print(f"Chargement de l'image à transformer : {os.path.basename(moving_path)}")
    moving_img = ants.image_read(moving_path)
    
    print("Application des matrices moyennes pour aligner sur le template...")
    
    # ORDRE CRUCIAL : Du Template vers l'Angio
    transform_list = [
        mat_t2_to_template, # 1. La matrice la plus proche du Template
        mat_angio_to_t2     # 2. La matrice la plus proche de l'Angio
    ]
    
    warped_img = ants.apply_transforms(
        fixed=fixed_img,
        moving=moving_img,
        transformlist=transform_list,
        interpolator='linear' # Tu peux tester 'bSpline' si 'linear' floute trop les vaisseaux
    )
    
    # Sauvegarde
    ants.image_write(warped_img, output_path)
    print(f"\nSuccès ! L'angio transformée dans l'espace du template a été sauvegardée ici :")
    print(f"-> {output_path}")