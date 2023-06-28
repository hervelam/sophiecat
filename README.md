Catalog Generator Module for the SOPHIE Spectrograph
=====================================================

This code generates the *.cat file required for the SOPHIE NSTS. It imports the information on the stars directly from SIMBAD.

Requirements
------------

Required packages:

* `astroquery.simbad`
* `csv`
* `chardet`
* `math`
* `os`
* `re`
* `numpy`

Quick Documentation
-------------------

To use this module, follow the instructions below:

1. Fill the `star_list.csv` file with your own stars using Excel or any text editor. Make sure to maintain the file format.

2. Fill in the following columns for instrumental settings:

   - **texp:** Enter the required exposure time in seconds.
   - **sn:** Enter the required SNR (Signal-to-Noise Ratio)
   - **tpltype:** Choose one of the following options:
     - HE_obs_objAB
     - HE_obs_fpsimult
     - HR_obs_objAB
     - HR_obs_objA
     - HR_obs_fpsimult
   - **progid:** Must be in the format: \d{2}[AB]\.[A-Z]+\.[A-Z]{4} (Example: 23A.PNP.LECO)
   - **piname:** Enter your name without any spaces or special characters.
   - **readmode:** Choose between "fast" (for SNR > 20) or "slow" (only for SNR < 20). If left empty, the readout mode will be automatically chosen based on the sn value.
   - **status:** Choose one of the following options: "public", "protected", or "extended". The default is "protected".
   - **remarks:** You don't need to add a remark, but keep this column in the `star_list` file.

3. Additional columns can be added after the "remarks" column without affecting the catalog generator.

Running the Code
----------------

To run the code, ensure that the directory contains two files: `star_list.csv` and `masks.csv`. Then execute the following command in the terminal:

```shell
> python cat_sophie.py
```

Authors
-------

* Hervé Le Coroller
