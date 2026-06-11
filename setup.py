#!/usr/bin/env python3
#
#

import glob
import os

from setuptools import setup

from riocore.VERSION import VERSION

scripts = []
package_data = {
    "riocore": [
        "kicad-images.json",
        "modifiers.py",
        "halpins.py",
        "checksums.py",
        "files/*",
        "boards/*",
        "boards/*/*",
        "modules/*/*",
        "configs/*/*",
        "plugins/fpga/*/*",
    ],
}
packages = ["riocore"]

for script in glob.glob("bin/*"):
    scripts.append(script)

for folder in ("riocore/plugins/*", "riocore/generator/*", "riocore/gui/*"):
    packages.append(folder.replace("/*", "").replace("/", "."))
    for module in glob.glob(folder):
        if "__" not in module and not module.endswith(".py") and not module.endswith(".md"):
            module_name = module.replace("/", ".")
            packages.append(module_name)
            package_data[module_name] = ["*.c", "*.v", "*.png", "*.md"]

package_data["riocore.plugins.fpga.generator"] = ["*.c", "*.v", "*.png", "*.md"]

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
    description="riocore",
    long_description=open("README.md").read(),
    install_requires=["PyQt5>=5.15", "graphviz>=0.20", "pyqtgraph>=0.13.3"],
    include_package_data=True,
)
