"""
Script di debug per trovare le coordinate corrette dei costi degli edifici
"""
from PIL import ImageGrab
from shared_state import shared_state
import cv2
import numpy as np
import os

print("=" * 60)
print("DEBUG REGIONI COSTI EDIFICI")
print("=" * 60)
print("\nASSICURATI DI ESSERE NELLA SCHERMATA BUILD!")
input("\nPremi ENTER quando sei pronto...")

# Crea la directory se non esiste
output_dir = "debug_screenshots/build"
os.makedirs(output_dir, exist_ok=True)

# Cattura screenshot completo
window_coords = shared_state.window_coords
screenshot = ImageGrab.grab(bbox=window_coords)
screenshot_np = np.array(screenshot)
screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

# Salva screenshot completo
full_screen_path = os.path.join(output_dir, "debug_full_build_screen.png")
cv2.imwrite(full_screen_path, screenshot_cv)
print(f"\n✓ Screenshot completo salvato: {full_screen_path}")

# Coordinate corrette degli edifici
buildings = [
    {"name": "building1", "x": 37, "y": 86, "right": 40.5, "bottom": 91},
    {"name": "building2", "x": 42.5, "y": 86, "right": 46, "bottom": 91},
    {"name": "building3", "x": 48.5, "y": 86, "right": 52, "bottom": 91},
    {"name": "building4", "x": 54.5, "y": 86, "right": 58, "bottom": 91},
    {"name": "building5", "x": 60.5, "y": 86, "right": 64, "bottom": 91},
]

# Disegna rettangoli sulle regioni attuali
img_with_boxes = screenshot_cv.copy()
height, width = screenshot_cv.shape[:2]

for building in buildings:
    x1 = int(width * building["x"] / 100)
    y1 = int(height * building["y"] / 100)
    x2 = int(width * building["right"] / 100)
    y2 = int(height * building["bottom"] / 100)
    
    # Disegna rettangolo rosso
    cv2.rectangle(img_with_boxes, (x1, y1), (x2, y2), (0, 0, 255), 2)
    cv2.putText(img_with_boxes, building["name"], (x1, y1-5), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

regions_path = os.path.join(output_dir, "debug_build_regions.png")
cv2.imwrite(regions_path, img_with_boxes)
print(f"✓ Screenshot con regioni marcate: {regions_path}")

print("\n" + "=" * 60)
print("SUGGERIMENTI PER NUOVE COORDINATE:")
print("=" * 60)
print(f"\nGuarda '{output_dir}/debug_build_regions.png' e modifica le coordinate")
print("in base a dove vedi effettivamente i costi degli edifici.")
print("\nCONSIGLI:")
print("- Se i rettangoli sono troppo in basso, riduci y_percent e bottom_percent")
print("- Se sono troppo larghi, stringi x_percent e right_percent")
print("- Il testo del costo dovrebbe essere centrato nel rettangolo rosso")
