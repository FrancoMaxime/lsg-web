from setuptools import find_packages, setup

setup(
    name='lsg_web',
    version='0.2.a',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ],
)