#!/usr/bin/env python3
#
#

import glob
import os

from setuptools import setup

from riocore.VERSION import VERSION

scripts = []
packages = ["riocore"]
package_data = {}
for package in packages:
    package_data = {package: ["*"]}
    for folder in glob.glob(f"{package}/*"):
        if os.path.isdir(folder) and folder[-1] != "_":
            package_data[package].append(f"{folder.split('/')[-1]}/*")
            package_data[package].append(f"{folder.split('/')[-1]}/**/*")

for script in glob.glob("bin/*"):
    scripts.append(script)

deps = [pkg for pkg in open("requirements.txt", "r").read().split("\n") if pkg]

setup(
    name="riocore",
    version=VERSION,
    author="Oliver Dippel",
    author_email="o.dippel@gmx.de",
    packages=packages,
    package_data=package_data,
    scripts=scripts,
    url="https://github.com/multigcs/riocore/",
    license="LICENSE",
    description="Realtime-IO for Motion-Control - FPGA/MC generator",
    long_description=open("README.md").read(),
    install_requires=deps,
    include_package_data=True,
)
