
import pandas as pd
import pytest
from snipe_app import find_new_monsters, parse_monster_lines


@pytest.fixture
def paste_data():
    """Dummy paste data for testing"""
    return """🇺🇸 :magikarp: :shiny: :male: (:dsp: in 8 minutes) :I_: 100.00 (15/15/15) :C_: 204 :L_: 26 :ms_: Splash / Struggle 40.571750,-112.027377
Only you can see this • Dismiss message
[3:18 AM] 
BOT
 CoordsBot: 🇺🇸 :magikarp: :shiny: :female: (:dsp: in 8 minutes) :I_: 100.00 (15/15/15) :C_: 212 :L_: 27 :ms_: Splash / Struggle 27.899009,-82.734335


🇺🇸 :magikarp: :shiny: :male: (:dsp: in 7 minutes) :I_: 100.00 (15/15/15) :C_: 235 :L_: 30 :ms_: Splash / Struggle 27.917255,-82.302918


🇬🇧 :magikarp: :shiny: :female: (:dsp: in 3 minutes) :I_: 100.00 (15/15/15) :C_: 219 :L_: 28 :ms_: Splash / Struggle 50.757109,-1.860315


🇺🇸 :murkrow: :shiny: :male: (:dsp: in 49 minutes) :I_: 100.00 (15/15/15) :C_: 1361 :L_: 31 :ms_: Feint Attack / Foul Play 27.849096,-82.772172


🇺🇸 :mankey: :shiny: :female: (:dsp: in 49 minutes) :I_: 100.00 (15/15/15) :C_: 732 :L_: 22 :ms_: Scratch / Low Sweep 29.780319,-95.854961


🇺🇸 :cottonee: :shiny: :male: (:dsp: in 49 minutes) :I_: 100.00 (15/15/15) :C_: 340 :L_: 17 :ms_: Razor Leaf / Grass Knot 36.336129,-95.823228


🇺🇸 :pawmi: :female: (:dsp: in 48 minutes) :I_: 100.00 (15/15/15) :C_: 143 :L_: 8 :ms_: Charge Beam / Wild Charge 39.977464,-75.127310


🇺🇸 :charmander: :shiny: :male: (:dsp: in 48 minutes) :I_: 100.00 (15/15/15) :C_: 308 :L_: 11 :ms_: Ember / Flame Charge 34.061464,-118.233886

"""


@pytest.fixture
def old_mons():
    return pd.DataFrame(data={'seconds': [3, 8, 7, 3], 'level': [26, 27, 30, 28], 
                 'lat': [5,6,7,8],
                 'lng': [5,6,7,8],
                 'cp': [204, 212, 235, 219]})

@pytest.fixture
def new_mons():
    return pd.DataFrame(data={'seconds': [1, 2, 3, 4], 'level': [26, 27, 30, 28], 
                 'lat': [1,2,3,4],
                 'lng': [1,2,3,4],
                 'cp': [204, 212, 235, 219]})

@pytest.fixture
def new_and_old_mons():
    return pd.DataFrame(data={'seconds': [1, 2, 3, 4, 3, 8], 
                              'level': [26, 27, 30, 28, 26, 27],
                 'lat': [1,2,3,4,5,6],
                 'lng': [1,2,3,4,5,6],
                 'cp': [204, 212, 235, 219, 204, 212]})


def test_parse_mons(paste_data):
    mons = paste_data
    parsed = parse_monster_lines(mons)
    assert len(parsed) == 9
    assert 'level' in parsed.columns
    assert 'lat' in parsed.columns
    assert 'lng' in parsed.columns
    assert 'seconds' in parsed.columns
    assert 'cp' in parsed.columns
    assert 'type' in parsed.columns
    parsed.apply(
            lambda row: print(
                row["type"],
                row['cp'],
                row["seconds"],
                row["level"],
                row["lat"],
                row["lng"]
            ),
            axis=1,
        )
    
def test_find_new_mons_allnew(new_mons, old_mons):
    new_df = find_new_monsters(new_mons, old_mons)

    assert len(new_df) == 4
    assert 'level' in new_df.columns
    assert 'lat' in new_df.columns
    assert 'lng' in new_df.columns
    assert 'seconds' in new_df.columns
    assert 'cp' in new_df.columns

def test_find_new_mons_allold(new_mons, old_mons):
    new_df = find_new_monsters(new_mons, pd.concat([new_mons, old_mons]))

    assert len(new_df) == 0
    assert 'level' in new_df.columns
    assert 'lat' in new_df.columns
    assert 'lng' in new_df.columns
    assert 'seconds' in new_df.columns
    assert 'cp' in new_df.columns

def test_find_new_mons_someold(new_and_old_mons, old_mons):
    new_df = find_new_monsters(new_and_old_mons, old_mons)

    assert len(new_df) == 4
    assert 'level' in new_df.columns
    assert 'lat' in new_df.columns
    assert 'lng' in new_df.columns
    assert 'seconds' in new_df.columns
    assert 'cp' in new_df.columns
