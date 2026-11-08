from setuptools import setup

setup(
    name="neotics_replay",
    version="0.1.0",
    packages=["neotics_replay"],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/neotics_replay"]),
        ("share/neotics_replay", ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Neotics",
    maintainer_email="neotics.lab@gmail.com",
    description="Plays a Neotics Episode on ROS 2 topics.",
    license="Proprietary",
    entry_points={"console_scripts": ["replay = neotics_replay.replay:main"]},
)
