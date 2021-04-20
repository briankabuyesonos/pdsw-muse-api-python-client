from setuptools import setup
# try to disable version string normalization
# this import is only needed for creating the museclient package
# should not be required during package install
try:
    import setupnovernormalize
except ImportError:
    pass

with open("README.md", "r") as fh:
    long_description = fh.read()

version = "1.5.0"

setup(
    name='sonos-museclient',
    version=version,
    long_description=long_description,
    description='Muse API client for the Sonos Python test automation framework',
    url='https://github.com/Sonos-Inc/pdsw-muse-api/tree/mainline/muse_platform_api',
    author='SfB-Control (#sfb-pd-control)',
    author_email='sfb-control@sonos.com',
    packages=['sonos_museclient', 'sonos_museclient.muse_helpers'],
    python_requires='>=2.7.12, <3',
    install_requires=["requests>=2.22.0",
                      "Twisted>=12.3.0",
                      "websocket_client>=0.57.0",
                      "retry>=0.9.2",
                      "pyOpenSSL>=19.1.0"],
    classifiers=[
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7'
    ],
)
