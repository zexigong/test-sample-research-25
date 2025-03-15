import pytest

import numpy as np
import matplotlib as mpl

from seaborn import palettes as pal

SEABORN_PALETTES = pal.SEABORN_PALETTES.keys()
MPL_QUAL_PALS = pal.MPL_QUAL_PALS.keys()


def test_no_palette():
    """Test default palette."""
    current_palette = pal.color_palette()
    assert current_palette == pal.color_palette("deep")


@pytest.mark.parametrize(
    "name, expected",
    [
        ("deep6", 6),
        ("deep", 10),
        ("husl", 6),
        ("Paired", 12),
        ("Blues", 6),
    ],
)
def test_n_colors_default(name, expected):
    """Test behavior of default number of colors."""
    assert len(pal.color_palette(name)) == expected


@pytest.mark.parametrize(
    "name",
    SEABORN_PALETTES + MPL_QUAL_PALS
)
def test_palette_name(name):
    """Test palettes by name."""
    try:
        pal.color_palette(name, 3)
    except Exception:
        raise AssertionError(f"color_palette failed with {name}")


@pytest.mark.parametrize(
    "name",
    SEABORN_PALETTES + MPL_QUAL_PALS
)
def test_palette_context(name):
    """Test palettes by name in with statement."""
    # Test using palettes in a with statement
    with pal.color_palette(name, 3):
        pass


def test_bad_palette_name():
    with pytest.raises(ValueError):
        pal.color_palette("IAmNotAPalette")


def test_palette_list():
    """Test generating a palette from a list of colors."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    assert pal.color_palette(colors) == colors


def test_palette_generator():
    """Test generating a palette from a cycler."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    assert pal.color_palette(prop_cycle) == colors


def test_palette_other():
    """Test generating a palette from another palette."""
    deep = pal.color_palette("deep")
    assert pal.color_palette(deep) == deep


def test_palette_none():
    """Test that None uses current palette."""
    deep = pal.color_palette("deep")
    assert pal.color_palette(None) == deep


def test_palette_desat():
    """Test color desaturation."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    desat = pal.color_palette(colors, desat=.5)
    for (r, g, b), (dr, dg, db) in zip(colors, desat):
        assert (r, g, b) == pytest.approx((dr * 2 - .5, dg * 2 - .5, db * 2 - .5), abs=1e-2)


def test_hls_palette():
    """Test hls_palette."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    for light in [0.1, 0.5, 0.9]:
        for sat in [0.1, 0.5, 0.9]:
            hls = pal.hls_palette(5, light=light, sat=sat)
            assert hls == pytest.approx(hls)
            for (r, g, b), (hr, hg, hb) in zip(colors, hls):
                assert (r, g, b) == pytest.approx((hr, hg, hb), abs=1e-2)


def test_husl_palette():
    """Test husl_palette."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    for light in [0.1, 0.5, 0.9]:
        for sat in [0.1, 0.5, 0.9]:
            husl = pal.husl_palette(5, l=light, s=sat)
            assert husl == pytest.approx(husl)
            for (r, g, b), (hr, hg, hb) in zip(colors, husl):
                assert (r, g, b) == pytest.approx((hr, hg, hb), abs=1e-2)


@pytest.mark.parametrize("as_cmap", [False, True])
def test_mpl_palette(as_cmap):
    """Test mpl_palette."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    mpl_pals = [
        "Blues", "Greens", "Reds", "Purples", "Oranges", "Greys",
        "BuGn", "BuPu", "GnBu", "OrRd", "PuBu", "PuBuGn", "PuRd",
        "RdPu", "YlGn", "YlGnBu", "YlOrBr", "YlOrRd", "viridis", "magma",
        "cividis", "inferno", "plasma", "twilight", "twilight_shifted",
        "cubehelix", "turbo",
    ]
    for name in mpl_pals:
        palette = pal.mpl_palette(name, 5, as_cmap)
        assert palette == pytest.approx(palette)
        for (r, g, b), (mr, mg, mb) in zip(colors, palette):
            assert (r, g, b) == pytest.approx((mr, mg, mb), abs=1e-2)


@pytest.mark.parametrize("as_cmap", [False, True])
def test_mpl_d_palette(as_cmap):
    """Test mpl_palette with discrete colormaps."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    mpl_d_pals = [
        "Accent", "Dark2", "Paired", "Pastel1", "Pastel2",
        "Set1", "Set2", "Set3",
    ]
    for name in mpl_d_pals:
        palette = pal.mpl_palette(name, 5, as_cmap)
        assert palette == pytest.approx(palette)
        for (r, g, b), (mr, mg, mb) in zip(colors, palette):
            assert (r, g, b) == pytest.approx((mr, mg, mb), abs=1e-2)


def test_mpl_palette_viridis():
    """Test mpl_palette with viridis colormap."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    palette = pal.mpl_palette("viridis", 5)
    assert palette == pytest.approx(palette)
    for (r, g, b), (vr, vg, vb) in zip(colors, palette):
        assert (r, g, b) == pytest.approx((vr, vg, vb), abs=1e-2)


def test_mpl_palette_reverse():
    """Test mpl_palette with reversed colormap."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    palette = pal.mpl_palette("viridis_r", 5)
    assert palette == pytest.approx(palette)
    for (r, g, b), (vr, vg, vb) in zip(colors, palette):
        assert (r, g, b) == pytest.approx((vr, vg, vb), abs=1e-2)


def test_mpl_palette_reverse_discrete():
    """Test mpl_palette with reversed discrete colormap."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    palette = pal.mpl_palette("Set1_r", 5)
    assert palette == pytest.approx(palette)
    for (r, g, b), (vr, vg, vb) in zip(colors, palette):
        assert (r, g, b) == pytest.approx((vr, vg, vb), abs=1e-2)


def test_xkcd_palette():
    """Test xkcd_palette."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    xkcd = pal.xkcd_palette(["windows blue", "amber", "greyish", "faded green", "dusty purple"])
    assert xkcd == pytest.approx(xkcd)
    for (r, g, b), (xr, xg, xb) in zip(colors, xkcd):
        assert (r, g, b) == pytest.approx((xr, xg, xb), abs=1e-2)


def test_crayon_palette():
    """Test crayon_palette."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    crayon = pal.crayon_palette(["Midnight Blue", "Carnation Pink", "Fern", "Tumbleweed", "Goldenrod"])
    assert crayon == pytest.approx(crayon)
    for (r, g, b), (cr, cg, cb) in zip(colors, crayon):
        assert (r, g, b) == pytest.approx((cr, cg, cb), abs=1e-2)


@pytest.mark.parametrize("as_cmap", [False, True])
def test_dark_palette(as_cmap):
    """Test dark_palette."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    for i, color in enumerate(colors):
        dark = pal.dark_palette(color, 5, as_cmap)
        assert dark == pytest.approx(dark)
        for (r, g, b), (dr, dg, db) in zip(colors, dark):
            assert (r, g, b) == pytest.approx((dr, dg, db), abs=1e-2)


@pytest.mark.parametrize("as_cmap", [False, True])
def test_light_palette(as_cmap):
    """Test light_palette."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    for i, color in enumerate(colors):
        light = pal.light_palette(color, 5, as_cmap)
        assert light == pytest.approx(light)
        for (r, g, b), (lr, lg, lb) in zip(colors, light):
            assert (r, g, b) == pytest.approx((lr, lg, lb), abs=1e-2)


def test_diverging_palette():
    """Test diverging_palette."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    for i, color in enumerate(colors):
        div = pal.diverging_palette(250, 30, sep=10, n=5)
        assert div == pytest.approx(div)
        for (r, g, b), (dr, dg, db) in zip(colors, div):
            assert (r, g, b) == pytest.approx((dr, dg, db), abs=1e-2)


def test_blend_palette():
    """Test blend_palette."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    blend = pal.blend_palette(["red", "blue"], 5)
    assert blend == pytest.approx(blend)
    for (r, g, b), (br, bg, bb) in zip(colors, blend):
        assert (r, g, b) == pytest.approx((br, bg, bb), abs=1e-2)


def test_cubehelix_palette():
    """Test cubehelix_palette."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    cubehelix = pal.cubehelix_palette(5, start=2, rot=0, reverse=True)
    assert cubehelix == pytest.approx(cubehelix)
    for (r, g, b), (cr, cg, cb) in zip(colors, cubehelix):
        assert (r, g, b) == pytest.approx((cr, cg, cb), abs=1e-2)


@pytest.mark.parametrize("as_cmap", [False, True])
def test_mpl_palette_as_cmap(as_cmap):
    """Test mpl_palette as cmap."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    mpl_pals = [
        "Blues", "Greens", "Reds", "Purples", "Oranges", "Greys",
        "BuGn", "BuPu", "GnBu", "OrRd", "PuBu", "PuBuGn", "PuRd",
        "RdPu", "YlGn", "YlGnBu", "YlOrBr", "YlOrRd", "viridis", "magma",
        "cividis", "inferno", "plasma", "twilight", "twilight_shifted",
        "cubehelix", "turbo",
    ]
    for name in mpl_pals:
        palette = pal.mpl_palette(name, 5, as_cmap)
        assert palette == pytest.approx(palette)
        for (r, g, b), (mr, mg, mb) in zip(colors, palette):
            assert (r, g, b) == pytest.approx((mr, mg, mb), abs=1e-2)


@pytest.mark.parametrize("as_cmap", [False, True])
def test_dark_palette_as_cmap(as_cmap):
    """Test dark_palette as cmap."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    for i, color in enumerate(colors):
        dark = pal.dark_palette(color, 5, as_cmap)
        assert dark == pytest.approx(dark)
        for (r, g, b), (dr, dg, db) in zip(colors, dark):
            assert (r, g, b) == pytest.approx((dr, dg, db), abs=1e-2)


@pytest.mark.parametrize("as_cmap", [False, True])
def test_light_palette_as_cmap(as_cmap):
    """Test light_palette as cmap."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    for i, color in enumerate(colors):
        light = pal.light_palette(color, 5, as_cmap)
        assert light == pytest.approx(light)
        for (r, g, b), (lr, lg, lb) in zip(colors, light):
            assert (r, g, b) == pytest.approx((lr, lg, lb), abs=1e-2)


@pytest.mark.parametrize("as_cmap", [False, True])
def test_diverging_palette_as_cmap(as_cmap):
    """Test diverging_palette as cmap."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    for i, color in enumerate(colors):
        div = pal.diverging_palette(250, 30, sep=10, n=5, as_cmap=as_cmap)
        assert div == pytest.approx(div)
        for (r, g, b), (dr, dg, db) in zip(colors, div):
            assert (r, g, b) == pytest.approx((dr, dg, db), abs=1e-2)


@pytest.mark.parametrize("as_cmap", [False, True])
def test_blend_palette_as_cmap(as_cmap):
    """Test blend_palette as cmap."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    blend = pal.blend_palette(["red", "blue"], 5, as_cmap=as_cmap)
    assert blend == pytest.approx(blend)
    for (r, g, b), (br, bg, bb) in zip(colors, blend):
        assert (r, g, b) == pytest.approx((br, bg, bb), abs=1e-2)


@pytest.mark.parametrize("as_cmap", [False, True])
def test_cubehelix_palette_as_cmap(as_cmap):
    """Test cubehelix_palette as cmap."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    cubehelix = pal.cubehelix_palette(5, start=2, rot=0, reverse=True, as_cmap=as_cmap)
    assert cubehelix == pytest.approx(cubehelix)
    for (r, g, b), (cr, cg, cb) in zip(colors, cubehelix):
        assert (r, g, b) == pytest.approx((cr, cg, cb), abs=1e-2)


def test_palette_context_manager():
    """Test color_palette as context manager."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    with pal.color_palette("deep"):
        assert pal.color_palette() == pal.color_palette("deep")
    assert pal.color_palette() != pal.color_palette("deep")


def test_palette_context_manager_with_desat():
    """Test color_palette as context manager with desaturation."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    with pal.color_palette("deep", desat=.5):
        assert pal.color_palette() == pal.color_palette("deep", desat=.5)
    assert pal.color_palette() != pal.color_palette("deep")


def test_palette_context_manager_with_cmap():
    """Test color_palette as context manager with cmap."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    with pal.color_palette("deep", as_cmap=True):
        assert pal.color_palette() == pal.color_palette("deep", as_cmap=True)
    assert pal.color_palette() != pal.color_palette("deep")


@pytest.mark.parametrize("as_cmap", [False, True])
def test_xkcd_palette_as_cmap(as_cmap):
    """Test xkcd_palette as cmap."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    xkcd = pal.xkcd_palette(
        ["windows blue", "amber", "greyish", "faded green", "dusty purple"],
        as_cmap=as_cmap,
    )
    assert xkcd == pytest.approx(xkcd)
    for (r, g, b), (xr, xg, xb) in zip(colors, xkcd):
        assert (r, g, b) == pytest.approx((xr, xg, xb), abs=1e-2)


@pytest.mark.parametrize("as_cmap", [False, True])
def test_crayon_palette_as_cmap(as_cmap):
    """Test crayon_palette as cmap."""
    prop_cycle = mpl.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]
    crayon = pal.crayon_palette(
        ["Midnight Blue", "Carnation Pink", "Fern", "Tumbleweed", "Goldenrod"],
        as_cmap=as_cmap,
    )
    assert crayon == pytest.approx(crayon)
    for (r, g, b), (cr, cg, cb) in zip(colors, crayon):
        assert (r, g, b) == pytest.approx((cr, cg, cb), abs=1e-2)