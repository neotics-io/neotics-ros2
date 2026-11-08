import sys
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT))

from neotics_scene import Scene  # noqa: E402
from scene_to_urdf import to_urdf  # noqa: E402


@pytest.fixture
def scene():
    return Scene.load(KIT / "samples" / "depot.scene.json")


def test_urdf_is_one_unbroken_chain_from_world_to_tool(scene):
    robot = ET.fromstring(to_urdf(scene))
    child_of = {j.find("child").get("link"): j.find("parent").get("link") for j in robot.findall("joint")}
    chain, here = ["tool"], "tool"
    while here in child_of:
        here = child_of[here]
        chain.append(here)
    assert chain[-1] == "world" and len(chain) == len(scene.links) + 2


def test_every_joint_keeps_its_limits(scene):
    robot = ET.fromstring(to_urdf(scene))
    joints = {j.get("name"): j for j in robot.findall("joint") if j.get("type") == "revolute"}
    assert list(joints) == scene.joint_names
    for link in scene.links:
        limit = joints[link.joint].find("limit")
        assert float(limit.get("lower")) == link.lower and float(limit.get("upper")) == link.upper


def test_base_sits_where_the_scene_says(scene):
    first = ET.fromstring(to_urdf(scene)).find("joint")
    assert [float(v) for v in first.find("origin").get("xyz").split()] == list(scene.base)
