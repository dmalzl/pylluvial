# pyalluvial
A python library for creating alluvial diagrams with an arbitrary number of layers

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

data = pa.generate_test_data()
colors = pa.get_color_list(
    data,
    'timepoint',
    'module',
)
fig, ax = pa.alluvial(
    x = 'timepoint',
    stratum = 'module',
    alluvium = 'nodename',
    colors = colors,
    data = data,
    stratum_width = 2
)

fig.set_figwidth(10)
fig.set_figheight(5)
fig.tight_layout()
```
![](/example/example.png)
