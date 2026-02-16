import time
import os
import csv
import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
from matplotlib.colors import ListedColormap
from matplotlib.ticker import MultipleLocator
import numpy as np
import pprint
from scipy.ndimage import zoom

from dds_subscribe_485 import DDSHandler
from inspire_sdkpy import inspire_hand_defaut

# Set maximum raw data
max_raw_data = 4095

def get_sensor_regions_on_hand():
    """Map each sensor from data_sheet to its location on the hand visualization"""
    data_sheet = inspire_hand_defaut.data_sheet
    finger_base_x = 0.22
    finger_base_y = 0.42
    finger_width = 0.08
    finger_length = 0.4
    finger_spacing = 0.09
    thumb_x, thumb_y, thumb_width, thumb_length = 0.59, 0.20, 0.08, 0.35
    palm_x, palm_y, palm_width, palm_height = 0.22, 0.1, 0.35, 0.3
    
    regions = {}
    
    for name, addr, length, size, var in data_sheet:
        if 'fingerone' in var: finger_idx = 0
        elif 'fingertwo' in var: finger_idx = 1
        elif 'fingerthree' in var: finger_idx = 2
        elif 'fingerfour' in var: finger_idx = 3
        else: finger_idx = None
        
        if finger_idx is not None:
            finger_center_x = finger_base_x + finger_idx * finger_spacing + finger_width / 2
            if 'tip' in var: x, y, w, h = finger_center_x-0.015, finger_base_y+finger_length-0.05, 0.03, 0.03
            elif 'top' in var or 'palm' in var: x, y, w, h = finger_center_x-0.03, finger_base_y+finger_length*0.55 if 'top' in var else finger_base_y+finger_length*0.22, 0.06, 0.12
        elif 'fingerfive' in var:  # Thumb
            thumb_center_x = thumb_x + thumb_width/2
            w = 0.06
            if 'tip' in var: h = thumb_length*0.08; w=thumb_width*0.5; x=thumb_center_x-w/2; y=thumb_y+thumb_length*0.95
            elif 'top' in var: h=0.08; x=thumb_center_x-w/2; y=thumb_y+thumb_length*0.7
            elif 'middle' in var or 'mid' in var: h=0.08; x=thumb_center_x-w/2; y=thumb_y+thumb_length*0.43
            elif 'palm' in var: h=0.10; x=thumb_center_x-w/2; y=thumb_y+thumb_length*0.10
        elif 'palm_touch' in var:
            palm_center_x = (palm_x+palm_width/2)+0.05
            w,h=0.18,0.16; x=(palm_center_x-w/2)-0.05; y=palm_y+0.12
        
        regions[var] = {'bbox': (x, y, w, h), 'size': size, 'name': name}
    return regions

def upsample(data, scale=2):
    return zoom(data, zoom=scale, order=1)

def orient_sensor(var, data):
    if 'finger' in var and 'fingerfive' not in var: return np.flipud(data)
    if 'fingerfive' in var: return np.flipud(data)
    if 'palm_touch' in var: return np.rot90(data, k=1)
    return data

def draw_hand_outline(ax):
    palm = patches.Rectangle((0.23,0.1),0.35,0.3,linewidth=2,edgecolor='black',facecolor='lightgray',alpha=0.2)
    ax.add_patch(palm)
    finger_width, finger_length, finger_spacing, finger_base_x = 0.08,0.4,0.09,0.22
    for i in range(4):
        finger = patches.Rectangle((finger_base_x+i*finger_spacing,0.41),finger_width,finger_length,linewidth=2,edgecolor='black',facecolor='lightgray',alpha=0.2)
        ax.add_patch(finger)
    thumb = patches.Rectangle((0.59,0.20),0.08,0.37,linewidth=2,edgecolor='black',facecolor='lightgray',alpha=0.2)
    ax.add_patch(thumb)

def setup_csv_logging(sensor_regions):
    """Create session folder inside 'data' & CSV writers for each sensor with metadata"""
    timestamp = datetime.datetime.now().strftime("%m_%d_%y_%H%M%S")
    
    # Ensure top-level "data" folder exists
    base_folder = "data"
    os.makedirs(base_folder, exist_ok=True)
    
    # Session folder inside "data"
    session_folder = os.path.join(base_folder, f"inspire_gripper_session_{timestamp}")
    os.makedirs(session_folder, exist_ok=True)
    
    csv_files = {}
    csv_writers = {}
    for var, info in sensor_regions.items():
        filepath = os.path.join(session_folder, f"{var}.csv")
        f = open(filepath, "w", newline='')
        writer = csv.writer(f)
        # write metadata row with shape
        shape_row = ["shape"] + list(info['size'])
        writer.writerow(shape_row)
        csv_files[var] = f
        csv_writers[var] = writer
    return csv_files, csv_writers


def main():
    dds_handler = DDSHandler(sub_touch=True)
    data_sheet = inspire_hand_defaut.data_sheet
    sensor_regions = get_sensor_regions_on_hand()
    
    # CSV logging setup
    csv_files, csv_writers = setup_csv_logging(sensor_regions)
    
    # Colormap
    colors_blue_yellow = [(0,i/127.0,1.0) if i<128 else ((i-128)/127.0,1.0,1.0-(i-128)/127.0) for i in range(256)]
    blue_yellow_cmap = ListedColormap(colors_blue_yellow)
    
    baselines = {}
    smoothed_data = {}
    smoothing_factor = 0.3
    fig, ax = plt.subplots(figsize=(12,10))
    draw_hand_outline(ax)
    
    sensor_images = {}
    for name, addr, length, size, var in data_sheet:
        if var in sensor_regions:
            x,y,w,h = sensor_regions[var]['bbox']
            img_data = np.zeros(size)
            im = ax.imshow(img_data, extent=[x,x+w,y,y+h], origin='lower',
                           cmap=blue_yellow_cmap, alpha=0.8, vmin=0, vmax=100,
                           interpolation='nearest')
            sensor_images[var] = im
    
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title("Inspire Hand Touch Sensor Map", fontsize=16, weight='bold', pad=20)
    sm = plt.cm.ScalarMappable(cmap=blue_yellow_cmap, norm=plt.Normalize(vmin=0,vmax=max_raw_data))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, orientation='horizontal', pad=0.05, fraction=0.05)
    cbar.set_label(f'Touch Sensor Value (0-{max_raw_data})', fontsize=12)
    cbar.locator = MultipleLocator(max_raw_data/10)
    cbar.update_ticks()
    plt.tight_layout(); plt.ion(); plt.show()
    
    try:
        print_counter = 0
        while plt.fignum_exists(fig.number):
            data_dict = dds_handler.read()
            touch_data = data_dict.get('touch', {})
            
            for name, addr, length, size, var in data_sheet:
                if var in touch_data and var in sensor_images:
                    sensor_matrix = touch_data[var]
                    if sensor_matrix is None or sensor_matrix.size==0: continue
                    if sensor_matrix.shape != size:
                        try: sensor_matrix = sensor_matrix.reshape(size)
                        except: continue
                    if var not in baselines: baselines[var]=sensor_matrix.copy(); smoothed_data[var]=sensor_matrix.copy()
                    relative_data = np.clip(sensor_matrix - baselines[var],0.0,max_raw_data)
                    smoothed_data[var] = relative_data.copy()
                    
                    display_data = orient_sensor(var, smoothed_data[var])
                    if 'fingerfive' in var and ('mid' in var or 'middle' in var):
                        display_data = upsample(display_data, scale=2)
                    sensor_images[var].set_data(display_data)
                    sensor_images[var].set_clim(0,max_raw_data)
                    
                    # --- CSV logging ---
                    flat_row = display_data.flatten().tolist()
                    csv_writers[var].writerow(flat_row)
            
            if print_counter == 40:
                np.set_printoptions(precision=1, suppress=True)
                for var, data_array in smoothed_data.items():
                    print(f"Sensor: {var}\n{np.transpose(data_array)}\n{'-'*30}")
                print_counter=0
                
            fig.canvas.draw_idle()
            fig.canvas.flush_events()
            print_counter+=1
            time.sleep(0.025)
    except KeyboardInterrupt:
        pass
    finally:
        # Close all CSV files
        for f in csv_files.values():
            f.close()

if __name__ == "__main__":
    main()
