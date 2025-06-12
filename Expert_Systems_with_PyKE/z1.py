# -*- coding: utf-8 -*-

# Pokrenuti u Google Colab sa Python 2 runtime:

import sys
import time
import os
import shutil

# --- START PyKE Import Setup ---
PYKE_SOURCE_PATH = "/content/pyke/pyke-1.1.1" # Putanja do PyKE foldera
if PYKE_SOURCE_PATH not in sys.path:
    sys.path.insert(0, PYKE_SOURCE_PATH)
# --- END PyKE Import Setup ---

TEMP_PYKE_DIR_BASE = "/content/temp_pyke_processing_v3"

try:
    from pyke import knowledge_engine, krb_traceback, goal
except ImportError:
    print "GRESKA: PyKE biblioteka nije pronađena."
    print "Proverite Python 2 runtime i PyKE instalaciju/putanju."
    sys.exit(1)
except Exception as e_imp:
    print "GRESKA prilikom importovanja PyKE: %s" % e_imp
    sys.exit(1)

# --- Definicije za Zadatak 1: Porodične relacije ---
FAMILY_KFB_CONTENT = """
son_of(bruce, thomas, norma)
son_of(david, thomas, norma)
daughter_of(linda, thomas, norma)
son_of(peter, bruce, carol)
daughter_of(susan, bruce, carol)
son_of(michael, david, julia)
daughter_of(mary, david, julia)
son_of(george, peter, anna)
daughter_of(emily, susan, john)
"""

FAMILY_KRB_FC_EXAMPLE_CONTENT = """
# -*- coding: utf-8 -*-
# Pravila za porodicne relacije

son_of_to_child_parent
  foreach
    family.son_of($child, $father, $mother)
  assert
    family.child_parent($child, $father, father, son)
    family.child_parent($child, $mother, mother, son)

daughter_of_to_child_parent
  foreach
    family.daughter_of($child, $father, $mother)
  assert
    family.child_parent($child, $father, father, daughter)
    family.child_parent($child, $mother, mother, daughter)

sibling_rule
  foreach
    family.child_parent($person1, $parent, $p_type1, $r_type1)
    family.child_parent($person2, $parent, $p_type2, $r_type2)
    check $person1 != $person2
  assert
    family.sibling($person1, $person2)

brother_is_rule
  foreach
    family.sibling($person1, $person2)
    family.child_parent($person2, $any_parent_of_person2, $any_parent_type, son)
  assert
    family.brother_is($person1, $person2)

sister_is_rule
  foreach
    family.sibling($person1, $person2)
    family.child_parent($person2, $any_parent_of_person2, $any_parent_type, daughter)
  assert
    family.sister_is($person1, $person2)

grandparent_is_rule
  foreach
    family.child_parent($child, $parent, $parent_role_to_child, $child_gender)
    family.child_parent($parent, $grandparent, $grandparent_role_to_parent, $parent_gender)
  assert
    family.grandparent_is($child, $grandparent)
"""

def create_temp_pyke_files(dir_name, kfb_map, krb_map):
    full_path = os.path.join(TEMP_PYKE_DIR_BASE, dir_name)
    if os.path.exists(full_path):
        shutil.rmtree(full_path)
    os.makedirs(full_path)
    for fname, content in kfb_map.items():
        with open(os.path.join(full_path, fname), "w") as f:
            f.write(content) # Python 2 'str' je byte string, trebalo bi da bude ok
    for fname, content in krb_map.items():
        with open(os.path.join(full_path, fname), "w") as f:
            f.write(content) # Sadržaj je već ASCII-fied
    return full_path

def setup_engine_with_temp_files(dir_name, kfb_files_map, krb_files_map, engine_type_msg=""):
    try:
        path_to_rules = create_temp_pyke_files(dir_name, kfb_files_map, krb_files_map)
        eng = knowledge_engine.engine(path_to_rules)
        print "%s engine inicijalizovan koristeći privremene fajlove u: %s" % (engine_type_msg, path_to_rules)
        return eng, path_to_rules
    except Exception as e:
        print "Greška pri inicijalizaciji %s engine-a: %s" % (engine_type_msg, e)
        # krb_traceback.print_exc() # Može biti previše bučno, ali korisno za debug
        return None, None

def run_family_query(engine, rules_to_activate, query_goal_pattern, query_args=None, header=""):
    if not engine:
        print "Engine nije dostupan za query: %s" % header
        return
    if header:
        print "\n--- %s ---" % header
    engine.reset()
    engine.activate(rules_to_activate)
    compiled_goal = goal.compile(query_goal_pattern)
    prove_kwargs = query_args if query_args else {}
    found_count = 0
    try:
        for bindings in engine.prove_n(compiled_goal, **prove_kwargs): # ISPRAVKA OVDE
            if bindings:
                result_str_parts = []
                sorted_keys = sorted(bindings.keys())
                for var_name in sorted_keys:
                    result_str_parts.append("%s: %s" % (var_name, bindings[var_name]))
                print "  Pronađeno: %s" % (", ".join(result_str_parts))
                found_count +=1
        if found_count == 0:
            print "  Nijedna činjenica ne odgovara cilju."
    except Exception as e:
        print "  Greška tokom 'prove': %s" % e
        # krb_traceback.print_exc()

def solve_task1(family_engine):
    print "\n======= ZADATAK 1: Porodične relacije ======="
    if not family_engine:
        print "Family engine nije inicijalizovan. Preskačem Zadatak 1."
        return
    run_family_query(family_engine, 'fc_example', 'family.sibling(david, $neka_osoba)', header="1.1: Sibling od 'david'")
    run_family_query(family_engine, 'fc_example', 'family.brother_is(bruce, david)', header="1.2: Da li je David brat Bruce-u?")
    run_family_query(family_engine, 'fc_example', 'family.sister_is(bruce, linda)', header="1.2: Da li je Linda sestra Bruce-u?")
    run_family_query(family_engine, 'fc_example', 'family.brother_is($osoba, david)', header="1.3: Osobe kojima je 'david' brat")
    run_family_query(family_engine, 'fc_example', 'family.brother_is(linda, $brat_od_linde)', header="1.3 (Alt): Braća od 'linda'")
    run_family_query(family_engine, 'fc_example', 'family.sister_is($osoba, linda)', header="1.4: Osobe kojima je 'linda' sestra")
    run_family_query(family_engine, 'fc_example', 'family.sister_is(bruce, $sestra_od_brucea)', header="1.4 (Alt): Sestre od 'bruce'")
    run_family_query(family_engine, 'fc_example', 'family.sibling(bruce, $sibling_osoba)', header="1.5: Sibling od 'bruce'")
    run_family_query(family_engine, 'fc_example', 'family.sibling(bruce, david)', header="1.6: Da li su 'bruce' i 'david' sibling?")
    run_family_query(family_engine, 'fc_example', 'family.sibling(bruce, peter)', header="1.6: Da li su 'bruce' i 'peter' sibling? (očekivano NE)")
    run_family_query(family_engine, 'fc_example', 'family.grandparent_is(peter, $djed_baka)', header="1.7: Djed/baka od 'peter'")
    run_family_query(family_engine, 'fc_example', 'family.grandparent_is(george, $djed_baka_od_georgea)', header="1.7: Djed/baka od 'george'")

# --- Definicije za Zadatak 2: Ekspertni sistem za vrijeme ---
WEATHER_RULES_KRB_CONTENT = """
# -*- coding: utf-8 -*-
# Pravila za vreme

kabanica_rule
  foreach
    weather.pada_kisa("True")
    weather.puse_vjetar("True")
  assert
    weather.ponijeti(Kabanicu)

kisobran_rule
  foreach
    weather.pada_kisa("True")
    weather.puse_vjetar("False")
  assert
    weather.ponijeti(Kisobran) # ASCII

nista_rule
  foreach
    weather.pada_kisa("False")
    weather.puse_vjetar("False")
  assert
    weather.ponijeti(Nista)    # ASCII
"""

def solve_task2():
    print "\n======= ZADATAK 2: Ekspertni sistem za vreme ======="
    scenarios = [
        {"pada_kisa": True, "puse_vjetar": True, "ocekivano": "Kabanicu"},
        {"pada_kisa": True, "puse_vjetar": False, "ocekivano": "Kisobran"}, # ASCII
        {"pada_kisa": False, "puse_vjetar": False, "ocekivano": "Nista"},   # ASCII
        {"pada_kisa": False, "puse_vjetar": True, "ocekivano": None}
    ]
    for i, scn in enumerate(scenarios):
        print "\n--- Scenario 2.%d: Pada kiša = %s, Puše vjetar = %s ---" % (
            i + 1, scn["pada_kisa"], scn["puse_vjetar"]
        )
        # ISPRAVKA: Koristimo stringove "True" i "False" za .kfb
        current_kfb_content = 'weather.pada_kisa("%s")\nweather.puse_vjetar("%s")\n' % (
            str(scn["pada_kisa"]),  # Python str(True) je "True"
            str(scn["puse_vjetar"]) # Python str(False) je "False"
        )
        weather_kfb_map = {"weather.kfb": current_kfb_content}
        weather_krb_map = {"weather_rules.krb": WEATHER_RULES_KRB_CONTENT}
        current_weather_dir_name = "weather_scenario_%d" % (i+1)
        weather_engine, _ = setup_engine_with_temp_files(
            current_weather_dir_name, weather_kfb_map, weather_krb_map, "Weather"
        )
        if not weather_engine:
            print "  Greška pri inicijalizaciji weather engine-a za scenario."
            continue
        weather_engine.activate('weather_rules')
        compiled_goal = goal.compile('weather.ponijeti($sta)')
        savjet = None
        prove_kwargs = {} # Nema argumenata za vezivanje u ovom cilju
        try:
            bindings = weather_engine.prove_1(compiled_goal, **prove_kwargs)
            if bindings and '$sta' in bindings:
                savjet = bindings['$sta']
        except Exception as e:
            print "  Greška tokom 'prove' za vreme: %s" % e
        if savjet:
            print "  Preporuka: Ponesite %s" % savjet
        else:
            print "  Preporuka: Nije specificirano šta poneti (verovatno Nista)."

if __name__ == "__main__":
    print "Pokretanje PyKE zadataka (Python 2) v3..."
    family_kfb_map = {"family.kfb": FAMILY_KFB_CONTENT}
    family_krb_map = {"fc_example.krb": FAMILY_KRB_FC_EXAMPLE_CONTENT}
    family_engine, _ = setup_engine_with_temp_files(
        "family_relations_rules", family_kfb_map, family_krb_map, "Family"
    )
    solve_task1(family_engine)
    solve_task2()
    print "\nČišćenje privremenih PyKE direktorijuma..."
    if os.path.exists(TEMP_PYKE_DIR_BASE):
        try:
            shutil.rmtree(TEMP_PYKE_DIR_BASE)
            print "Privremeni direktorijum '%s' obrisan." % TEMP_PYKE_DIR_BASE
        except Exception as e_clean:
            print "Greška pri brisanju privremenog direktorijuma '%s': %s" % (TEMP_PYKE_DIR_BASE, e_clean)
    else:
        print "Privremeni direktorijum '%s' nije pronađen za brisanje." % TEMP_PYKE_DIR_BASE
    print "\nSvi zadaci završeni."