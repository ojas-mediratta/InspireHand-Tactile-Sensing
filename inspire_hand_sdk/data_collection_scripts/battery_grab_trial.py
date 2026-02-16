import time
import sys

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

    # Command structure
    cmd = inspire_hand_defaut.get_inspire_hand_ctrl()
    cmd.mode = 0b0001  # Angle Control Mode

    # Define poses
    pose6 = [800, 800, 800, 800, 1000, 100]  # Pre Grab
    pose7 = [200, 200, 200, 200, 700, 100]   # Grab

    # Start in pose 6
    cmd.angle_set = pose6
    for _ in range(5):  # Send multiple times to ensure command is received
        pubr.Write(cmd)
        publ.Write(cmd)
        time.sleep(0.01)
    print("Robot initialized at Pose 6 (Pre Grab).")

    # Wait for user input to start toggling
    user_input = input("Press 'y' to start toggling between Pose 6 and 7: ").strip().lower()
    if user_input != 'y':
        print("Exiting without toggling.")
        return

    # Toggle 10 times
    for i in range(10):
        # Pose 7
        cmd.angle_set = pose7
        for _ in range(5):
            pubr.Write(cmd)
            publ.Write(cmd)
            time.sleep(0.01)
        print(f"Toggled to Pose 7 ({i+1}/10)")
        time.sleep(1.5)

        # Pose 6
        cmd.angle_set = pose6
        for _ in range(5):
            pubr.Write(cmd)
            publ.Write(cmd)
            time.sleep(0.01)
        print(f"Toggled to Pose 6 ({i+1}/10)")
        time.sleep(1.5)

    print("Completed toggling. Hand returned to Pose 6.")

if __name__ == "__main__":
    main()
