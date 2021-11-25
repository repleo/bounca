from typing import List

from setuptools import Command, find_packages, setup
from setuptools.command.install import install as _install
from setuptools.command.sdist import sdist as _sdist

src_dir = "."
packages = find_packages(src_dir)


class FrontendBuilder(Command):
    user_options = []  # type: List[str]
    description = "builds the frontend assets using NPM"

    def run(self):
        self.spawn(["npm", "install"])

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class sdist(_sdist):
    def run(self):
        """
        Runs the frontend command *before* packaging everything.
        """
        self.run_command("frontend")
        _sdist.run(self)


class install(_install):
    def run(self):
        """
        Runs the frontend command *after* installing the python package(s).
        """
        _install.run(self)
        self.run_command("frontend")


cmdclass = {
    "sdist": sdist,
    "install": install,
    "frontend": FrontendBuilder,
}

setup(
    name="bounca",
    version="0.2.0",
    cmdclass=cmdclass,
    entry_points={"console_scripts": ["djadmin = manage:main"]},
    scripts=["manage.py"],
    packages=packages,
    include_package_data=True,
    license="proprietary",
    classifiers=[
        "Private :: Do Not Upload",
        "License :: Other/Proprietary License",
    ],
    zip_safe=False,
)
