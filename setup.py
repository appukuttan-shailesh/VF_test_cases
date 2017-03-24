try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='VF_test_cases',
    version='0.0.5dev',
    author='Shailesh Appukuttan',
    author_email='shailesh.appukuttan@unic.cnrs-gif.fr',
    packages=['VF_test_cases', 'VF_test_cases.tests'],
    url='https://github.com/appukuttan-shailesh/VF_test_cases',
    license='MIT',
    description='A SciUnit library for data-driven validation of models having layers.',
    long_description="",
    install_requires=['sciunit>=0.1.3.1', 'neuronunit']
)
