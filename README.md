# pylluvial
![pypi](https://img.shields.io/badge/pypi-v1.1.0-blue)
![python-version](https://img.shields.io/badge/Python->=3.9-blue)
![stable-version](https://img.shields.io/badge/version-1.1.0-blue)

A python library for creating alluvial diagrams with an arbitrary number of layers

## Installation
Simply run the following
```commandline
pip install pylluvial
```
or clone the repository 
```commandline
git clone git@github.com:dmalzl/pyalluvial.git
```
and run
```commandline
cd pyluvial
pip install .
```
you should then be able to import the package as usual

## Usage
A minimal usage example would be as follows

```python
import pylluvial as pa

data = pa.generate_test_data(
    [3, 4, 3, 2]
)

# by default labels are not shown
fig, ax = pa.alluvial(
    x='timepoint',
    stratum='module',
    alluvium='nodename',
    data=data,
    palette='husl',
    stratum_gap=2,
    stratum_width=2
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

The color assignment for hue elements using string arguments for palette can be quite cumbersome.
However, you can always pass a dictionary with the colors you want to use to palette instead of a string
```python
tab20_colors = {
    '1_s': '#1F77B5',
    '1_ns': '#B0C6E8',
    '2_s': '#F07E21',
    '2_ns': '#F9BA79',
    '3_s': '#2AA137',
    '3_ns': '#9DCB88',
    '4_s': '#D62828',
    '4_ns': '#F29697'
}
colors = {
    f't{i}': tab20_colors for i in range(4)
}
fig, ax = pa.alluvial(
    x = 'timepoint',
    stratum = 'module',
    alluvium = 'nodename',
    hue = 'signif',
    palette = colors,
    data = data,
    stratum_gap = 2,
    stratum_width = 2,
    show_labels = True
)
```

