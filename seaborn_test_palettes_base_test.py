import pytest
import matplotlib.pyplot as plt
from seaborn.colors import color_palette, hls_palette, husl_palette, mpl_palette
from seaborn.colors import dark_palette, light_palette, diverging_palette
from seaborn.colors import blend_palette, xkcd_palette, crayon_palette
from seaborn.colors import cubehelix_palette, set_color_codes

def test_color_palette():
    palette = color_palette("deep", 10)
    assert len(palette) == 10
    assert isinstance(palette, list)

def test_color_palette_none():
    palette = color_palette(None, 10)
    assert len(palette) == 10
    assert isinstance(palette, list)

def test_hls_palette():
    palette = hls_palette(5)
    assert len(palette) == 5
    assert isinstance(palette, list)

def test_husl_palette():
    palette = husl_palette(5)
    assert len(palette) == 5
    assert isinstance(palette, list)

def test_mpl_palette():
    palette = mpl_palette("Set2", 8)
    assert len(palette) == 8
    assert isinstance(palette, list)

def test_dark_palette():
    palette = dark_palette("purple", 5)
    assert len(palette) == 5
    assert isinstance(palette, list)

def test_light_palette():
    palette = light_palette("purple", 5)
    assert len(palette) == 5
    assert isinstance(palette, list)

def test_diverging_palette():
    palette = diverging_palette(250, 10, n=9)
    assert len(palette) == 9
    assert isinstance(palette, list)

def test_blend_palette():
    colors = ["red", "blue"]
    palette = blend_palette(colors, 6)
    assert len(palette) == 6
    assert isinstance(palette, list)

def test_xkcd_palette():
    colors = ["red", "green", "blue"]
    palette = xkcd_palette(colors)
    assert len(palette) == 3
    assert isinstance(palette, list)

def test_crayon_palette():
    colors = ["Red", "Green", "Blue"]
    palette = crayon_palette(colors)
    assert len(palette) == 3
    assert isinstance(palette, list)

def test_cubehelix_palette():
    palette = cubehelix_palette(8)
    assert len(palette) == 8
    assert isinstance(palette, list)

def test_set_color_codes():
    set_color_codes("deep")
    rc_params = plt.rcParams
    assert rc_params["axes.prop_cycle"].by_key()["color"][0] == "#4C72B0"

def test_set_color_codes_reset():
    set_color_codes("reset")
    rc_params = plt.rcParams
    assert rc_params["axes.prop_cycle"].by_key()["color"][0] == (0., 0., 1.)