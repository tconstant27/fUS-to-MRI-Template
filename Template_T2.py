import os
import glob
import ants

# ---------------------------------------------------------
# 1. Configuration des chemins
# ---------------------------------------------------------
base_dir = "/home/thomas/DATASET_TEMPLATE_FINAL/derivatives"

chemin_recherche = os.path.join(base_dir, "**", "T2", "*_brain.nii.gz")
fichiers_bruts = glob.glob(chemin_recherche, recursive=True)

# On filtre les masques et on trie par ordre alphabétique pour être reproductible
fichiers = sorted([f for f in fichiers_bruts if "mask" not in f.lower()])

# ---------------------------------------------------------
# 2. Vérification
# ---------------------------------------------------------
if not fichiers:
    print(f"Erreur : Aucun fichier trouvé avec la recherche récursive dans '{base_dir}'.")
else:
    print(f"{len(fichiers)} images trouvées pour le template.")
    print(f"L'image de référence choisie (la première) est : {os.path.basename(fichiers[0])}")
    
    # ---------------------------------------------------------
    # 3. Pré-alignement Rigide sur la première image
    # ---------------------------------------------------------
    print("\nChargement et pré-alignement rigide des images...")
    
    # On charge la toute première image qui servira de référence
    img_ref = ants.image_read(fichiers[0])
    
    # On initialise la liste avec cette première image (qui est déjà bien placée par définition)
    img_list_aligned = [img_ref]

    # On boucle sur le reste des fichiers (de l'index 1 jusqu'à la fin)
    for f in fichiers[1:]:
        print(f" - Alignement de {os.path.basename(f)}...")
        img_moving = ants.image_read(f)
        
        # Recalage rigide (Translation + Rotation) vers la première image
        reg = ants.registration(
            fixed=img_ref,
            moving=img_moving,
            type_of_transform='Rigid'
        )
        
        # On ajoute l'image recalée à la liste
        img_list_aligned.append(reg['warpedmovout'])

    # ---------------------------------------------------------
    # 4. Création du Template
    # ---------------------------------------------------------
    print("\nCréation du template 3D (Cette étape prend beaucoup de temps)...")
    
    template_3d = ants.build_template(
        image_list=img_list_aligned,
        iterations=6,
        type_of_transform='SyN',
        syn_metric='CC',
        syn_sampling=3,
        reg_iterations=(100, 100, 70, 30),
        gradient_step=0.1
    )

    # ---------------------------------------------------------
    # 5. Sauvegarde
    # ---------------------------------------------------------
    chemin_sauvegarde = os.path.join(base_dir, "template_T2_brain.nii.gz")
    os.makedirs(os.path.dirname(chemin_sauvegarde), exist_ok=True)
    
    ants.image_write(template_3d, chemin_sauvegarde)
    print(f"\nTemplate sauvegardé avec succès dans : {chemin_sauvegarde}")