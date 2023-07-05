Catalog Generator for the SOPHIE Spectrograph Documentation
===========================================================

This code generates the *.cat file required for the SOPHIE NSTS. It imports the information on the stars directly from SIMBAD.

Requirements
------------

|sophiecat| requires Python>=3.7 (e.g. Anaconda to
get a recent Python if needed).

Required packages:

* `csv`
* `math`
* `os`
* `re`

How to install
--------------

To install |sophiecat| in your Python environment, from the git repository::

    $ git clone https://github.com/hervelam/sophiecat
    $ cd sophiecat
    $ pip install -e .

Quickstart
----------

1. Fill the `star_list.csv` file (see star_list.csv in example directory) with your own stars using Excel or any text editor. 
Make sure to maintain the file format:

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

  Additional columns can be added after the "remarks" column without affecting the catalog generator.

2. Running the Code

Ensure that the directory contains the file: `star_list.csv`. 
Execute the following command in the terminal:

```shell
> sophiecat star_list.csv
```

Authors
-------

* Hervé Le Coroller
