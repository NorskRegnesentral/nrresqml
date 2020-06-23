from setuptools import setup, find_packages


setup(
    name='nrresqml',
    version=open('nrresqml/VERSION.txt').read(),
    description='Package for converting Delft3D output to ResQml',
    author='Norwegian Computing Center',
    packages=find_packages(),
    include_package_data=True,
)
