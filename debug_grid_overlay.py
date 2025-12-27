"""
Script per visualizzare lo screenshot con griglia cartesiana percentuale
"""
from PIL import ImageGrab
from shared_state import shared_state
import cv2
import numpy as np
import os

print("=" * 60)
print("GRIGLIA CARTESIANA PERCENTUALE")
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

# Crea una copia per la griglia
img_with_grid = screenshot_cv.copy()
height, width = screenshot_cv.shape[:2]

# Colori
grid_color = (0, 255, 0)  # Verde
text_color = (0, 255, 255)  # Giallo
axis_color = (255, 0, 0)  # Rosso

# Disegna linee verticali ogni 5%
for i in range(0, 101, 5):
    x = int(width * i / 100)
    # Linea più spessa ogni 10%
    thickness = 2 if i % 10 == 0 else 1
    cv2.line(img_with_grid, (x, 0), (x, height), grid_color, thickness)
    
    # Testo ogni 10%
    if i % 10 == 0:
        cv2.putText(img_with_grid, f"{i}%", (x + 2, 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
        cv2.putText(img_with_grid, f"{i}%", (x + 2, height - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)

# Disegna linee orizzontali ogni 5%
for i in range(0, 101, 5):
    y = int(height * i / 100)
    # Linea più spessa ogni 10%
    thickness = 2 if i % 10 == 0 else 1
    cv2.line(img_with_grid, (0, y), (width, y), grid_color, thickness)
    
    # Testo ogni 10%
    if i % 10 == 0:
        cv2.putText(img_with_grid, f"{i}%", (5, y - 5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
        cv2.putText(img_with_grid, f"{i}%", (width - 50, y - 5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)

# Disegna assi principali (0% rosso)
cv2.line(img_with_grid, (0, 0), (width, 0), axis_color, 3)
cv2.line(img_with_grid, (0, 0), (0, height), axis_color, 3)

# Salva l'immagine
grid_path = os.path.join(output_dir, "debug_grid_overlay.png")
cv2.imwrite(grid_path, img_with_grid)
print(f"\n✓ Griglia salvata: {grid_path}")

# Salva anche lo screenshot pulito per riferimento
clean_path = os.path.join(output_dir, "debug_clean_screen.png")
cv2.imwrite(clean_path, screenshot_cv)
print(f"✓ Screenshot pulito: {clean_path}")

print("\n" + "=" * 60)
print("COME LEGGERE LA GRIGLIA:")
print("=" * 60)
print("- Linee verdi ogni 5%, linee più spesse ogni 10%")
print("- Numeri gialli indicano le percentuali")
print("- Origine (0%, 0%) in alto a sinistra")
print("- x_percent = distanza da sinistra")
print("- y_percent = distanza dall'alto")
print("- right_percent = distanza da sinistra del bordo destro")
print("- bottom_percent = distanza dall'alto del bordo inferiore")
print("\nPer ogni edificio devi trovare:")
print("  x_percent: dove inizia il testo a sinistra")
print("  y_percent: dove inizia il testo in alto")
print("  right_percent: dove finisce il testo a destra")
print("  bottom_percent: dove finisce il testo in basso")
