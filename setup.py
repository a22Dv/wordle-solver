from setuptools import setup, find_packages
setup(
    name='WordleSolver',
    version='1.0.0',
    packages=find_packages(where='data'),
    package_dir={'': 'data'},
    package_data={'WordleSolver': ['words.txt']},
    include_package_data=True,
)