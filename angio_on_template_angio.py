import ants
import os

# 1. Chemins
input_path = ''

output_dir = ''

# 2. Génération automatique du nom de sortie
base_name = os.path.basename(input_path)
name_part, ext_part = base_name.split('.', 1) 
# On combine le dossier, le nouveau nom et l'extension
output_path = os.path.join(output_dir, f"{name_part}_on_MRI_space.{ext_part}")

# 3. Charger les images
template_angio = ants.image_read('/home/thomas/DATASET_TEMPLATE_FINAL/derivatives/average_template_space_angio.nii.gz')
nouvelle_angio = ants.image_read(input_path)

# 4. Recalage (SyN)
reg = ants.registration(
    fixed=template_angio,
    moving=nouvelle_angio,
    type_of_transform='SyN'
)

# 5. Application des transformations
angio_dans_espace_irm = ants.apply_transforms(
    fixed=template_angio,
    moving=nouvelle_angio,
    transformlist=reg['fwdtransforms']
)

# 6. Sauvegarde dans le dossier 'derivatives'
ants.image_write(angio_dans_espace_irm, output_path)

print(f"Recalage terminé. Fichier sauvegardé sous : {output_path}")