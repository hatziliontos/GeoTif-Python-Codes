import os
import glob
from osgeo import gdal

def calculate_percent_slope_batch(directory_path):
    # Ενεργοποίηση εξαιρέσεων για καλύτερο εντοπισμό σφαλμάτων
    gdal.UseExceptions()
    
    # Εύρεση όλων των .tif αρχείων στον φάκελο
    search_pattern = os.path.join(directory_path, '*.tif')
    tif_files = glob.glob(search_pattern)
    
    if not tif_files:
        print(f"Δεν βρέθηκαν αρχεία .tif στον φάκελο:\n{directory_path}")
        return

    processed_count = 0
    
    # Επιλογές δημιουργίας για μέγιστη συμπίεση GeoTIFF
    creation_opts = [
        'COMPRESS=DEFLATE', # Αλγόριθμος συμπίεσης με την υψηλότερη απόδοση για raster
        'ZLEVEL=9',         # Μέγιστο επίπεδο συμπίεσης (1-9)
        'PREDICTOR=2',      # Βελτιστοποίηση για δεδομένα κινητής υποδιαστολής (Float)
        'TILED=YES'         # Εσωτερική οργάνωση σε tiles (απαραίτητο για μεγάλα αρχεία)
    ]
    
    for tif_path in tif_files:
        # Αποφυγή επανεπεξεργασίας
        if tif_path.lower().endswith('_slope.tif'):
            continue
            
        file_dir, file_name = os.path.split(tif_path)
        name_only, ext = os.path.splitext(file_name)
        output_name = f"{name_only}_slope{ext}"
        output_path = os.path.join(file_dir, output_name)
        
        print(f"Επεξεργασία: {file_name} ...")
        
        try:
            # Υπολογισμός κλίσης με ενσωμάτωση των επιλογών συμπίεσης
            gdal.DEMProcessing(
                destName=output_path,
                srcDS=tif_path,
                processing='slope',
                slopeFormat='percent',
                computeEdges=True,
                creationOptions=creation_opts
            )
            print(f"  -> Αποθηκεύτηκε με μέγιστη συμπίεση: {output_name}")
            processed_count += 1
            
        except Exception as e:
            print(f"  -> Σφάλμα στο {file_name}: {str(e)}")

    print(f"\nΟλοκληρώθηκε! Επεξεργάστηκαν {processed_count} αρχεία.")

# --- Εκτέλεση Κώδικα ---
if __name__ == "__main__":
    current_folder = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Φάκελος εργασίας: {current_folder}\n")
    calculate_percent_slope_batch(current_folder)