import rasterio
import numpy as np
import csv
import sys
import os
import glob

def process_dem_to_csv(dem_path):
 base_name, _ = os.path.splitext(dem_path)
 csv_path = f"{base_name}.csv"

 try:
  with rasterio.open(dem_path) as src:
   dem_data = src.read(1)
   nodata_val = src.nodata
 except Exception as e:
  print(f"Σφάλμα στο {dem_path}: {e}")
  return

 if nodata_val is not None:
  valid_pixels = dem_data[dem_data != nodata_val]
 else:
  valid_pixels = dem_data[~np.isnan(dem_data)]

 sorted_elevations = np.sort(valid_pixels)[::-1]
 total_pixels = len(sorted_elevations)

 if total_pixels == 0:
  print(f"Δεν βρέθηκαν έγκυρα δεδομένα στο {dem_path}.")
  return

 percentages = [i * 0.5 for i in range(11)]
 percentages.extend(range(6, 101, 1))

 try:
  with open(csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
   writer = csv.writer(csv_file, delimiter='\t')
   writer.writerow(["Area_Percentage", "Elevation_Z"])

   for p in percentages:
    if p == 100:
     idx = total_pixels - 1
    else:
     idx = int((p / 100.0) * total_pixels)
    
    z_value = sorted_elevations[idx]
    writer.writerow([f"{p:g}%", round(float(z_value), 3)])
   
  print(f"Επιτυχία: {csv_path}")
 except Exception as e:
  print(f"Σφάλμα εγγραφής στο {csv_path}: {e}")

def batch_process_directory(directory_path):
 search_pattern = os.path.join(directory_path, "*.tif")
 tif_files = glob.glob(search_pattern)

 if not tif_files:
  print(f"Δεν βρέθηκαν αρχεία .tif στον τρέχοντα φάκελο: {directory_path}")
  sys.exit(0)

 print(f"Βρέθηκαν {len(tif_files)} αρχεία .tif. Ξεκινάει η επεξεργασία...\n")

 for dem_file in tif_files:
  process_dem_to_csv(dem_file)
  
 print("\nΗ μαζική επεξεργασία ολοκληρώθηκε!")

if __name__ == "__main__":
 # Λαμβάνει αυτόματα τον φάκελο από τον οποίο τρέχει το script (τρέχων κατάλογος)
 current_folder = os.getcwd()
 batch_process_directory(current_folder)
