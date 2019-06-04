import matplotlib.pyplot as plt
from scarabocchi.annotator import Annotator


def scribbles_tools2d(img, **kwargs):
    """
    Simple 2D annotation tools, allows to scribble labels over a image.
    The scribbles will interact can interact with any segmentation algorithm.
    just override update_segmentation() method in Annotator.

    inputs:
        - img: must be an  image array (x, y) or rgb array (x, y, 3)
        - subplots additional parameters
    returns: annotator object
    """
    assert (img.ndim == 3 and img.shape[-1] == 3) or img.ndim == 2, "Invalid image dimension. " \
                                                                    "must be an  image array (x, y)" \
                                                                    " or rgb array (x, y, 3)"
    # Plot original image
    fig, axes = plt.subplots(**kwargs)
    axes.imshow(img, origin='upper')
    plt.axis('off')
    plt.gray()

    # Init annotation tools and activate interactions
    annotator = Annotator(axes, img)
    plt.connect('motion_notify_event', annotator.mouse_move)
    plt.connect('button_press_event', annotator.mouse_click)
    plt.connect('button_release_event', annotator.mouse_release)
    plt.connect('key_press_event', annotator.key_press_event)

    # Plot and usage instructions
    axes.plot()
    fig.text(0.5, 0.01, '- Mouse click to start a scrible \n' +
                        '- Change label with digits or <up>/<down> arrows\n' +
                        '- <r> to reset current label, <t> to change random colors', ha='center')

    plt.show()
    return annotator
