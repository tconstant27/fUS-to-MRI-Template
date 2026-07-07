#!/bin/bash

# Force le format numérique standard
export LC_ALL=C

# --- Chemins ---
BASE_DIR="/home/thomas/DATASET_TEMPLATE_FINAL"
DERIVATIVES_DIR="$BASE_DIR/derivatives"

echo "Début du traitement (BIDS - Préservation voxels et masquage T1)..."

for SUB_DIR in "$BASE_DIR"/sub-*; do
    [ -d "$SUB_DIR" ] || continue
    SUB_ID=$(basename "$SUB_DIR")
    
    for SESS_DIR in "$SUB_DIR"/ses-*; do
        [ -d "$SESS_DIR" ] || continue
        SESS_ID=$(basename "$SESS_DIR")

        # --- 1. Traitement T2 : Extraction Cerveau ---
        if [ -d "$SESS_DIR/T2" ]; then
            OUTPUT_T2_DIR="$DERIVATIVES_DIR/$SUB_ID/$SESS_ID/T2"
            mkdir -p "$OUTPUT_T2_DIR"
            
            for INPUT_T2 in "$SESS_DIR"/T2/*.nii.gz; do
                [ -f "$INPUT_T2" ] || continue
                T2_BASE=$(basename "$INPUT_T2" .nii.gz)
                
                # Copie temporaire pour BET (pour conserver l'original intact)
                cp "$INPUT_T2" "$OUTPUT_T2_DIR/${T2_BASE}_for_bet.nii.gz"
                
                # Astuce rat : Mise à l'échelle temporaire pour BET
                fslchpixdim "$OUTPUT_T2_DIR/${T2_BASE}_for_bet.nii.gz" 0.5 0.5 0.5
                
                # Extraction
                bet "$OUTPUT_T2_DIR/${T2_BASE}_for_bet.nii.gz" "$OUTPUT_T2_DIR/${T2_BASE}_brain" -f 0.5 -m
                
                # RE-COPIE DE LA GÉOMÉTRIE ORIGINALE
                # Réinjecte l'orientation et les dimensions originales dans les fichiers de sortie
                fslcpgeom "$INPUT_T2" "$OUTPUT_T2_DIR/${T2_BASE}_brain.nii.gz"
                fslcpgeom "$INPUT_T2" "$OUTPUT_T2_DIR/${T2_BASE}_brain_mask.nii.gz"
                
                # Nettoyage temporaire
                rm "$OUTPUT_T2_DIR/${T2_BASE}_for_bet.nii.gz"
            done
        fi

        # --- 2. Traitement T1 : Recalage et Masquage ---
        if [ -d "$SESS_DIR/T1_SWI" ]; then
            OUTPUT_T1_DIR="$DERIVATIVES_DIR/$SUB_ID/$SESS_ID/T1_SWI"
            mkdir -p "$OUTPUT_T1_DIR"
            
            for INPUT_T1 in "$SESS_DIR"/T1_SWI/*.nii.gz; do
                T1_FILENAME=$(basename "$INPUT_T1" .nii.gz)
                
                for INPUT_T2 in "$SESS_DIR"/T2/*.nii.gz; do
                    T2_BASE=$(basename "$INPUT_T2" .nii.gz)
                    MASK="$OUTPUT_T2_DIR/${T2_BASE}_brain_mask.nii.gz"
                    
                    if [ -f "$MASK" ]; then
                        echo "  -> Recalage et masquage T1 : $T1_FILENAME avec masque $T2_BASE"
                        
                        # A. Calcul de la matrice de recalage rigide T2 -> T1
                        flirt -in "$INPUT_T2" -ref "$INPUT_T1" \
                              -omat "${OUTPUT_T1_DIR}/T2_to_T1.mat" -dof 6
                        
                        # B. Application du masque T2 vers l'espace T1
                        flirt -in "$MASK" -ref "$INPUT_T1" \
                              -applyxfm -init "${OUTPUT_T1_DIR}/T2_to_T1.mat" \
                              -interp nearestneighbour \
                              -out "${OUTPUT_T1_DIR}/${T2_BASE}_mask_in_T1_space.nii.gz"
                        
                        # C. Application du masque sur le T1 original
                        fslmaths "$INPUT_T1" \
                                   -mas "${OUTPUT_T1_DIR}/${T2_BASE}_mask_in_T1_space.nii.gz" \
                                   "${OUTPUT_T1_DIR}/${T1_FILENAME}_brain_extracted.nii.gz"
                    fi
                done
            done
        fi
    done
done
echo "Traitement terminé avec succès."
