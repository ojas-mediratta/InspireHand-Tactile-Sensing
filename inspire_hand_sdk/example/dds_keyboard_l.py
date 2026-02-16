import time
import sys
import numpy as np

from unitree_sdk2py.core.channel import ChannelPublisher, ChannelFactoryInitialize
from inspire_sdkpy import inspire_hand_defaut, inspire_dds

def main():
    # --- Initialization ---
    if len(sys.argv) > 1:
        ChannelFactoryInitialize(0, sys.argv[1])
    else:
        ChannelFactoryInitialize(0)

    # Create publishers
    pubr = ChannelPublisher("rt/inspire_hand/ctrl/r", inspire_dds.inspire_hand_ctrl)
    pubr.Init()
    
    publ = ChannelPublisher("rt/inspire_hand/ctrl/l", inspire_dds.inspire_hand_ctrl)
    publ.Init()

    cmd = inspire_hand_defaut.get_inspire_hand_ctrl()
    cmd.mode = 0b0001 # Set to Angle Control Mode

    # Format: [Pinky, Ring, Middle, Index, Thumb, Rotation] (This order may vary by model)
    poses = {
        '1': [800, 800, 800, 800, 800, 800],  # 1. Open
        '2': [50, 50, 50, 50, 700, 1000],                    # 2. Closed
        '3': [50, 50, 50, 50, 300, 1000],              # 3. Pinch
        '4': [1000, 1000, 1000, 1000, 1000, 1000],         # 4. Rock/Spiderman
        '5': [800, 800, 800, 800, 300, 300],        # 5. Half Grasp
    }

    print("------------------------------------------------")
    print("Interactive Inspire Hand Control")
    print("Press 1-5 to send command.")
    print("Press 'q' to quit.")
    print("------------------------------------------------")

    while True:
        # This blocks the code until you type and hit enter
        user_input = input("Enter Pose (1-5): ").strip().lower()

        if user_input == 'q':
            break

        if user_input in poses:
            target_angles = poses[user_input]
            cmd.angle_set = target_angles
            
            print(f"Sending Pose {user_input}: {target_angles}")

            for _ in range(5):
                publ.Write(cmd)
                time.sleep(0.01) 
        else:
            print("Invalid selection. Try 1, 2, 3, 4, or 5.")

    print("Done.")

if __name__ == '__main__':
    main()
