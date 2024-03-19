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


## geoFoils
# Paul Dechamps, 2024

import os.path
import sys
import argparse
import numpy as np
import pandas as pd

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='airfoil dat files')
    parser.add_argument('--name', help='geo file name', type=str, default=None)
    args = parser.parse_args()
    if args.name is None:
        name = os.path.split(args.file)[1].split('.')[0]
    else:
        name = args.name
    # Ignore double space when loading the data
    df = pd.read_csv(args.file, sep='\s+', header=None)
    data = np.array(df)
    #data = np.genfromtxt(args.file, delimiter=' ')
    checkAirfoil(data)

    print('Writing GEO file for airfoil: ' + name)
    writeGeo(data, name)

def writeGeo(data, name):
    # create a geo file in a folder named 'output'
    thisdir = os.path.split(os.path.abspath(__file__))[0]
    outputdir = os.path.join(thisdir, 'workspace')
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    outputfile = os.path.join(outputdir, name + '.geo')

    # write the geo file

    with open(outputfile, 'w') as f:
        f.write(f'/* Airfoil {name} */\n')
        f.write('// This file was generated automatically using geoFoils (https://github.com/Paul-Dech/geoFoils)\n')
        f.write('// @author: Paul Dechamps\n\n')
        f.write('// Geometry\n')
        f.write('DefineConstant[ xLgt = { 5.0, Name "Domain length (x-dir)" }  ];\n')
        f.write('DefineConstant[ yLgt = { 5.0, Name "Domain length (y-dir)" }  ];\n')
        f.write('\n')
        f.write('// Mesh\n')
        f.write('DefineConstant[ msF = { 1.0, Name "Farfield mesh size" }  ];\n')
        f.write('DefineConstant[ msTe = { 0.01, Name "Airfoil TE mesh size" }  ];\n')
        f.write('DefineConstant[ msLe = { 0.01, Name "Airfoil LE mesh size" }  ];\n')
        f.write('\n')
        f.write('// Rotation\n')
        f.write('DefineConstant[ xRot = { 0.25, Name "Center of rotation" }  ];\n')
        f.write('DefineConstant[ angle = { 0*Pi/180, Name "Angle of rotation" }  ];\n')
        f.write('Geometry.AutoCoherence = 0; // Needed so that gmsh does not remove duplicate\n')
        f.write('\n')
        ## Airfoil
        f.write('/**************\n Geometry\n **************/\n')
        f.write('Te = 1; // trailing edge\n')
        # Find where the leading edge is 
        f.write(f'Le = {np.where(data[:,0] == 0)[0][0] + 1}; // leading edge\n')
        for i in range(data.shape[0]):
            if i == data.shape[0]-1:
                f.write(f'// Point( {i+1} ) = {{ {data[i,0]}, {data[i,1]}, 0.0, msTe }};\n')
            elif data[i,0] == 0.:
                f.write(f'Point( {i+1} ) = {{ {data[i,0]}, {data[i,1]}, 0.0, msLe }};\n')
            elif data[i,0] == 1.:
                f.write(f'Point( {i+1} ) = {{ {data[i,0]}, {data[i,1]}, 0.0, msTe }};\n')
            else:
                f.write(f'Point( {i+1} ) = {{ {data[i,0]}, {data[i,1]}, 0.0}};\n')
        
        f.write('\n')
        # Spline goes from 1 to the number of the leading edge point in {0,0,0}
        f.write(f'Spline(1) = {{1:{np.where(data[:,0] == 0)[0][0]+1}}}; // upper side\n')
        f.write(f'Spline(2) = {{{np.where(data[:,0] == 0)[0][0]+1}:{data.shape[0]-1}, 1}}; // lower side\n')
        f.write('\n')
        f.write('// Rotation\n')
        f.write('If (angle != 0)\n')
        f.write('   For i In {Te:N:1}\n')
        f.write('       Rotate{{0, 0, 1}, {xRot, 0, 0}, -angle} {Point{i};}\n')
        f.write('   EndFor\n')
        f.write('EndIf\n')
        f.write('\n')
        f.write('// Farfield\n')
        f.write('Point(10001) = {1+xLgt, 0, 0,msF};\n')
        f.write('Point(10002) = {1+xLgt, yLgt, 0,msF};\n')
        f.write('Point(10003) = {-xLgt, yLgt, 0,msF};\n')
        f.write('Point(10004) = {-xLgt, 0, 0,msF};\n')
        f.write('Point(10005) = {-xLgt,-yLgt, 0,msF};\n')
        f.write('Point(10006) = {1+xLgt, -yLgt, 0,msF};\n')
        f.write('\n')
        f.write('Line(10001) = {10001, 10002};\n')
        f.write('Line(10002) = {10002, 10003};\n')
        f.write('Line(10003) = {10003, 10004};\n')
        f.write('Line(10004) = {10004, 10005};\n')
        f.write('Line(10005) = {10005, 10006};\n')
        f.write('Line(10006) = {10006, 10001};\n')
        f.write('\n')
        f.write('// Front and wake\n')
        f.write('Line(10007) = {Le, 10004};\n')
        f.write('Line(10008) = {Te, 10001};\n')
        f.write('\n')
        f.write('// Internal field\n')
        f.write('Line Loop(20001) = {10007, -10003, -10002, -10001, -10008, 1};\n')
        f.write('Line Loop(20002) = {10007, 10004, 10005, 10006, -10008, -2};\n')
        f.write('Plane Surface(30001) = {20001};\n')
        f.write('Plane Surface(30002) = {20002};\n')
        f.write('\n')
        f.write('/************************* \n Mesh Options \n *************************/\n')
        f.write('\n')
        f.write('Mesh.Algorithm = 5; // Delaunay\n')
        f.write('\n')
        f.write('/************************* \n Physical Groups \n *************************/\n')
        f.write('\n')
        f.write('Physical Point("te") = {Te};\n')
        f.write('Physical Line("upstream") = {10003, 10004};\n')
        f.write('Physical Line("farfield") = {10002, 10005};\n')
        f.write('Physical Line("downstream") = {10001};\n')
        f.write('Physical Line("downstream") += {10006};\n')
        f.write('Physical Line("airfoil") = {1};\n')
        f.write('Physical Line("airfoil_") = {2};\n')
        f.write('Physical Line("wake") = {10008};\n')
        f.write('Physical Surface("field") = {30001};\n')
        f.write('Physical Surface("field") += {30002};')
        f.write('\n')

def checkAirfoil(data):
    # Check that the input contains two columns
    if data.shape[1] != 2:
        sys.exit('Error: The input file must contain two columns')
    # Check that the airfoil is in Selig format
    if np.all(data[0,:] != data[-1,:]):
        sys.exit('Error: The airfoil must be in Selig format')
    if not np.any(data[:,0] == 0):
        sys.exit('Error: The airfoil has no point on the leading edge')
    # Check if the trailing edge is sharp
    if data[0,1] != data[-1,1]:
        sys.exit('Error: The airfoil has a blunt trailing edge')

if __name__ == '__main__':
    main()
