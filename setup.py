from distutils.core import setup

setup(
    name='vcompress',
    author='Evgeniy Malov',
    author_email='evgeniiml@gmail.com',
    version='1.1',
    url='https://github.com/evgenii-malov/vcompress',
    platforms='any',
    packages=['.',],
    requires = ['python (>= 2.7)',],
    license='GPL',
    description="video compressor for mov files",
    keywords = ["compress","mov",]
)