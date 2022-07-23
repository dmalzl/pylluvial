from setuptools import setup

def get_requirements(requirementfile):
    with open(requirementfile, 'r') as reqfile:
        requirements = [
            req.rstrip() for req in reqfile
        ]
    return requirements

install_requires = get_requirements('requirements.txt')
setup(name='pyalluvial',
    version='1.0',
    description='Python package for plotting alluvial diagrams with an arbitrary number of layers',
    url='http://github.com/dmalzl/pyalluvial',
    author='Daniel Malzl',
    author_email='daniel@menchelab.com',
    license='MIT',
    packages=['pyalluvial'],
    install_requires = install_requires,
    zip_safe=False
)