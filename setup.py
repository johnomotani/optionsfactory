import setuptools
import versioneer

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="optionsfactory",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="John Omotani",
    author_email="john.omotani@cantab.net",
    description=(
        "Handles user-provided options with flexible defaults, documentation and "
        "checking"
    ),
    license="OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/boutproject/hypnotoad",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)