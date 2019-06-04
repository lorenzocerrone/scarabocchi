# scarabocchi
Barebone tools for interactive image scribbles on python

# Requirements
- numpy
- matplotlib
- skimage

# Usage 

Run the annotation tools:
```python
from scarabocchi.scarabocchi import scribbles_tools2d
from skimage.data import astronaut

# Simple annotator example
annotator = scribbles_tools2d(img=astronaut(), figsize=(10, 10))
```

 - Paint scribbles by mouse click and move on the image.
 - Use digits or up-down arrows to select new labels.
 - remove scribble with <kbd>r</kbd>.
 - new random color map with <kbd>t</kbd>.
 
 ## Annotator 
 The annotator object contains all labels information:
 
- a label mask with same spatial dimension as the initial image.
 ```python
annotator.mask
```
- a dictionary with all annotation information and pixel-wise segmentation for each object.
 ```python
 # Example for segment "1"
annotation = annotator.labels["1"]

# Scrabbles 
annotation.xdata, annotation.ydata

# Object segmentation
annotation.xsegdata, annotation.ysegdata
```

# Segmentation

Segmentation is performed with a simple seeded watershed,
 for custom segmentation algorithm just override the following method:
 ```python
annotator.update_segmentation() 
```

# Jupyter notebook
To get scarabocchi works on jupyter notebooks to use the following magic commands
 ```python
%matplotlib notebook
```
