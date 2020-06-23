from setuptools import setup, find_packages


setup(
    name='nrresqml',
    version=open('nrresqml/VERSION.txt').read(),
    description='Package for converting Delft3D output to ResQml',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author='Norwegian Computing Center',
    license='GPL-3.0',
    url='https://github.com/NorskRegnesentral/nrresqml',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
