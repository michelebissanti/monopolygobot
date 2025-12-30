from mss import mss
from mss.tools import to_png
import pyscreeze
import cv2
import numpy as np
from pytesseract import pytesseract
from shared_state import shared_state
import pyautogui
import time

pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"


class OCRUtils:
    def __init__(self):
        """
        Initialize the OCRUtils class.

        This class provides utility functions for performing optical character recognition (OCR) on screen captures.
        It uses various libraries such as PIL, OpenCV, NumPy, and pytesseract.

        Attributes:
            window: A tuple representing the window coordinates (x, y, width, height).
            window_x: The x-coordinate of the window's top-left corner.
            window_y: The y-coordinate of the window's top-left corner.
            window_width: The width of the window.
            window_height: The height of the window.
            window_coords: A tuple representing the window coordinates (left, top, right, bottom).
            window_size: The size of the window.
        """
        self.window = shared_state.window
        (
            self.window_x,
            self.window_y,
            self.window_width,
            self.window_height,
        ) = self.window
        self.window_coords = shared_state.window_coords
        self.window_size = self.window

    def find_template(self, template: np.ndarray, bbox=None, threshold=0.50) -> pyscreeze.Point | None:
        """
        Robust Template Matching with Multi-Scale support.
        This allows finding UI elements even if the resolution differs slightly.
        """
        try:
            if bbox is None:
                bbox = self.window_coords
            
            with mss() as sct:
                monitor = {
                    "top": bbox[1],
                    "left": bbox[0],
                    "width": bbox[2] - bbox[0],
                    "height": bbox[3] - bbox[1]
                }
                sct_img = sct.grab(monitor)
                screenshot_cv = cv2.cvtColor(np.array(sct_img), cv2.COLOR_BGRA2BGR)

            # --- Multi-Scale Logic ---
            best_match_val = -1
            best_match_loc = None
            best_scale = 1.0
            
            # Helper to get width/height
            t_h, t_w = template.shape[:2]

            # Define scales to search: 80% to 120% in 10 steps (Focus on minor variations first for speed)
            # If "different resolutions" implies big changes, we can widen to 0.5 - 1.5
            scales = np.linspace(0.8, 1.2, 11) 

            # Also check exact scale 1.0 explicitly just in case linspace misses it slightly
            if 1.0 not in scales:
                scales = np.append(scales, 1.0)
            
            for scale in scales:
                # Resize template
                width = int(t_w * scale)
                height = int(t_h * scale)
                
                # Skip if template becomes larger than screenshot
                if width > screenshot_cv.shape[1] or height > screenshot_cv.shape[0]:
                    continue
                    
                resized_template = cv2.resize(template, (width, height))
                
                res = cv2.matchTemplate(screenshot_cv, resized_template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                
                if max_val > best_match_val:
                    best_match_val = max_val
                    best_match_loc = max_loc
                    best_scale = scale
            
            # Check if our best match exceeds threshold
            if best_match_val >= threshold:
                x, y = best_match_loc
                # Calculate center based on the SCALED template size
                center_x = x + int(t_w * best_scale / 2)
                center_y = y + int(t_h * best_scale / 2)
                
                match_center_absolute = (
                    int(center_x + bbox[0]),
                    int(center_y + bbox[1])
                )
                
                # Debug Overlay
                w_final = int(t_w * best_scale)
                h_final = int(t_h * best_scale)
                top_left_abs = (int(x + bbox[0]), int(y + bbox[1]))
                
                shared_state.debug_overlays.append(
                    ((top_left_abs[0], top_left_abs[1], w_final, h_final), f"Match ({int(best_match_val*100)}%) S:{best_scale:.2f}", time.time())
                )
                
                return match_center_absolute

            return None
         
        except Exception as e:
            print(f"[OCR] find_template failed: {e}")
            return None


    def find_sift(self, template: np.ndarray, bbox=None, min_match_count=10) -> pyscreeze.Point | None:
        """
        Find a template image using SIFT Feature Matching.
        Robust to scale, rotation, and brightness changes.
        """
        try:
            if bbox is None:
                bbox = self.window_coords
            
            with mss() as sct:
                monitor = {
                    "top": bbox[1],
                    "left": bbox[0],
                    "width": bbox[2] - bbox[0],
                    "height": bbox[3] - bbox[1]
                }
                sct_img = sct.grab(monitor)
                screenshot_cv = cv2.cvtColor(np.array(sct_img), cv2.COLOR_BGRA2BGR)

            # Initialize SIFT detector
            sift = cv2.SIFT_create()

            # Find the keypoints and descriptors with SIFT
            kp1, des1 = sift.detectAndCompute(template, None)
            kp2, des2 = sift.detectAndCompute(screenshot_cv, None)

            # FLANN parameters
            FLANN_INDEX_KDTREE = 1
            index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
            search_params = dict(checks=50)

            flann = cv2.FlannBasedMatcher(index_params, search_params)
            
            # Need check if descriptors are None (e.g. blank images)
            if des1 is None or des2 is None or len(des1) < 2 or len(des2) < 2:
                return None

            matches = flann.knnMatch(des1, des2, k=2)

            # Store all the good matches as per Lowe's ratio test.
            good = []
            for m, n in matches:
                if m.distance < 0.7 * n.distance:
                    good.append(m)

            if len(good) > min_match_count:
                src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
                dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                
                if M is not None:
                    h, w, d = template.shape
                    pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
                    dst = cv2.perspectiveTransform(pts, M)

                    # Calculate center of the projected quad
                    # Simple average of corners
                    center_x = np.mean(dst[:, 0, 0])
                    center_y = np.mean(dst[:, 0, 1])
                    
                    match_center_absolute = (
                        int(center_x) + bbox[0],
                        int(center_y) + bbox[1]
                    )
                    # logger.debug(f"[OCR-SIFT] Found match with {len(good)} good matches.")
                    # Debug Overlay (SIFT uses center point usually)
                    shared_state.debug_overlays.append(
                        (match_center_absolute, f"SIFT ({len(good)})", time.time())
                    )
                    return match_center_absolute
            
            # logger.debug(f"[OCR-SIFT] Not enough matches are found - {len(good)}/{min_match_count}")
            return None

        except Exception as e:
            print(f"[OCR-SIFT] Error: {e}")
            return None

    def find(self, template: np.ndarray, bbox=None, threshold=0.65, min_match_count=8) -> pyscreeze.Point | None:
        # Priority: SIFT > Template Matching
        
        # 1. Try SIFT (Feature Matching)
        match = self.find_sift(template, bbox, min_match_count=min_match_count)
        
        # 2. Fallback
        if not match:
             match = self.find_template(template, bbox, threshold)
             
        # Safety Check: PyAutoGUI Fail-Safe trigger (corners)
        if match:
            screen_w, screen_h = pyautogui.size()
            x, y = match
            
            # Reset triggers: (0,0), (w,0), (0,h), (w,h)
            # We add a margin of 5 pixels to be safe
            margin = 5
            # Fix: Ensure we only check for (0,0) of the PRIMARY monitor (where failsafe usually is)
            # and ignore negative coordinates which are valid on secondary monitors.
            in_left = 0 <= x < margin
            in_right = (screen_w - margin) < x <= screen_w
            in_top = 0 <= y < margin
            in_bottom = (screen_h - margin) < y <= screen_h
            
            if (in_left and in_top) or (in_right and in_top) or (in_left and in_bottom) or (in_right and in_bottom):
                 print(f"[OCR] Ignored match at unsafe coordinates ({x}, {y})")
                 return None
                 
        return match

    def preprocess_image(
        self,
        image,
        target_size=None,
        threshold_value=None,
        invert=None,
    ):
        """
        Preprocess an image for OCR by resizing, converting to grayscale, and thresholding.

        Args:
            image: The input image to preprocess.
            target_size (tuple, optional): The target size for resizing (width, height).
            threshold_value (int, optional): The threshold value for binarization.
            invert (bool, optional): Whether to invert the colors (black background).

        Returns:
            np.ndarray: The preprocessed image.
        """
        # Resize the image to the target size (if specified)
        if target_size:
            image = cv2.resize(image, target_size, interpolation=cv2.INTER_LANCZOS4)
        # Convert the image to grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Apply thresholding if threshold_value is provided\
        if invert:
            if threshold_value is not None:
                _, thresholded_image = cv2.threshold(
                    gray_image,
                    threshold_value,
                    255,
                    cv2.THRESH_BINARY_INV,
                )
                return thresholded_image
            if threshold_value is None:
                gray_image_inv = 255 - gray_image
                return gray_image_inv
        else:
            if threshold_value is not None:
                _, thresholded_image = cv2.threshold(
                    gray_image,
                    threshold_value,
                    255,
                    cv2.THRESH_BINARY,
                )
                return thresholded_image
            if threshold_value is None:
                return gray_image

    def ocr_to_str(
        self,
        region_x_percent,
        region_y_percent,
        region_right_percent,
        region_bottom_percent,
        output_image_path=None,
        ocr_settings=None,
        process_settings=None,
    ):
        """
        Perform OCR on a specified region of the screen and return the recognized text.

        Args:
            region_x_percent (float): The X-coordinate percentage of the left edge of the region.
            region_y_percent (float): The Y-coordinate percentage of the top edge of the region.
            region_right_percent (float): The X-coordinate percentage of the right edge of the region.
            region_bottom_percent (float): The Y-coordinate percentage of the bottom edge of the region.
            output_image_path (str, optional): The path to save the preprocessed image.
            ocr_settings (str, optional): Additional OCR configuration settings.
            process_settings (dict, optional): Image preprocessing settings.

        Returns:
            str: The recognized text within the specified region.
        """
        left = int(
            self.window_x + (self.window_width * (region_x_percent / 100))
        )
        upper = int(
            self.window_y + (self.window_height * (region_y_percent / 100))
        )
        right = int(
            self.window_x
            + (self.window_width * (region_right_percent / 100))
        )
        bottom = int(
            self.window_y
            + (self.window_height * (region_bottom_percent / 100))
        )

        width = right - left
        height = bottom - upper

        # Debug Overlay for OCR Region
        try:
             # Store as (left, top, w, h)
             # Adjust relative for visualizer if needed, but visualizer expects abs coords
             shared_state.debug_overlays.append(
                ((left, upper, width, height), "OCR Region", time.time())
             )
        except Exception:
             pass

        with mss() as sct:
            monitor = {
                "top": upper,
                "left": left,
                "width": width,
                "height": height
            }
            sct_img = sct.grab(monitor)
            # Convert BGRA to BGR to be consistent with previous RGB->BGR assumptions (or just BGR)
            screenshot_np = cv2.cvtColor(np.array(sct_img), cv2.COLOR_BGRA2BGR)
            
            # Preprocessing: Convert to Grayscale (Helps with white text/contrast)
            screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)

        # screenshot_cropped = screenshot_np[upper:bottom, left:right]
        if process_settings:
            screenshot_size = (
                screenshot_np.shape[1] * process_settings["scale_factor"],
                screenshot_np.shape[0] * process_settings["scale_factor"],
            )
            screenshot_proc = self.preprocess_image(
                image=screenshot_np,
                target_size=screenshot_size,
                threshold_value=process_settings["threshold_value"],
                invert=process_settings["invert"],
            )
        else:
            # Default to grayscale if no settings provided (Better for simple OCR)
            screenshot_proc = screenshot_gray
        if output_image_path:
            cv2.imwrite(output_image_path, screenshot_proc)
        if ocr_settings:
            text = pytesseract.image_to_string(screenshot_proc, config=ocr_settings)
        else:
            text = pytesseract.image_to_string(screenshot_proc)

        return text

    def screenshot(self, name):
        """
        Capture a screenshot of the entire window and save it to a file.

        Args:
            name (str): The name and path of the output screenshot file.
        """
        with mss() as sct:
            monitor = {
                "top": self.window_coords[1],
                "left": self.window_coords[0],
                "width": self.window_coords[2] - self.window_coords[0],
                "height": self.window_coords[3] - self.window_coords[1]
            }
            to_png(sct.grab(monitor).rgb, sct.grab(monitor).size, output=name)
