# Neotics kit for ROS 2

This folder is Neotics' own work, added to our copy of [ROS 2](https://github.com/ros2/ros2). It plays a recorded Neotics run on ROS 2 topics and shares the robot's description.

It is one part of the Neotics stack. Every fork in [neotics-io](https://github.com/neotics-io) reads the same two files:

- a **Neotics Scene** (`samples/depot.scene.json`): the room, the obstacles, the arm and the named places;
- a **Neotics Episode** (`samples/depot.episode.json`): a run recorded in MuJoCo, with time, joint positions and commands.

The depot is a sample made for these tools. It is not an entry or an answer for any [Neotics challenge](https://lab.neotics.io).

## Use it

Run from this folder:

```bash
python scene_to_urdf.py samples/depot.scene.json arm.urdf
colcon build --base-paths neotics_replay
ros2 run neotics_replay replay --ros-args -p episode:=$PWD/samples/depot.episode.json -p urdf:=$PWD/arm.urdf
```

## How it's checked

Builds the package in ROS 2 Jazzy, plays the sample run and checks every message against the recording. This runs on GitHub in `.github/workflows/neotics.yml`, on every change to this folder.

## Licence

See [`LICENSE`](LICENSE). It covers this folder only.
