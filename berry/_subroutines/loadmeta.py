""" This program reads all the data from the datafile.npy file

"""

import numpy as np

with open("datafile.npy", "rb") as fich:
    k0 = np.load(fich)
    nkx = int(np.load(fich))
    nky = int(np.load(fich))
    nkz = int(np.load(fich))
    nks = int(np.load(fich))
    step = float(np.load(fich))
    npr = int(np.load(fich))
    dftdirectory = str(np.load(fich))
    name_scf = str(np.load(fich))
    name_nscf = str(np.load(fich))
    wfcdirectory = str(np.load(fich))
    prefix = str(np.load(fich))
    outdir = str(np.load(fich))
    dftdatafile = str(np.load(fich))
    a1 = np.load(fich)
    a2 = np.load(fich)
    a3 = np.load(fich)
    b1 = np.load(fich)
    b2 = np.load(fich)
    b3 = np.load(fich)
    nr1 = int(np.load(fich))
    nr2 = int(np.load(fich))
    nr3 = int(np.load(fich))
    nr = int(np.load(fich))
    nbnd = int(np.load(fich))
    berrypath = str(np.load(fich))
    rpoint = int(np.load(fich))
    workdir = str(np.load(fich))
    noncolin = str(np.load(fich))
    program = str(np.load(fich))
    lsda = str(np.load(fich))
    nelec = float(np.load(fich))
    prefix = str(np.load(fich))
    wfck2r = str(np.load(fich))
    version = str(np.load(fich))
    refname = str(np.load(fich))
    vb = int(np.load(fich))