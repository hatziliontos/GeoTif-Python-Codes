import os
import sys
import argparse
import re
import geopandas as gpd
import rasterio
from rasterio.mask import mask

def sanitize_filename(name):
 if not name or name == 'None':
  return "unnamed_subdem"
 safe_name = re.sub(r'[\\/*?:"<>|]', "", str(name))
 return safe_name.replace(" ", "_")

def clip_dem_with_gpkg(dem_path, gpkg_path):
 print(f"Ανάγνωση αρχείου διανυσματικών δεδομένων: {gpkg_path}")
 try:
  gdf = gpd.read_file(gpkg_path)
 except Exception as e:
  print(f"Σφάλμα κατά την ανάγνωση του GeoPackage: {e}")
  sys.exit(1)

 if 'NAME_EN' not in gdf.columns:
  print("Σφάλμα: Δεν βρέθηκε το πεδίο 'NAME_EN' στο αρχείο GeoPackage.")
  sys.exit(1)

 print(f"Άνοιγμα αρχείου DEM: {dem_path}")
 try:
  with rasterio.open(dem_path) as src:
   dem_crs = src.crs

   if gdf.crs != dem_crs:
    print(f"Τα CRS διαφέρουν. Γίνεται μετατροπή των πολυγώνων από {gdf.crs} σε {dem_crs}...")
    gdf = gdf.to_crs(dem_crs)

   print(f"Βρέθηκαν {len(gdf)} πολύγωνα. Ξεκινάει η διαδικασία αποκοπής (clip)...")

   for index, row in gdf.iterrows():
    geom = row.geometry
    name_en = row['NAME_EN']
    
    if geom is None or geom.is_empty:
     print(f"Παράλειψη: Το στοιχείο '{name_en}' δεν έχει έγκυρη γεωμετρία.")
     continue

    safe_name = sanitize_filename(name_en)
    out_tif_name = f"{safe_name}.tif"

    try:
     out_image, out_transform = mask(src, [geom], crop=True)
     out_meta = src.meta.copy()

     out_meta.update({
      "driver": "GTiff",
      "height": out_image.shape[1],
      "width": out_image.shape[2],
      "transform": out_transform,
      "compress": "deflate",
      "zlevel": 9,
      "tiled": True
     })

     with rasterio.open(out_tif_name, "w", **out_meta) as dest:
      dest.write(out_image)
     
     print(f"Επιτυχία: Δημιουργήθηκε το '{out_tif_name}'")

    except ValueError as e:
     print(f"Παράλειψη '{name_en}': {e}")
    except Exception as e:
     print(f"Απροσδόκητο σφάλμα στο '{name_en}': {e}")

 except Exception as e:
  print(f"Σφάλμα κατά την ανάγνωση του DEM: {e}")
  sys.exit(1)

 print("\nΗ διαδικασία ολοκληρώθηκε!")

if __name__ == "__main__":
 parser = argparse.ArgumentParser(description="Αποκοπή ενός DEM βάσει πολυγώνων από ένα GeoPackage.")
 parser.add_argument("dem_file", help="Η διαδρομή προς το αρχείο εισόδου (π.χ. dem.tif)")
 parser.add_argument("gpkg_file", help="Η διαδρομή προς το αρχείο πολυγωνικών επιφανειών (π.χ. subdems.gpkg)")
 
 args = parser.parse_args()
 
 if not os.path.isfile(args.dem_file):
  print(f"Σφάλμα: Το αρχείο DEM '{args.dem_file}' δεν βρέθηκε.")
  sys.exit(1)
  
 if not os.path.isfile(args.gpkg_file):
  print(f"Σφάλμα: Το αρχείο GeoPackage '{args.gpkg_file}' δεν βρέθηκε.")
  sys.exit(1)

 clip_dem_with_gpkg(args.dem_file, args.gpkg_file)