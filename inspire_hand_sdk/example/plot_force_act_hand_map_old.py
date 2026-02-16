import time

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
from matplotlib.colors import ListedColormap
import numpy as np
import colorcet

from dds_subscribe_485 import DDSHandler
from inspire_sdkpy import inspire_hand_defaut


def get_sensor_regions_on_hand():
    """Map each sensor from data_sheet to its location on the hand visualization"""
    data_sheet = inspire_hand_defaut.data_sheet
    
    # Define hand regions in normalized coordinates (0-1)
    # Finger positions: from left (pinky) to right (index)
    finger_base_x = 0.22  # Moved left
    finger_base_y = 0.4
    finger_width = 0.08
    finger_length = 0.4
    finger_spacing = 0.09  # More compact spacing
    
    # Thumb position (on the left, closer to palm)
    thumb_x = 0.12
    thumb_y = 0.25
    thumb_width = 0.08
    thumb_length = 0.35
    
    # Palm position (closer to thumb)
    palm_x = 0.2
    palm_y = 0.1
    palm_width = 0.35
    palm_height = 0.3
    
    regions = {}
    
    # Map each sensor to its location
    # fingerone = pinky (leftmost)
    # fingertwo = ring
    # fingerthree = middle
    # fingerfour = index
    # fingerfive = thumb
    
    for name, addr, length, size, var in data_sheet:
        if 'fingerone' in var:  # Pinky
            finger_idx = 3  # Leftmost finger
            finger_center_x = finger_base_x + finger_idx * finger_spacing + finger_width / 2
            if 'tip' in var:
                # Tip at the end of finger, centered
                w, h = 0.03, 0.03
                x = finger_center_x - w / 2
                y = finger_base_y + finger_length - 0.05
            elif 'top' in var:
                # Top sensor along finger, centered
                w, h = 0.06, 0.12
                x = finger_center_x - w / 2
                y = finger_base_y + finger_length * 0.6
            elif 'palm' in var:
                # Palm side of finger, centered
                w, h = 0.05, 0.1
                x = finger_center_x - w / 2
                y = finger_base_y + finger_length * 0.3
        elif 'fingertwo' in var:  # Ring
            finger_idx = 2
            finger_center_x = finger_base_x + finger_idx * finger_spacing + finger_width / 2
            if 'tip' in var:
                w, h = 0.03, 0.03
                x = finger_center_x - w / 2
                y = finger_base_y + finger_length - 0.05
            elif 'top' in var:
                w, h = 0.06, 0.12
                x = finger_center_x - w / 2
                y = finger_base_y + finger_length * 0.6
            elif 'palm' in var:
                w, h = 0.05, 0.1
                x = finger_center_x - w / 2
                y = finger_base_y + finger_length * 0.3
        elif 'fingerthree' in var:  # Middle
            finger_idx = 1
            finger_center_x = finger_base_x + finger_idx * finger_spacing + finger_width / 2
            if 'tip' in var:
                w, h = 0.03, 0.03
                x = finger_center_x - w / 2
                y = finger_base_y + finger_length - 0.05
            elif 'top' in var:
                w, h = 0.06, 0.12
                x = finger_center_x - w / 2
                y = finger_base_y + finger_length * 0.6
            elif 'palm' in var:
                w, h = 0.05, 0.1
                x = finger_center_x - w / 2
                y = finger_base_y + finger_length * 0.3
        elif 'fingerfour' in var:  # Index
            finger_idx = 0
            finger_center_x = finger_base_x + finger_idx * finger_spacing + finger_width / 2
            if 'tip' in var:
                w, h = 0.03, 0.03
                x = finger_center_x - w / 2
                y = finger_base_y + finger_length - 0.05
            elif 'top' in var:
                w, h = 0.06, 0.12
                x = finger_center_x - w / 2
                y = finger_base_y + finger_length * 0.6
            elif 'palm' in var:
                w, h = 0.05, 0.1
                x = finger_center_x - w / 2
                y = finger_base_y + finger_length * 0.3
        elif 'fingerfive' in var:  # Thumb
            thumb_center_x = thumb_x + thumb_width / 2
            if 'tip' in var:
                w, h = 0.03, 0.03
                x = thumb_center_x - w / 2
                y = thumb_y + thumb_length - 0.05
            elif 'top' in var:
                w, h = 0.06, 0.12
                x = thumb_center_x - w / 2
                y = thumb_y + thumb_length * 0.5
            elif 'middle' in var:
                w, h = 0.03, 0.03
                x = thumb_center_x - w / 2
                y = thumb_y + thumb_length * 0.3
            elif 'palm' in var:
                w, h = 0.06, 0.12
                x = thumb_center_x - w / 2
                y = thumb_y + thumb_length * 0.1
        elif 'palm_touch' in var:  # Palm
            palm_center_x = palm_x + palm_width / 2
            w, h = 0.2, 0.2
            x = palm_center_x - w / 2
            y = palm_y + 0.05
        
        regions[var] = {
            'bbox': (x, y, w, h),
            'size': size,
            'name': name
        }
    
    return regions


def draw_hand_outline(ax):
    """Draw a simplified hand outline"""
    # Palm (base, closer to thumb)
    palm = patches.Rectangle((0.21, 0.1), 0.35, 0.3, 
                              linewidth=2, edgecolor='black', 
                              facecolor='lightgray', alpha=0.2)
    ax.add_patch(palm)
    
    # Fingers (from left to right: pinky, ring, middle, index)
    finger_width = 0.08
    finger_length = 0.4
    finger_spacing = 0.09  # More compact spacing
    finger_base_x = 0.22  # Moved left
    
    for i in range(4):
        x = finger_base_x + i * finger_spacing
        finger = patches.Rectangle((x, 0.4), finger_width, finger_length,
                                   linewidth=2, edgecolor='black',
                                   facecolor='lightgray', alpha=0.2)
        ax.add_patch(finger)
    
    # Thumb (positioned on the left, straight up, closer to palm)
    thumb_x = 0.12
    thumb_y = 0.25
    thumb_width = 0.08
    thumb_length = 0.35
    thumb = patches.Rectangle((thumb_x, thumb_y), thumb_width, thumb_length,
                             linewidth=2, edgecolor='black',
                             facecolor='lightgray', alpha=0.2)
    ax.add_patch(thumb)


def main():
    # Subscribe to touch data (like ImageTab does)
    dds_handler = DDSHandler(sub_touch=True)
    data_sheet = inspire_hand_defaut.data_sheet
    
    # Create blue to yellow colormap
    # Blue (low) to Cyan to Yellow (high)
    colors_blue_yellow = []
    for i in range(256):
        if i < 128:
            # Blue to Cyan
            r = 0
            g = i / 127.0
            b = 1.0
        else:
            # Cyan to Yellow
            r = (i - 128) / 127.0
            g = 1.0
            b = 1.0 - (i - 128) / 127.0
        colors_blue_yellow.append((r, g, b))
    blue_yellow_cmap = ListedColormap(colors_blue_yellow)
    
    # Get sensor region mappings
    sensor_regions = get_sensor_regions_on_hand()
    
    # Set up hand visualization
    baselines = {}  # Store baseline for each sensor
    smoothed_data = {}  # Store smoothed values for noise reduction
    smoothing_factor = 0.3  # Alpha for exponential moving average (0-1, lower = more smoothing)
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Draw hand outline
    draw_hand_outline(ax)
    
    # Create image overlays for each sensor (initially empty/transparent)
    sensor_images = {}
    for name, addr, length, size, var in data_sheet:
        if var in sensor_regions:
            x, y, w, h = sensor_regions[var]['bbox']
            # Create initial empty image
            img_data = np.zeros(size, dtype=float)
            # Use imshow to display sensor data
            extent = [x, x + w, y, y + h]
            im = ax.imshow(img_data, extent=extent, origin='lower',
                          cmap=blue_yellow_cmap, alpha=0.8,
                          vmin=0, vmax=100, interpolation='nearest')
            sensor_images[var] = im
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("Inspire Hand Touch Sensor Map", fontsize=16, weight='bold', pad=20)
    
    # Add colorbar (like ImageTab)
    sm = plt.cm.ScalarMappable(cmap=blue_yellow_cmap, norm=plt.Normalize(vmin=0, vmax=100))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, orientation='horizontal', pad=0.05, fraction=0.05)
    cbar.set_label('Touch Sensor Value (0-100)', fontsize=12)
    
    plt.tight_layout()
    plt.ion()
    plt.show()

    try:
        while plt.fignum_exists(fig.number):
            # Read touch data (like ImageTab.update_plot)
            data_dict = dds_handler.read()
            touch_data = data_dict.get('touch', {})
            
            # Update each sensor overlay
            for name, addr, length, size, var in data_sheet:
                if var in touch_data and var in sensor_images:
                    sensor_matrix = touch_data[var]
                    
                    if sensor_matrix is not None and sensor_matrix.size > 0:
                        # Ensure it's the right shape
                        if sensor_matrix.shape != size:
                            try:
                                sensor_matrix = sensor_matrix.reshape(size)
                            except:
                                continue
                        
                        # Initialize baseline from first valid reading
                        if var not in baselines:
                            baselines[var] = sensor_matrix.copy()
                            smoothed_data[var] = sensor_matrix.copy()
                        
                        # Calculate relative values (start at 0)
                        relative_data = sensor_matrix - baselines[var]
                        # Clamp to fixed display range
                        relative_data = np.clip(relative_data, 0.0, 100.0)
                        
                        # Apply exponential moving average for noise reduction
                        if var in smoothed_data:
                            # Smooth: new_value = alpha * current + (1-alpha) * previous
                            smoothed_data[var] = (smoothing_factor * relative_data + 
                                                  (1 - smoothing_factor) * smoothed_data[var])
                        else:
                            smoothed_data[var] = relative_data.copy()
                        
                        # Update image with smoothed data
                        sensor_images[var].set_data(smoothed_data[var])
                        # Keep fixed scale 0-100 (like ImageTab but with fixed range)
                        sensor_images[var].set_clim(0, 100)
            
            fig.canvas.draw_idle()
            plt.pause(0.05)  # ~20 Hz update rate

    except KeyboardInterrupt:
        # Allow clean exit on Ctrl+C
        pass


if __name__ == "__main__":
    main()
