from astroquery.simbad import Simbad
import csv
import chardet
import math

import os
import inspect

import re
import numpy as np

# Add author's name
author_name = "Hervé Le Coroller"

# Obtient le chemin absolu du répertoire du script cat_sophie.py
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construit le chemin absolu du fichier masks.csv
masks_file_path = os.path.join(script_dir, "masks.csv")


def detect_encoding(star_list_file):
    with open(star_list_file, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
    return encoding

def get_obs_info(star_list_file):
    obs_info = []

    encoding = detect_encoding(star_list_file)

    with open(star_list_file, 'r', encoding=encoding) as csv_file:
        reader = csv.DictReader(csv_file, delimiter=';')
        for row in reader:
            obs_info.append(row)

    return obs_info

def format_ra(ra):
    ra_parts = ra.split(' ')
    hours = ra_parts[0].zfill(2)
    minutes = ra_parts[1].zfill(2)
    seconds = float(ra_parts[2])
    seconds = round(seconds, 2)
    return f"{hours}:{minutes}:{seconds:05.2f}"

def format_dec(dec):
    dec_parts = dec.split(' ')
    hours = dec_parts[0].zfill(2)
    minutes = dec_parts[1].zfill(2)
    seconds = float(dec_parts[2])
    seconds = round(seconds, 2)
    return f"{hours}:{minutes}:{seconds:05.2f}"

def find_type_spectral(spectr):
    with open(masks_file_path, "r") as file:
        masks = {}
        for line in file:
            line = line.strip()
            if line:
                spectral_type, masked_type = line.split(";")
                masks[spectral_type] = masked_type

        if spectr in masks:
            return masks[spectr]
        else:
            return None


def get_star_info(star_name):
    # Requête vers SIMBAD pour obtenir les informations de l'étoile
    custom_simbad = Simbad()
    custom_simbad.add_votable_fields('flux(V)', 'flux(B)', 'rv_value', 'sp', 'pmra', 'pmdec')
    result_table = custom_simbad.query_object(star_name)

    if result_table is None:
        return None

    # Extraction des informations

    ra = format_ra(result_table['RA'][0])
    dec = format_dec(result_table['DEC'][0])

    if np.ma.is_masked(result_table['FLUX_V'][0]) and result_table['FLUX_V'][0].mask:
        v_mag = np.nan
        print(f"Warning: no magnitude B in Simbad for star {star_name} \n"
              f"YOU HAVE TO PUT A VALUE MANUALLY !!! (Otherwise DRS can crash !) \n")
    else:
        v_mag = round(float(result_table['FLUX_V'][0]), 2)

    if np.ma.is_masked(result_table['FLUX_B'][0]) and result_table['FLUX_B'][0].mask:
        b_mag = np.nan
        print(f"Warning: no magnitude B in Simbad for star {star_name} \n"
              f"YOU HAVE TO PUT A VALUE MANUALLY !!! (Otherwise DRS can crash !) \n")
    else:
        b_mag = round(float(result_table['FLUX_B'][0]), 2)

    b_min_v = b_mag - v_mag

    if math.isnan(b_min_v):
        b_min_v = 999.9
        print(f"Warning: B-V can t be computed for star {star_name}\n"
              f"The DRS default value has been used: 999.9 \n")
    else:
        b_min_v = round(float(b_mag - v_mag), 3)

    if np.ma.is_masked(result_table['RV_VALUE'][0]) and result_table['RV_VALUE'][0].mask:
        radial_velocity = 9999
        print(f"Warning: no radial velocity in Simbad for {star_name}\n"
              f"The DRS default value has been used: 9999 \n")
    else:
        radial_velocity = round(float(result_table['RV_VALUE'][0]), 3)

    if np.ma.is_masked(result_table['SP_TYPE'][0][:2]) and result_table['SP_TYPE'][0][:2].mask:
        spectral_type = "K5"
        print(f"Warning: no spectral type in Simbad for {star_name}\n"
              f"K5 has been used\n")
    else:
        if result_table['SP_TYPE'][0][:2] == "":
            spectral_type = "K5"
            print(f"Warning: no spectral type in Simbad for {star_name}\n"
                  f"K5 has been used\n")
        else:
            spectral_type = result_table['SP_TYPE'][0][:2]

    if np.ma.is_masked(result_table['PMRA'][0]) and result_table['PMRA'][0].mask:
        pm_ra = 0.0
        print(f"Warning: no proper motion in Simbad for {star_name} \n"
              f"pm_ra = 0.0 has been used. It cans affect the DRS RV computation \n")
    else:
        pm_ra = round(float(result_table['PMRA'][0] / 1000.), 6)  # converted in arcsecond

    if np.ma.is_masked(result_table['PMDEC'][0]) and result_table['PMDEC'][0].mask:
        pm_dec = 0.0
        print(f"Warning: no proper motion in Simbad for {star_name} \n"
              f"pm_dec = 0.0 has been used. It cans affect the DRS RV computation \n")
    else:
        pm_dec = round(float(result_table['PMDEC'][0] / 1000.), 6)  # converted in arcsecond

    # Création d'un dictionnaire avec les informations extraites
    star_info = {
        #'coord': coordinates,
        'RA': ra,
        'DEC': dec,
        'V': v_mag,
        'B': b_mag,
        'bv': b_min_v,
        'Radial velocity': radial_velocity,
        'Spectral type': spectral_type,
        'Proper motions (RA)': pm_ra,
        'Proper motions (Dec)': pm_dec
    }
    return star_info

def main():

    star_list_file = 'star_list.csv'
    obs_info = get_obs_info(star_list_file)

    #Creation du fichier de sorti
    cat_filename = obs_info[0]['progid'] + '.cat'
    with open(cat_filename, 'w') as f:
        f.write("name\talpha\tdelta\tmv\tspectr\tsn\ttexp\tbv\tradvel\tst\ttpltype\tmualpha\tmudelta\tequinox\tepoch\tprogid\tpiname\treadmode\tstatus\tremarks\n")
        f.write("----\t-----\t-----\t--\t------\t--\t----\t--\t------\t--\t-------\t-------\t-------\t-------\t-----\t------\t------\t--------\t------\t-------\n")

    # Affichage des informations d'observation
    for obs in obs_info:
        name = obs['name']
        info_simbad = get_star_info(name)
        if info_simbad is not None:
            alpha = info_simbad['RA']
            delta = info_simbad['DEC']
            mv = info_simbad['V']
            spectr = find_type_spectral(info_simbad['Spectral type'])

            try:
                sn = int(obs['sn'])
            except ValueError:
                print(f"ERROR: sn for the star {name} is not an integer !\n"
                      f"STOP generating the catalog")
                raise SystemExit

            try:
                texp = int(obs['texp'])
            except ValueError:
                print(f"ERROR: texp for the star {name} is not an integer !\n"
                      f"STOP generating the catalog")
                raise SystemExit

            bv = info_simbad['bv']
            radvel = info_simbad['Radial velocity']
            st = info_simbad['Spectral type']

            try:
                tpltype = obs['tpltype']
            except:
                print(
                    f"tpltype '{tpltype}' is not specified for star {name} and has been replaced with 'HE_obs_objAB' \n")
                tpltype = "HE_obs_objAB"

            if tpltype == "HE_obs_objAB" or tpltype == "HE_obs_objA" or tpltype == "HE_obs_fpsimult" or tpltype == "HR_obs_objAB" or tpltype == "HR_obs_objA" or tpltype == "HR_obs_fpsimult":
                pass
            elif tpltype.startswith("HR"):
                print(
                    f"tpltype '{tpltype}' is improperly formatted for star {name} and has been replaced with 'HR_obs_fpsimult' \n")
                tpltype = "HR_obs_fpsimult"

            elif tpltype.startswith("HE"):
                print(
                    f"tpltype '{tpltype}' is improperly formatted for star {name} and has been replaced with 'HE_obs_objAB' \n")
                tpltype = "HE_obs_objAB"

            elif not tpltype or tpltype.strip() == "":
                print(f"tpltype is not specified for star {name} and has been replaced with 'HE_obs_objAB' \n")
                tpltype = "HE_obs_objAB"
            else:
                print(
                    f"tpltype '{tpltype}' is not specified for star {name} and has been replaced with 'HE_obs_objAB'\n")
                tpltype = "HE_obs_objAB"

            mualpha = info_simbad['Proper motions (RA)']
            mudelta = info_simbad['Proper motions (Dec)']
            equinox = 2000.0
            epoch = 2000

            try:
                progid = obs['progid']
                if not re.match(r"\d{2}[AB]\.[A-Z]+\.[A-Z]{4}$", progid):
                    raise ValueError
            except (KeyError, ValueError):
                print(f"progid for the star {name} is missing or has an incorrect format! Exemple of correcte format: 23A.PNP.LECO \n"
                      f"STOP generating the catalog \n")
                raise SystemExit

            try:
                piname = str(obs['piname'])
                piname = piname.replace(" ", "")
                if piname == "":
                    print(f"ERROR: piname column of star line {name} is empty !\n"
                    f"STOP generating the catalog \n")
                    raise SystemExit
            except (KeyError, TypeError):
                print(f"Format name is not correct at star line {name}\n"
                      f"STOP generating the catalog \n")
                raise SystemExit

            try:
                readmode = obs['readmode']
                if readmode == 'fast' or readmode == 'slow':
                    pass
                elif not readmode or readmode.strip() not in ['fast', 'slow']:
                    if float(obs['sn']) < 20:
                        readmode = 'slow'
                    else:
                        readmode = 'fast'
                    print(f"readmode is improperly formatted for star {name} and has been replaced with {readmode} \n")
            except KeyError:
                if float(obs['sn']) < 20:
                    readmode = 'slow'
                else:
                    readmode = 'fast'
                print(f"readmode is improperly formatted for star {name} and has been replaced with {readmode} \n")


            try:
                status = str(obs['status']).lower()
                if status not in ["public", "protected", "extended"]:
                    status = "protected"
            except KeyError:
                status = "protected"
                print(f"status at line {name} is not correctly formatted ! Put at protected \n")

            try:
                remarks = obs['remarks']
            except KeyError:
                remarks = ""

            # Écriture des valeurs dans le fichier
            with open(cat_filename, 'a') as f:
                f.write(
                    f"{name}\t{alpha}\t{delta}\t{mv}\t{spectr}\t{sn}\t{texp}\t{bv}\t{radvel}\t{st}\t{tpltype}\t{mualpha}\t{mudelta}\t{equinox}\t{epoch}\t{progid}\t{piname}\t{readmode}\t{status}\t{remarks}\n")
        else:
            print(f"The star {name} has not been found in simbad ! \n")


if __name__ == '__main__':
    main()
