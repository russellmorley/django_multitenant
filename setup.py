
import os

from setuptools import setup


def read(fname):
  with open(os.path.join(os.path.dirname(__file__), fname)) as fp:
    return fp.read()


setup(
  author="Russell Morley",
  author_email="russ@compass-point.net",
  classifiers=[
    "Development Status :: 3 - Alpha",
    "Framework :: Django",
    "License :: OSI Approved :: MIT License",
  ],
  description="Generic sockets server implementation for multitenant sites.",
  install_requires=[
  ],
  keywords="channels sockets django",
  license="MIT",
  long_description=read("README.md"),
  name="django_multitenant_sockets",
  packages=["django_multitenant_sockets"],
  url="https://github.com/russellmorley/django_multitenant",
  version="0.0.1",
)
