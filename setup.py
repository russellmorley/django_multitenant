import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django_multitenant_sockets",
    version = "0.0.1",
    author = "Russell Morley",
    author_email = "russ@compass-point.net",
    description = ("a generic sockets server implementation for multitenant sites."),
    license = "MIT",
    keywords = "channels sockets django",
    url = "https://github.com/russellmorley/django_multitenant_sockets",
    packages=['django_multichannel_sockets'],
    install_requires=['django>=1.8.14', 'channels>=1.1.3', 'djangorestframework>=3.4.1'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
    ],
)



