from pathlib import Path

from setuptools import find_packages, setup

BASE_DIR = Path(__file__).resolve().parent
with open(BASE_DIR / "LICENSE") as file:
    _license = file.read()

with open(BASE_DIR / "README.md") as file:
    _description = file.read()

setup(
    name="fasoarzeka",
    version="0.1.0",
    long_description=_description,
    long_description_content_type="text/markdown",
    url="https://github.com/parice02/fasoarzeka",
    description="API non officielle de paiement mobile pour le service FASO ARZEKA au Burkina Faso",
    packages=find_packages(),
    author="Mohamed Zeba",
    author_email="m.zeba@mzeba.dev",
    license=_license,
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    requires=["requests>=2.31.0", "urllib3<1.27,>=1.21.1"],
)
