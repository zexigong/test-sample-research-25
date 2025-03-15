import pytest
import matplotlib as mpl
import seaborn as sns
from matplotlib import cycler


def test_set():
    """
    Test the top-level set method.
    """
    # This mostly tests that the function doesn't raise errors
    sns.set_theme()


def test_set_context():
    """
    Test the function that sets plot context parameters.
    """
    # Define some set of valid contexts
    contexts = ["paper", "notebook", "talk", "poster"]

    # Iterate through and test that the function works with each
    for context in contexts:
        sns.set_context(context)
        assert mpl.rcParams["axes.labelsize"] == sns.plotting_context(context)["axes.labelsize"]

    # Test using a number to scale the fonts
    sns.set_context("notebook", font_scale=2)
    assert mpl.rcParams["axes.labelsize"] == sns.plotting_context("notebook")["axes.labelsize"] * 2

    # Test temporarily setting the context
    rc = mpl.rcParams["axes.labelsize"]
    with sns.plotting_context("paper"):
        assert rc != mpl.rcParams["axes.labelsize"]
    assert rc == mpl.rcParams["axes.labelsize"]

    # Test temporarily setting the context in a function
    rc = mpl.rcParams["axes.labelsize"]

    @sns.plotting_context("paper")
    def func():
        assert rc != mpl.rcParams["axes.labelsize"]

    func()
    assert rc == mpl.rcParams["axes.labelsize"]

    # Test passing a dictionary
    sns.set_context(rc={"font.size": 10})
    assert mpl.rcParams["font.size"] == 10
    sns.set_context()


def test_set_style():
    """
    Test the function that sets style parameters.
    """
    # Define some set of valid styles
    styles = ["white", "dark", "whitegrid", "darkgrid", "ticks"]

    # Iterate through and test that the function works with each
    for style in styles:
        sns.set_style(style)
        assert mpl.rcParams["axes.facecolor"] == sns.axes_style(style)["axes.facecolor"]

    # Test temporarily setting the style
    rc = mpl.rcParams["axes.facecolor"]
    with sns.axes_style("dark"):
        assert rc != mpl.rcParams["axes.facecolor"]
    assert rc == mpl.rcParams["axes.facecolor"]

    # Test temporarily setting the style in a function
    rc = mpl.rcParams["axes.facecolor"]

    @sns.axes_style("dark")
    def func():
        assert rc != mpl.rcParams["axes.facecolor"]

    func()
    assert rc == mpl.rcParams["axes.facecolor"]

    # Test passing a dictionary
    sns.set_style(rc={"axes.facecolor": "plum"})
    assert mpl.rcParams["axes.facecolor"] == "plum"
    sns.set_style()


def test_set_palette():
    """
    Test the function that sets the color cycle.
    """
    # Define some set of valid palettes
    palettes = ["deep", "muted", "pastel", "dark", "colorblind", "Set2"]

    # Iterate through and test that the function works with each
    for palette in palettes:
        sns.set_palette(palette)
        assert mpl.rcParams["axes.prop_cycle"] == cycler("color", sns.color_palette(palette))

    # Test setting the color codes
    sns.set_palette("deep", color_codes=True)
    assert mpl.colors.colorConverter.colors["b"] == sns.color_palette("deep")[0]

    # Test temporarily setting the palette
    rc = mpl.rcParams["axes.prop_cycle"]
    with sns.color_palette("deep"):
        assert rc != mpl.rcParams["axes.prop_cycle"]
    assert rc == mpl.rcParams["axes.prop_cycle"]

    # Test temporarily setting the palette in a function
    rc = mpl.rcParams["axes.prop_cycle"]

    @sns.color_palette("deep")
    def func():
        assert rc != mpl.rcParams["axes.prop_cycle"]

    func()
    assert rc == mpl.rcParams["axes.prop_cycle"]

    # Test passing a list
    sns.set_palette(["#ff0000", "#00ff00", "#0000ff"])
    assert mpl.rcParams["axes.prop_cycle"] == cycler("color", ["#ff0000", "#00ff00", "#0000ff"])
    sns.set_palette()


def test_reset_defaults():
    """
    Test that resetting to defaults works.
    """
    sns.set_theme()
    sns.reset_defaults()
    assert mpl.rcParams["axes.labelsize"] == mpl.rcParamsDefault["axes.labelsize"]


def test_reset_orig():
    """
    Test that resetting to the original works.
    """
    sns.set_theme()
    sns.reset_orig()
    assert mpl.rcParams["axes.labelsize"] == mpl.rcParamsOrig["axes.labelsize"]