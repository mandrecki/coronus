import os

from setuptools import setup, find_packages

with open("requirements.txt") as f:
    tests_require = f.readlines()
install_requires = [t.strip() for t in tests_require]

with open("README.md") as f:
    long_description = f.read()

data_files = []
for (root, _, files) in os.walk('data'):
    data_files.append((root, [os.path.join(root, f) for f in files]))

setup(
    name="coronus_web",
    version="0.9.0",
    description="Predicting development of the virus across the world",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.predictvirus.com",
    author="Marian Andrecki",
    author_email="marian.andrecki@gmail.com",
    license="",
    packages=find_packages(exclude=['doc', 'tests*']),
    package_data={"": ["requirements.txt"], "coronus_web": ['data/*']},
    python_requires=">=3.6",
    install_requires=install_requires,
    zip_safe=False,
)
