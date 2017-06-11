from setuptools import setup, find_packages

setup(
    name='ioscodesign',
    version='1.0.0',
    description='codesign tool for iOS package',
    url='https://github.com/oylbin/iOSCodeSign',
    author='oylbin',
    author_email='oylbin@gmail.com',
    license='Apache',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='ios codesign codesigning',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'sh',
        'biplist',
    ],
    entry_points={
        'console_scripts': [
            'ioscodesign=ioscodesign.cmd:main',
        ],
    },
)
