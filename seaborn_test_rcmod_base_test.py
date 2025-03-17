import pytest
import matplotlib as mpl
from seaborn.rcmod import set_theme, set, reset_defaults, reset_orig, axes_style, set_style, plotting_context, set_context, set_palette

def test_set_theme():
    set_theme(context="paper", style="white", palette="muted", font="serif", font_scale=0.8, color_codes=False, rc={"axes.facecolor": "gray"})
    assert mpl.rcParams["axes.facecolor"] == "gray"
    assert mpl.rcParams["font.family"] == "serif"

def test_set_alias():
    set(style="darkgrid", palette="bright", font="sans-serif", font_scale=1.2, rc={"axes.edgecolor": "blue"})
    assert mpl.rcParams["axes.edgecolor"] == "blue"
    assert mpl.rcParams["font.family"] == "sans-serif"

def test_reset_defaults():
    reset_defaults()
    for key in mpl.rcParamsDefault:
        assert mpl.rcParams[key] == mpl.rcParamsDefault[key]

def test_reset_orig():
    reset_orig()
    from seaborn import _orig_rc_params
    for key in _orig_rc_params:
        assert mpl.rcParams[key] == _orig_rc_params[key]

def test_axes_style():
    style_obj = axes_style("whitegrid", rc={"axes.labelcolor": "red"})
    assert style_obj["axes.labelcolor"] == "red"

def test_set_style():
    set_style("dark", rc={"grid.color": "black"})
    assert mpl.rcParams["grid.color"] == "black"

def test_plotting_context():
    context_obj = plotting_context("poster", font_scale=1.5)
    assert context_obj["font.size"] == 12 * 2 * 1.5

def test_set_context():
    set_context("talk", font_scale=1.1, rc={"axes.linewidth": 2})
    assert mpl.rcParams["axes.linewidth"] == 2

def test_set_palette():
    set_palette("deep", n_colors=8)
    cyl = mpl.rcParams['axes.prop_cycle']
    assert len(cyl.by_key()['color']) == 8

def test_set_palette_color_codes():
    set_palette("muted", color_codes=True)
    assert mpl.colors.colorConverter.colors["b"] == mpl.colors.colorConverter.to_rgb("#4878D0")