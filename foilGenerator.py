#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


## geoFoils NACA 4 digits generator
# Paul Dechamps, 2024

# Note: The airfoil generated will be in selig format with a closed trailing edge

import numpy as np
import pandas as pd
import os
import argparse
from math import atan, cos, sin, floor, pi

def generateAirfoil(naca, n=100, c=1.0):
    print('info: Generating NACA' + naca + ' airfoil', end='...')
    
    # Airfoil parameters
    tau = float(naca[-2:])/100
    epsilon = float(naca[0])/100
    p = int(naca[1])/10

    x_cosine = cosineSpacing(c, n)
    x, y = naca4digitCoord(x_cosine, c, tau, epsilon, p)

    # Write the airfoil in a file
    writeAirfoil(x, y, naca)
    print('done')
    return np.round(np.column_stack((x, y)), 14)
    
def naca4digitCoord(X, c, tau, epsilon, p):
    """Get X and Y-coord of NACA 4-digit associated to a X vector
    """
    T = 10 * tau * c * (
          0.2969 * np.sqrt(X/c) 
        - 0.1260 * (X/c) 
        - 0.3537 * (X/c)**2 
        + 0.2843 * (X/c)**3 
        - 0.1015 * (X/c)**4
    ) # Thickness

    YBar     = np.zeros(len(T))
    dYBar_dx = np.zeros(len(T))
    Y        = np.zeros(len(T))
    xB       = np.zeros(len(T))
    yB       = np.zeros(len(T))

    for i in range(len(X)):
        x = X[i]
        # Camber
        if x/c < p:
            YBar[i]     = ((epsilon * x)/(p**2)) * (2 * p - x/c)
            dYBar_dx[i] = (2 * epsilon)/(p**2) * (p - x/c)
        elif x/c >= p:
            YBar[i]     = (epsilon * (c - x)/((1-p)**2)) * (1 + x/c - 2 * p)
            dYBar_dx[i] = (2 * epsilon)/((1 - p)**2) * (p - x/c)

        # Final x & y coordinates
        if i <= len(X)/2 - 1: 
            # Lower surface
            yB[i] = YBar[i] - 0.5 * T[i] * cos(atan(dYBar_dx[i]))
            xB[i] = X[i]    + 0.5 * T[i] * sin(atan(dYBar_dx[i]))
        else: 
            # Upper surface
            yB[i] = YBar[i] + 0.5 * T[i] * cos(atan(dYBar_dx[i]))
            xB[i] = X[i]    - 0.5 * T[i] * sin(atan(dYBar_dx[i]))
            
    return (np.flip(xB), np.flip(yB))

def cosineSpacing(c, nbPanel):
    """generates x-coord of panels boundaries using cosinus distribution
    numerated from lower TE to lower LE and from upper LE to upper TE
    """
    nbPanelHalf = floor(nbPanel/2) + 1
    zetaHalf = np.linspace(0, pi, nbPanelHalf)
    zeta = np.concatenate((zetaHalf, np.flip(zetaHalf[:-1])), axis=None)
    x = (c/2) * (np.cos(zeta) + 1)
    return x

def writeAirfoil(x, y, name):
    thisdir = os.path.split(os.path.abspath(__file__))[0]
    outputdir = os.path.join(thisdir, 'workspace/'+'NACA'+name)
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    outputfile = os.path.join(outputdir, 'NACA'+name + '.dat')
    with open(outputfile, 'w') as f:
        for i in range(len(x)):
            f.write(f'{x[i]:16.12f} {y[i]:16.12f}\n')

if __name__ == '__main__':
    generateAirfoil()
