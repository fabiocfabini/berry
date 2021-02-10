###################################################################################
# This program finds the problematic cases and makes an interpolation of 
# the wavefunctions or, if not necessary, take decisions about what wfc to use
###################################################################################

# This is to include maths
import numpy as np

# This is to make operations in the shell
import os
import sys
import time

# These are the subroutines and functions
import contatempo
from headerfooter import header,footer
import loaddata as d


def polinomial(npontos,x,y,x0):

  p = np.full((7,7),-1,dtype=complex)
  p[0,:] = y

  for ite in range(1,npontos):
    for alpha in range(npontos-ite):
      m = alpha - ite
      p[ite,alpha] = ((x0 - x[m])*p[ite-1,alpha] + (x[alpha] - x0)*p[ite-1,alpha+1])/(x[alpha] - x[m])

  y0 = p[npontos,0]

  return y0



###################################################################################

if __name__ == '__main__':
  header('INTERPOLATION',time.asctime())

  starttime = time.time()                         # Starts counting time

  if len(sys.argv)!=2:
    print(' ERROR in number of arguments. You probably want to give the last band to be considered.')
    sys.exit("Stop")

  lastband = int(sys.argv[1])

# Reading data needed for the run
  berrypath = str(d.berrypath)
  print(' Path to BERRY files:',berrypath)

  wfcdirectory = str(d.wfcdirectory)
  print(' Directory where the wfc are:',wfcdirectory)
  nkx = d.nkx
  nky = d.nky
  nkz = d.nkz
  print(' Number of k-points in each direction:',nkx,nky,nkz)
  nks = d.nks
  print(' Total number of k-points:',nks)
  
  nr = d.nr
  print(' Total number of points in real space:',nr)
  npr = d.npr
  print(' Number of processors to use',npr)
  
  nbnd = d.nbnd
  print(' Number of bands:',nbnd)
  print()

  neighbors = d.neighbors
  print(' Neighbors loaded')
  
  eigenvalues = d.eigenvalues
  print(' Eigenvalues loaded')
  
  connections = np.load('dp.npy')
  print(' Modulus of direct product loaded')

  print(' Reading files bandsfinal.npy and signalfinal.npy')
  with open('bandsfinal.npy', 'rb') as f:
    bandsfinal = np.load(f)
  f.closed
  with open('signalfinal.npy', 'rb') as f:
    signalfinal = np.load(f)
  f.closed
  


###################################################################################

  print()
  print('**********************')
  print(' Problems not solved')
  kpproblem,bnproblem = np.where(signalfinal == -1)
  print('k-points',kpproblem)
  print('in bands',bnproblem)
  nrinter = 0
  print(' Will make interpolations of the wavefunctions.')
  sys.stdout.flush()
  for i in range(kpproblem.size):
    if bnproblem[i] <= lastband:
      nk0 = kpproblem[i]                    # Choose the first k-point of the list
      nb0 = bnproblem[i]                    # and the problematic band
      xx0 = np.full((7),-1,dtype=int)       # k-points in one direction
      xx1 = np.full((7),-1,dtype=int)       # k-points in another direction
      print(' k = ',nk0,'  band = ',nb0)
      for j in range(4):                    # Find the neigbhors of the k-point to be used 
        nk = neighbors[nk0,j]               # on interpolation
        if nk != -1 and nb0 <= lastband:
          if j == 0:
            xx0[2] = nk
          elif j == 1:
            xx1[2] = nk
          elif j == 2:
            xx0[4] = nk
          elif j == 3:
            xx1[4] = nk
          for jj in range(4):
            nk1 = neighbors[nk,jj]
            if nk1 != -1:
              if j == jj and j == 0:
                xx0[1] = nk1
                nk2 = neighbors[nk1,0]
                if nk2 != -1:
                  xx0[0] = nk2
              elif j == jj and j == 1:
                xx1[1] = nk1
                nk2 = neighbors[nk1,1]
                if nk2 != -1:
                  xx1[0] = nk2
              elif j == jj and j == 2:
                xx0[5] = nk1
                nk2 = neighbors[nk1,2]
                if nk2 != -1:
                  xx0[6] = nk2
              elif j == jj and j == 3:
                xx1[5] = nk1
                nk2 = neighbors[nk1,3]
                if nk2 != -1:
                  xx1[6] = nk2
   

      bx0 = np.full((7),-1,dtype=int)
      bx1 = np.full((7),-1,dtype=int)
   
      # Determine every pair k,b for the wfc used for the interpolation
      bx0 = bandsfinal[xx0,bnproblem[i]]
      bx1 = bandsfinal[xx1,bnproblem[i]]
   
      print('xx0',xx0)
      print('bx0',bx0)
      print('xx1',xx1)
      print('bx1',bx1)
 
 
      # nk0,nb0 - kpoint/machine band to be substituted
      print(' Interpolating ',nk0,nb0)
#      interpol(nk0,nb0,xx0,xx1,bx0,bx1)

      # xx0,xx1,bx0,bx1 - k-points and bands used for the interpolation of nk0, nb0
      print(' K point, band to interpolate:', nk0, nb0)
      psi = np.zeros((7,int(d.nr)),dtype=complex)
      psinewx = np.zeros((int(d.nr)),dtype=complex)
      psinewy = np.zeros((int(d.nr)),dtype=complex)
      x = np.zeros((7),dtype=int)
  
      flag = 0
      # direction x: xx0, bx0
      print(' Direction x')
      npontos = 0
      x0 = 3
      for ii in range(7):                      # Run through a line to fetch the data
        if xx0[ii] > -1 and ii != 3:           # if the k-point is valid and is not the point itself=3
          x[npontos] = ii                      # add to the list of points the order ii
          infile = str(d.wfcdirectory)+'k0'+str(xx0[ii])+'b0'+str(bx0[ii])+'.wfc'
          print(' Reading file: ',infile)
          with open(infile, 'rb') as f:        # Load the wfc from file
            psi[ii,:] = np.load(f)             # puts all wfc in this array
          f.close()
          npontos += 1                         # Count the number of valid k-points for interpolation
  
      if npontos > 1:
        flag += 1
        for i in range(int(d.nr)):             # Runs through all points of the wfc
          y = psi[:,i]                         # Takes the relevant values from all wfc
          psinewx[i] = polinomial(npontos,x,y,x0)   # Call interpolation routine
  
  
      # direction y
      print(' Direction y')
      npontos = 0
      x0 = 3
      for ii in range(7):                      # Run through a line to fetch the data
        if xx1[ii] > -1 and ii != 3:
          x[npontos] = ii
          infile = str(d.wfcdirectory)+'k0'+str(xx1[ii])+'b0'+str(bx1[ii])+'.wfc'
          print(' Reading file: ',infile)
          with open(infile, 'rb') as f:
            psi[ii,:] = np.load(f)
          f.close()
          npontos += 1
  
      if npontos > 1:
        flag += 2
        for i in range(int(d.nr)):
          y = psi[:,i]
          psinewy[i] = polinomial(npontos,x,y,x0)
  
  
      # Save new file
      print()
      outfile = str(d.wfcdirectory)+'k0'+str(nk0)+'b0'+str(nb0)+'.wfc1'
      print(' Writing file: ',outfile)
      with open(outfile, 'wb') as f:
        if flag == 1:
          np.save(f,psinewx)
        elif flag == 2:
          np.save(f,psinewy)
        elif flag == 3:
          psi = (psinewx+psinewy)/2.0
          np.save(f,psi)
      f.close()



      nrinter += 1
  
  #sys.exit("Stop")
  ###################################################################################
  print()
  print(' *** Final Report ***')
  print()
  nrnotattrib = np.full((nbnd),-1,dtype=int)
  sep = ' '
  print(' Bands: gives the original band that belongs to new band (nk,nb)')
  for nb in range(nbnd):
    nk = -1
    nrnotattrib[nb] = np.count_nonzero(bandsfinal[:,nb] == -1)
    print()
    print('  New band '+str(nb)+'      | y  x ->   nr of fails: '+str(nrnotattrib[nb]))
    for j in range(nky):
      lin = ''
      print()
      for i in range(nkx):
        nk = nk + 1
  #      f = bands[nk,nb,sete]
        f = bandsfinal[nk,nb]
        if f < 0:
          lin += sep+sep+str(f)
        elif f>= 0 and f < 10:
          lin += sep+sep+sep+str(f)
        elif f > 9 and f < 100:
          lin += sep+sep+str(f)
        elif f > 99 and f < 1000:
          lin += sep+str(f)
      print(lin)
  print()
  print(' Signaling')
  nrsignal = np.full((nbnd,7),-2,dtype=int)
  for nb in range(nbnd):
    nk = -1
    nrsignal[nb,0] = str(np.count_nonzero(signalfinal[:,nb] == -1))
    nrsignal[nb,1]  = str(np.count_nonzero(signalfinal[:,nb] == 0))
    nrsignal[nb,2]  = str(np.count_nonzero(signalfinal[:,nb] == 1))
    nrsignal[nb,3]  = str(np.count_nonzero(signalfinal[:,nb] == 2))
    nrsignal[nb,4]  = str(np.count_nonzero(signalfinal[:,nb] == 3))
    nrsignal[nb,5]  = str(np.count_nonzero(signalfinal[:,nb] == 4))
    nrsignal[nb,6]  = str(np.count_nonzero(signalfinal[:,nb] == 5))
    print()
    print('     '+str(nb)+'      | y  x ->   -1: '+str(nrsignal[nb,0])+ '     0: '+str(nrsignal[nb,1]))
    for j in range(nky):
      lin = ''
      print()
      for i in range(nkx):
        nk = nk + 1
  #      f = bands[nk,nb,sete]
        f = signalfinal[nk,nb]
        if f < 0:
          lin += sep+sep+str(f)
        elif f>= 0 and f < 10:
          lin += sep+sep+sep+str(f)
        elif f > 9 and nk < 100:
          lin += sep+sep+str(f)
        elif f > 99 and nk < 1000:
          lin += sep+str(f)
      print(lin)

  print()
  print(' Resume of results')
  print()
  print(' nr k-points not attributed to a band')
  print(' Band       nr k-points')
  for nb in range(nbnd):
    print(' ',nb,'         ',nrnotattrib[nb])
  
  print()
  print(' Signaling')
  print(' Band  -1  0  1  2  3  4  5')
  for nb in range(nbnd):
    print('  '+str(nb)+'   '+str(nrsignal[nb,:]))
  
  print()
  
  print(' Bands not usable (not completed)')
  for nb in range(nbnd):
    if nrsignal[nb,1] != 0:
      print('  band ',nb,'  failed attribution of ',nrsignal[nb,1],' k-points')
  
  print()
  print(' Number of bands interpolated: ',nrinter)
  
  print()
  
  
  # Finished
  endtime = time.time()
  
  footer(contatempo.tempo(starttime,endtime))
  
#sys.exit("Stop")
