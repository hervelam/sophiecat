from setuptools import setup, find_packages

setup(
    name='sophiecat',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'astroquery',
        'chardet',
        'numpy'
    ],
    entry_points={
        'console_scripts': [
            'sophiecat= sophiecat.sophiecat:main'
        ]
    }
)
