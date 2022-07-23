# pyalluvial
A python library for creating alluvial diagrams

# Installation
Simply clone the repository
```commandline
git clone git@github.com:dmalzl/pyalluvial.git
```
and run the following
```commandline
cd pyalluvial
python setup.py install
```
you should then be able to import the package as usual

# Usage
A minimal usage example would be as follows
```python
import pyalluvial as pa
import seaborn as sns

data = pa.generate_test_data()

```