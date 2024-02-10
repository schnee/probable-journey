
import pytest
from snipe_app import parse_mons


@pytest.fixture
def paste_data():
    """Dummy paste data for testing"""
    return """🇺🇸 :magikarp: :shiny: :male: (:dsp: in 8 minutes) :I_: 100.00 (15/15/15) :C_: 204 :L_: 26 :ms_: Splash / Struggle 40.571750,-112.027377
Only you can see this • Dismiss message
[3:18 AM] 
BOT
 CoordsBot: 🇺🇸 :magikarp: :shiny: :female: (:dsp: in 8 minutes) :I_: 100.00 (15/15/15) :C_: 212 :L_: 27 :ms_: Splash / Struggle 27.899009,-82.734335


🇺🇸 :magikarp: :shiny: :male: (:dsp: in 7 minutes) :I_: 100.00 (15/15/15) :C_: 235 :L_: 30 :ms_: Splash / Struggle 27.917255,-82.302918


🇬🇧 :magikarp: :shiny: :female: (:dsp: in 3 minutes) :I_: 100.00 (15/15/15) :C_: 219 :L_: 28 :ms_: Splash / Struggle 50.757109,-1.860315"""


def test_parse_mons(paste_data):
    mons = paste_data
    parsed = parse_mons(mons)
    assert len(parsed) == 4
    assert 'level' in parsed.columns
    assert 'lat' in parsed.columns
    assert 'lng' in parsed.columns
    assert 'minutes' in parsed.columns
    parsed.apply(
            lambda row: print(
                row["minutes"],
                row["level"],
                row["lat"],
                row["lng"]
            ),
            axis=1,
        )


