from setuptools import setup, find_packages

setup(
    name='knight-bus',
    version='0.0.2',
    description=(
        'Transport your python objects from one computer to another!'
    ),
    long_description="Knight bus can **safely** and **losslessly** transport "
                     "your python objects from one computer to another.",
    author='loopyme',
    author_email='peter@mail.loopy.tech',
    license='MIT License',
    packages=find_packages(),
    url='https://github.com/loopyme/knight-bus',
    install_requires=[
        'loopyCryptor>=0.1.1',
    ]
)
