from setuptools import setup, find_packages

setup(
    name='ioscodesign',
    version='1.0.3',
    description='codesign tool for iOS package',
    url='https://github.com/oylbin/iOSCodeSign',
    author='oylbin',
    author_email='oylbin@gmail.com',
    license='Apache Software License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='ios codesign codesigning',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'sh',
    ],
    entry_points={
        'console_scripts': [
            'ioscodesign=ioscodesign.cmd:main',
        ],
    },
)
