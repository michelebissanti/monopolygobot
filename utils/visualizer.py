from threading import Thread, Event
import cv2
import numpy as np
import time
from mss import mss
from shared_state import shared_state

class Visualizer:
    def __init__(self):
        self.window_name = "MonopolyGoBot Debug View"
        self.running = False
        self.fps = 10
        self.frame_delay = 1.0 / self.fps
        self.stop_event = Event()

    def run(self):
        self.running = True
        # Run visualization loop in the main thread (OpenCV requirement for GUI)
        self._visualization_loop()

    def _visualization_loop(self):
        with mss() as sct:
            while self.running and not self.stop_event.is_set():
                start_time = time.time()
                
                try:
                    # 1. Capture Screen
                    monitor = {
                        "top": shared_state.window_y,
                        "left": shared_state.window_x,
                        "width": shared_state.window_width,
                        "height": shared_state.window_height
                    }
                    if monitor["width"] <= 0 or monitor["height"] <= 0:
                         # Skip if invalid dimensions (e.g. minimized or calculating)
                         time.sleep(1)
                         continue
                         
                    sct_img = sct.grab(monitor)
                    frame = np.array(sct_img)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR) # OpenCV uses BGR

                    # 2. Draw Overlays
                    # Clean up old overlays (older than 2 seconds)
                    current_time = time.time()
                    shared_state.debug_overlays = [
                        o for o in shared_state.debug_overlays 
                        if current_time - o[2] < 2.0
                    ]

                    for overlay in shared_state.debug_overlays:
                        rect_or_point, label, timestamp = overlay
                        
                        # Check if it's a point (tuple of 2) or rect (tuple of 4)
                        if len(rect_or_point) == 2:
                             # Point
                             x, y = rect_or_point
                             # Adjust relative to window if needed? 
                             # Assuming points stored are absolute (screen coords)
                             # Convert to window relative for drawing
                             rel_x = x - shared_state.window_x
                             rel_y = y - shared_state.window_y
                             
                             cv2.circle(frame, (rel_x, rel_y), 5, (0, 0, 255), -1)
                             cv2.putText(frame, label, (rel_x + 10, rel_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                             
                        elif len(rect_or_point) == 4:
                             # Rect (x, y, w, h) - assuming absolute screen coords for x,y
                             x, y, w, h = rect_or_point
                             rel_x = x - shared_state.window_x
                             rel_y = y - shared_state.window_y
                             
                             cv2.rectangle(frame, (rel_x, rel_y), (rel_x + w, rel_y + h), (0, 255, 0), 2)
                             cv2.putText(frame, label, (rel_x, rel_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                    # 3. Draw Logs - REMOVED per user request
                    # y_offset = frame.shape[0] - 20
                    # for log in reversed(shared_state.recent_logs):
                    #     ...

                    # 4. Show Frame
                    cv2.imshow(self.window_name, frame)
                    
                    # Handle quit
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        self.stop()
                        break

                except Exception as e:
                    print(f"[VISUALIZER] Error: {e}")
                    time.sleep(1)

                # Cap FPS
                elapsed = time.time() - start_time
                if elapsed < self.frame_delay:
                    time.sleep(self.frame_delay - elapsed)
        
        cv2.destroyAllWindows()

    def stop(self):
        self.running = False
        self.stop_event.set()
