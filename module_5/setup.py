from setuptools import find_packages, setup

setup(
    name="module_5",
    version="1.0.0",
    description="Module 5 Software Assurance and Secure SQL project",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
