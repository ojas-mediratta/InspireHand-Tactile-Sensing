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
    
    # fingerone=pinky(3), fingertwo=ring(2), fingerthree=middle(1), fingerfour=index(0)
    finger_idx_by_var = {'fingerone': 3, 'fingertwo': 2, 'fingerthree': 1, 'fingerfour': 0}
    # (w, h), y_fraction for finger_base_y-relative; thumb uses thumb_y + fraction * thumb_length
    finger_zone = {'tip': ((0.03, 0.03), 1.0 - 0.05 / finger_length), 'top': ((0.06, 0.12), 0.6), 'palm': ((0.05, 0.1), 0.3)}
    thumb_zone = {'tip': ((0.03, 0.03), 1.0 - 0.05 / thumb_length), 'top': ((0.06, 0.12), 0.5), 'middle': ((0.03, 0.03), 0.3), 'palm': ((0.06, 0.12), 0.1)}

    regions = {}
    for name, addr, length, size, var in data_sheet:
        if var in finger_idx_by_var:
            idx = finger_idx_by_var[var]
            cx = finger_base_x + idx * finger_spacing + finger_width / 2
            for zone, ((w, h), y_frac) in finger_zone.items():
                if zone in var:
                    x, y = cx - w / 2, finger_base_y + finger_length * y_frac
                    break
        elif 'fingerfive' in var:
            cx = thumb_x + thumb_width / 2
            for zone, ((w, h), y_frac) in thumb_zone.items():
                if zone in var:
                    x, y = cx - w / 2, thumb_y + thumb_length * y_frac
                    break
        elif 'palm_touch' in var:
            w, h = 0.2, 0.2
            x = palm_x + palm_width / 2 - w / 2
            y = palm_y + 0.05
        regions[var] = {'bbox': (x, y, w, h), 'size': size, 'name': name}
    return regions


def draw_hand_outline(ax):
    palm = patches.Rectangle((0.21, 0.1), 0.35, 0.3, 
                              linewidth=2, edgecolor='black', 
                              facecolor='lightgray', alpha=0.2)
    ax.add_patch(palm)
    
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
    t = np.linspace(0, 1, 256)
    blue_yellow_cmap = ListedColormap(np.column_stack([np.where(t <= 0.5, 0, (t - 0.5) * 2), np.where(t <= 0.5, t * 2, 1), np.where(t <= 0.5, 1, 1 - (t - 0.5) * 2)]))
    
    # Get sensor region mappings
    sensor_regions = get_sensor_regions_on_hand()
    
    # Set up hand visualization
    baselines = {}  # Store baseline for each sensor
    smoothed_data = {}  # Store smoothed values for noise reduction
    smoothing_factor = 0.9  # Alpha for exponential moving average (0-1, lower = more smoothing)
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
