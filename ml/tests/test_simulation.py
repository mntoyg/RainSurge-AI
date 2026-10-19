import pandas as pd

from ml.simulation import SimulationConfig, generate

CFG = SimulationConfig(days=7, seed=7)


def test_shape_and_columns():
    df = generate(CFG)
    assert df["cell"].nunique() == 37
    assert len(df) == 37 * 7 * 96
    assert {"timestamp", "cell", "rain_mm_h", "demand", "supply"} <= set(df.columns)
    assert (df[["demand", "supply", "rain_mm_h"]] >= 0).all().all()


def test_reproducible():
    pd.testing.assert_frame_equal(generate(CFG), generate(CFG))


def test_different_seed_differs():
    other = generate(SimulationConfig(days=7, seed=8))
    assert not generate(CFG)["demand"].equals(other["demand"])


def test_rain_raises_demand_and_lowers_supply():
    df = generate(SimulationConfig(days=21, seed=3))
    wet = df[df["rain_mm_h"] > 5]
    dry = df[df["rain_mm_h"] == 0]
    assert len(wet) > 0
    ratio_wet = (wet["demand"] / wet["supply"].clip(lower=1)).mean()
    ratio_dry = (dry["demand"] / dry["supply"].clip(lower=1)).mean()
    assert ratio_wet > ratio_dry
