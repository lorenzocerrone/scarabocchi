import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.colors import hsv_to_rgb
from skimage.filters import rank
from skimage.morphology import watershed, disk
from skimage.color import rgb2gray
import numpy as np


class Annotation:
    """
    Object containing all attributes for each image segment
    """
    def __init__(self, idx):
        # Lists containing scribbles coordinates
        self.xdata = []
        self.ydata = []

        # Lists of pixels belonging to the object
        self.xsegdata = []
        self.ysegdata = []

        # Labels unique id
        self.labelsidx = idx

        # Colors for plotting
        h = np.random.rand()
        self._color = hsv_to_rgb(np.array([h, 0.9, 0.5]))
        self._color_highlighted = hsv_to_rgb(np.array([h, 1, 0.99]))

        # Parameters for nice lines plotting
        self._xdata_tmp = []
        self._ydata_tmp = []
        self._lines_id = []
        self._legend_exists = False
        self._is_active = False


class Annotator:
    """
    This object congaing all annotation and handle all the interactions callbacks
    """
    def __init__(self, axes, img):
        # Init axes and input image
        self.axes = axes

        if img.ndim == 3 and img.shape[-1] == 3:
            self.img = rgb2gray(img)
        elif img.ndim == 2:
            self.img = img
        else:
            raise TypeError("Invalid dimensions for image")

        # Init default label
        self.label_state = '1'
        self.labels = {self.label_state: Annotation(1)}

        self._state_annotate = False
        self._count_reset = 0
        self._count_lines = 0

        # Scribbles summary mask
        self.mask = np.zeros(self.img.shape, dtype=np.int)

    def update_segmentation(self):
        """
        return: 2D array with same dimension (x, y) as input image.

        !!! Implemented is a simple watershed, override for custom algorithm !!!
        """
        gradient = rank.gradient(self.img, disk(2))
        return watershed(gradient, self.mask)

    def mouse_move(self, event):
        # Handling mouse movement interactions
        if not self._state_annotate or not event.inaxes:
            # Need mouse click to get activated and mouse on figure
            return

        # Register movement
        x, y = event.xdata, event.ydata

        # Update scribbles
        self.labels[self.label_state]._xdata_tmp.append(x)
        self.labels[self.label_state]._ydata_tmp.append(y)

        # Draw lines
        line = Line2D(self.labels[self.label_state]._xdata_tmp,
                      self.labels[self.label_state]._ydata_tmp)

        line.set_color(self.labels[self.label_state]._color_highlighted)
        self.axes.add_line(line)
        self.labels[self.label_state]._lines_id.append(self._count_lines)
        self._count_lines += 1
        plt.draw()

        # Update mask
        self.mask[int(y), int(x)] = self.labels[self.label_state].labelsidx

        # Highlights selected label
        self.labels[self.label_state]._is_active = True

    def mouse_click(self, event):
        # Wait for mouse movement
        self._state_annotate = True

    def mouse_release(self, event):
        # Erase x and y data for new line

        # Temporary labels are needed to draw tightly lines, merge with
        self.labels[self.label_state].xdata += self.labels[self.label_state]._xdata_tmp
        self.labels[self.label_state].ydata += self.labels[self.label_state]._ydata_tmp

        self.labels[self.label_state]._xdata_tmp = []
        self.labels[self.label_state]._ydata_tmp = []

        # deactivate mouse movement
        self._state_annotate = False

        # create legend if none for new labels
        self._create_legend_lines()

        # recompute and draw segmentation
        self._draw_segmentation(recompute=True)

    def key_press_event(self, event):
        if event.key.isdigit() and event.key != '0':
            self._new_annotation(event.key)

        elif event.key == 'r':
            self._reset_label()

        elif event.key == "up":
            self._new_annotation(str(int(self.label_state) + 1))

        elif event.key == "down":
            self._new_annotation(str(int(self.label_state) - 1))

        elif event.key == "t":
            self._new_random_colors()

    def _new_random_colors(self):
        # initialize new random colors
        for label in self.labels.values():
            h = np.random.rand()
            label._color = hsv_to_rgb(np.array([h, 0.9, 0.5]))
            label._color_highlighted = hsv_to_rgb(np.array([h, 1, 0.99]))

            for line in label._lines_id:
                self.axes.lines[line].set_color(label._color_highlighted)
        plt.legend()
        plt.draw()
        self._draw_segmentation(recompute=False)

    def _new_annotation(self, state):
        # Create a new annotation object
        if int(state) > 1:
            self.label_state = state
            if self.label_state not in self.labels:
                self.labels[self.label_state] = Annotation(int(state))

    def _draw_segmentation(self, recompute=True):
        # create segmentation rgb image in axes
        if recompute:
            self.seg = self.update_segmentation()

        rgb_seg = np.zeros((self.seg.shape[0], self.seg.shape[1], 3))
        for idx in sorted(self.labels.keys()):
            if self.labels[idx]._is_active:
                segx, segy = np.where(self.seg == int(idx))
                if self.label_state == idx:
                    rgb_seg[segx, segy] = self.labels[idx]._color_highlighted
                else:
                    rgb_seg[segx, segy] = self.labels[idx]._color
                self.labels[idx].xsegdata, self.labels[idx].ysegdata = segx, segy

        self.axes.images = [self.axes.images[0]]
        # Modify alpha to change overlay strength
        self.axes.imshow(rgb_seg,
                         origin='upper',
                         alpha=0.4)
        plt.draw()

    def _create_legend_lines(self):
        # draw legend
        if not self.labels[self.label_state]._legend_exists:
            # add place older line with leg
            legendline = Line2D([0], [0], label=self.labels[self.label_state].labelsidx)
            legendline.set_color(self.labels[self.label_state]._color_highlighted)
            self.axes.add_line(legendline)
            plt.legend()

            self.labels[self.label_state]._lines_id.append(self._count_lines)
            self._count_lines += 1

            self.labels[self.label_state]._legend_exists = True

    def _reset_label(self):
        # Completely delete current label and clean the plot

        # Remove label from mask
        self.mask = np.where(self.mask == int(self.labels[self.label_state].labelsidx), 0, self.mask)

        # Remove lines
        for line in self.labels[self.label_state]._lines_id:
            self.axes.lines[line] = Line2D([0], [0])
        plt.legend()
        plt.draw()

        # Create clean label with same colors
        color = self.labels[self.label_state]._color
        color_highlighted = self.labels[self.label_state]._color_highlighted
        del self.labels[self.label_state]
        self.labels[self.label_state] = Annotation(self.label_state)
        self.labels[self.label_state]._color = color
        self.labels[self.label_state]._color_highlighted = color_highlighted

        # Deactivate and recompute segmentation
        self.labels[self.label_state]._is_active = False
        self._draw_segmentation(recompute=True)
