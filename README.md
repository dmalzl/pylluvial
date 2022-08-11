# pyalluvial
![python-version](https://img.shields.io/badge/Python-3.9-blue)
![stable-version](https://img.shields.io/badge/version-1.0.2-blue)

A python library for creating alluvial diagrams with an arbitrary number of layers

## Installation
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

## Usage
A minimal usage example would be as follows
```python
import pyalluvial as pa

data = pa.generate_test_data(
    [3, 4, 3, 2]
)

# by default labels are not shown
fig, ax = pa.alluvial(
    x = 'timepoint',
    stratum = 'module',
    alluvium = 'nodename',
    data = data,
    palette = 'husl',
    stratum_gap = 2,
    stratum_width = 2
)

fig.set_figwidth(10)
fig.set_figheight(5)
fig.tight_layout()
```
![](/example/without_labels.png)
```python
# pass show_labels = True to get labelled plots
fig, ax = pa.alluvial(
    x = 'timepoint',
    stratum = 'module',
    alluvium = 'nodename',
    palette = 'husl',
    data = data,
    stratum_gap = 2,
    stratum_width = 2,
    show_labels = True
)

fig.set_figwidth(10)
fig.set_figheight(5)
fig.tight_layout()
```
![](/example/with_labels.png)
```python
# use hue to split strata by a given grouping variable
fig, ax = pa.alluvial(
    x = 'timepoint',
    stratum = 'module',
    alluvium = 'nodename',
    hue = 'signif',
    palette = 'tab20',
    data = data,
    stratum_gap = 2,
    stratum_width = 2,
    show_labels = True
)

fig.set_figwidth(10)
fig.set_figheight(5)
fig.tight_layout()
```
![](/example/with_hue.png)

