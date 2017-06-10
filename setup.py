from setuptools import setup, find_packages

setup(
    name='iOSCodeSign',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'sh',
        'biplist',
    ],
    entry_points='''
        [console_scripts]
        ioscodesign=ioscodesign.cmd:main
    ''',
)
