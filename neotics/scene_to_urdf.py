"""Turn the arm in a Neotics Scene into a URDF robot.    python scene_to_urdf.py samples/depot.scene.json arm.urdf"""
import sys
from xml.etree import ElementTree as ET

from neotics_scene import Scene


def vec(values) -> str:
    return " ".join(f"{v:.6g}" for v in values)


def link_name(joint: str) -> str:
    return f"{joint}_link"


def _shape(parent, tag, link):
    node = ET.SubElement(parent, tag)
    ET.SubElement(node, "origin", xyz=vec((0, 0, link.length / 2)), rpy="0 0 0")
    geometry = ET.SubElement(node, "geometry")
    ET.SubElement(geometry, "cylinder", radius=f"{link.radius:.6g}", length=f"{link.length:.6g}")


def to_urdf(scene: Scene) -> str:
    robot = ET.Element("robot", name=scene.robot_name)
    ET.SubElement(robot, "link", name="world")
    parent, origin = "world", scene.base
    for link in scene.links:
        name = link_name(link.joint)
        body = ET.SubElement(robot, "link", name=name)
        inertial = ET.SubElement(body, "inertial")
        ET.SubElement(inertial, "origin", xyz=vec((0, 0, link.length / 2)), rpy="0 0 0")
        ET.SubElement(inertial, "mass", value=f"{link.mass:.6g}")
        ixx, iyy, izz = link.inertia
        ET.SubElement(inertial, "inertia", ixx=f"{ixx:.6g}", ixy="0", ixz="0", iyy=f"{iyy:.6g}", iyz="0", izz=f"{izz:.6g}")
        _shape(body, "visual", link)
        _shape(body, "collision", link)
        joint = ET.SubElement(robot, "joint", name=link.joint, type="revolute")
        ET.SubElement(joint, "origin", xyz=vec(origin), rpy="0 0 0")
        ET.SubElement(joint, "parent", link=parent)
        ET.SubElement(joint, "child", link=name)
        ET.SubElement(joint, "axis", xyz=vec(link.axis))
        ET.SubElement(joint, "limit", lower=f"{link.lower:.6g}", upper=f"{link.upper:.6g}", effort="40", velocity="2.5")
        ET.SubElement(joint, "dynamics", damping="0.6")
        parent, origin = name, (0, 0, link.length)
    ET.SubElement(robot, "link", name="tool")
    fixed = ET.SubElement(robot, "joint", name="tool_mount", type="fixed")
    ET.SubElement(fixed, "origin", xyz=vec(origin), rpy="0 0 0")
    ET.SubElement(fixed, "parent", link=parent)
    ET.SubElement(fixed, "child", link="tool")
    ET.indent(robot)
    return ET.tostring(robot, encoding="unicode") + "\n"


if __name__ == "__main__":
    with open(sys.argv[2], "w", encoding="utf-8") as out:
        out.write(to_urdf(Scene.load(sys.argv[1])))
