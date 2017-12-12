from setuptools import setup

setup(
    name='redq',
    version='0.0.1',
    url='http://github.com/peterfraedrich/redq',
    license='MIT',
    author='Peter Fraedrich',
    author_email='peter.fraedrich@hexapp.net',
    description='A Redis-based message queue library',
    packages=find_packages(),
    platforms='any'
    install_requires=[
        'redis'
    ],
    keywords=[
        'Redis',
        'message',
        'queue',
        'mq',
        'FIFO'
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)