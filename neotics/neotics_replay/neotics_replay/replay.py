"""Play a Neotics Episode on /joint_states and share the robot on /robot_description.

    ros2 run neotics_replay replay --ros-args -p episode:=depot.episode.json -p urdf:=arm.urdf
"""
import json
from pathlib import Path

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile
from sensor_msgs.msg import JointState
from std_msgs.msg import String


class Replay(Node):
    def __init__(self):
        super().__init__("neotics_replay")
        self.episode = json.loads(Path(self.declare_parameter("episode", "").value).read_text(encoding="utf-8"))
        self.loop = self.declare_parameter("loop", True).value
        urdf = self.declare_parameter("urdf", "").value
        if urdf:
            latched = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
            self.description = self.create_publisher(String, "robot_description", latched)
            self.description.publish(String(data=Path(urdf).read_text(encoding="utf-8")))
        self.states = self.create_publisher(JointState, "joint_states", 10)
        self.frame = 0
        self.timer = self.create_timer(1.0 / self.episode["rate_hz"], self.tick)

    def tick(self):
        if self.frame >= len(self.episode["time"]):
            if not self.loop:
                self.timer.cancel()
                return
            self.frame = 0
        message = JointState()
        message.header.stamp = self.get_clock().now().to_msg()
        message.name = self.episode["joints"]
        message.position = self.episode["qpos"][self.frame]
        self.states.publish(message)
        self.frame += 1


def main():
    rclpy.init()
    node = Replay()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
