"""Full check inside ROS 2: the built package really plays the episode and shares the robot."""
import json
import signal
import subprocess
import sys
import time
from pathlib import Path

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile
from sensor_msgs.msg import JointState
from std_msgs.msg import String

KIT = Path(__file__).resolve().parents[1]
EPISODE = KIT / "samples" / "depot.episode.json"


def main(urdf: str) -> int:
    episode = json.loads(EPISODE.read_text(encoding="utf-8"))
    frames = {tuple(round(q, 4) for q in row) for row in episode["qpos"]}
    player = subprocess.Popen(["ros2", "run", "neotics_replay", "replay", "--ros-args", "-p", f"episode:={EPISODE}", "-p", f"urdf:={urdf}"])
    rclpy.init()
    node = Node("neotics_ci")
    states, descriptions = [], []
    node.create_subscription(JointState, "joint_states", states.append, 10)
    node.create_subscription(String, "robot_description", descriptions.append, QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL))
    deadline = time.monotonic() + 60
    try:
        while time.monotonic() < deadline and (len(states) < 100 or not descriptions):
            rclpy.spin_once(node, timeout_sec=0.2)
    finally:
        player.send_signal(signal.SIGINT)
    if len(states) < 100 or not descriptions:
        print(f"FAIL: {len(states)} joint states, {len(descriptions)} robot descriptions")
        return 1
    wrong_names = [m for m in states if list(m.name) != episode["joints"]]
    unknown = [m for m in states if tuple(round(q, 4) for q in m.position) not in frames]
    print(f"received {len(states)} joint states; wrong names {len(wrong_names)}; frames not in the episode {len(unknown)}")
    return 1 if wrong_names or unknown or "<robot" not in descriptions[0].data else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
