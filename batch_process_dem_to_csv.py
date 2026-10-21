import rasterio
import numpy as np
import csv
import sys
import os
import glob
import matplotlib.pyplot as plt

def batch_process_to_single_csv(directory_path):
 search_pattern = os.path.join(directory_path, "*.tif")
 tif_files = glob.glob(search_pattern)

 if not tif_files:
  print(f"Δεν βρέθηκαν αρχεία .tif στον φάκελο: {directory_path}")
  sys.exit(0)

 print(f"Βρέθηκαν {len(tif_files)} αρχεία .tif. Ξεκινάει η επεξεργασία...\n")

 # Λίστες ποσοστών
 # Πίνακας 1: 0% - 5% (ανά 0.5%) και 6% - 100% (ανά 1%)
 p1 = [i * 0.5 for i in range(11)]
 p1.extend(range(6, 101, 1))
 
 # Πίνακας 2: 0% - 100% (ανά 5%)
 p2 = list(range(0, 101, 5))

 results = []

 # Βρόχος για κάθε TIF
 for dem_path in tif_files:
  base_name, _ = os.path.splitext(os.path.basename(dem_path))
  
  try:
   with rasterio.open(dem_path) as src:
    dem_data = src.read(1)
    nodata_val = src.nodata
  except Exception as e:
   print(f"Σφάλμα στο {dem_path}: {e}")
   continue

  if nodata_val is not None:
   valid_pixels = dem_data[dem_data != nodata_val]
  else:
   valid_pixels = dem_data[~np.isnan(dem_data)]

  total_pixels = len(valid_pixels)
  if total_pixels == 0:
   print(f"Δεν βρέθηκαν έγκυρα δεδομένα στο {dem_path}.")
   continue

  # Σταθμισμένο μέσο υψόμετρο (ο μέσος όρος όλων των valid pixels)
  mean_elev = np.mean(valid_pixels)
  
  # Ταξινόμηση
  sorted_elevations = np.sort(valid_pixels)[::-1]

  # Υπολογισμός τιμών Z για τον Πίνακα 1
  z_list1 = []
  for p in p1:
   idx = total_pixels - 1 if p == 100 else int((p / 100.0) * total_pixels)
   z_list1.append(sorted_elevations[idx])

  # Υπολογισμός τιμών Z για τον Πίνακα 2
  z_list2 = []
  for p in p2:
   idx = total_pixels - 1 if p == 100 else int((p / 100.0) * total_pixels)
   z_list2.append(sorted_elevations[idx])

  # Αποθήκευση στη μνήμη για την τελική εγγραφή
  results.append({
   'name': base_name,
   'mean': mean_elev,
   'table1': z_list1,
   'table2': z_list2
  })

  # Δημιουργία ξεχωριστού γραφήματος για το TIF
  plt.figure(figsize=(10, 6))
  plt.plot(p1, z_list1, color='blue', linewidth=2)
  plt.title(f"Υψομετρική Καμπύλη - {base_name}")
  plt.xlabel("Ποσοστό Έκτασης (%)")
  plt.ylabel("Υψόμετρο (m)")
  plt.grid(True, linestyle='--', alpha=0.7)
  
  plot_filename = f"{base_name}_hypsometric.png"
  plt.savefig(plot_filename, dpi=300)
  plt.close()
  print(f"Δημιουργήθηκε γράφημα: {plot_filename}")

 if not results:
  print("Δεν προέκυψαν έγκυρα δεδομένα για κανένα αρχείο.")
  sys.exit(1)

 # Εγγραφή στο ενιαίο CSV
 combined_csv = "combined_hypsometric_curves.csv"
 try:
  with open(combined_csv, mode='w', newline='', encoding='utf-8') as f:
   writer = csv.writer(f, delimiter='\t')
   
   # Επικεφαλίδα για τα TIFs
   header = ["Area_Percentage"] + [r['name'] for r in results]
   
   # --- ΠΙΝΑΚΑΣ 1 ---
   writer.writerow(["--- ΠΙΝΑΚΑΣ 1: 0-5% (βήμα 0.5%), 5-100% (βήμα 1%) ---"])
   writer.writerow(header)
   for i, p in enumerate(p1):
    row = [f"{p:g}%"] + [round(float(r['table1'][i]), 3) for r in results]
    writer.writerow(row)
   
   writer.writerow([]) # Κενή γραμμή
   
   # --- ΣΤΑΘΜΙΣΜΕΝΟ ΜΕΣΟ ΥΨΟΜΕΤΡΟ ---
   mean_row = ["Weighted_Mean_Elevation"] + [round(float(r['mean']), 3) for r in results]
   writer.writerow(mean_row)
   
   writer.writerow([]) # Κενή γραμμή
   
   # --- ΠΙΝΑΚΑΣ 2 ---
   writer.writerow(["--- ΠΙΝΑΚΑΣ 2: 0-100% (βήμα 5%) ---"])
   writer.writerow(header)
   for i, p in enumerate(p2):
    row = [f"{p:g}%"] + [round(float(r['table2'][i]), 3) for r in results]
    writer.writerow(row)

  print(f"\nΌλα τα δεδομένα εξήχθησαν επιτυχώς στο αρχείο: {combined_csv}")
 except Exception as e:
  print(f"Σφάλμα κατά την εγγραφή του ενιαίου CSV: {e}")

if __name__ == "__main__":
 current_folder = os.getcwd()
 batch_process_to_single_csv(current_folder)
