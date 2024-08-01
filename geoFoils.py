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
import gmsh
from foilGenerator import generateAirfoil

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-n', help='4 digits NACA airfoil', type=str)
    group.add_argument('-f', help='airfoil dat files. Ignored if naca airfoil is given', type=str)
    parser.add_argument('--points', help='Number of elements on the airfoil', type=int, default=100)
    parser.add_argument('--name', help='geo file name', type=str, default=None)
    parser.add_argument('--gr', help='Growth ratio', type=bool, default=True)
    args = parser.parse_args()
    
    if args.f:
        if args.name is None:
            name = os.path.split(args.f)[1].split('.')[0]
        else:
            name = args.name
        # Ignore double space when loading the data
        df = pd.read_csv(args.f, sep='\s+', header=None)
        data = np.array(df)
    elif args.n:
        name = 'NACA'+args.n if args.name is None else args.name
        if len(args.n) != 4:
            raise ValueError('The input does not have 4 digits')
        data = generateAirfoil(args.n, args.points)
    else:
        raise ValueError('You must provide either a NACA code or a file')

    gr = args.gr

    checkAirfoil(data)

    print('Writing GEO file for airfoil: ' + name)
    writeGeo(data, name, gr)

    # Open geo file using gmsh api
    gmsh.initialize()
    geo_path = os.path.join(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'workspace/'+name), name + '.geo')
    gmsh.open(geo_path)
    gmsh.fltk.run()
    gmsh.finalize()

def writeGeo(data, name, gr=False):
    # create a geo file in a folder named 'workspace'
    thisdir = os.path.split(os.path.abspath(__file__))[0]
    outputdir = os.path.join(thisdir, 'workspace/'+name)
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    outputfile = os.path.join(outputdir, name + '.geo')

    # write the geo file

    with open(outputfile, 'w') as f:
        f.write(f'/* Airfoil {name} */\n')
        f.write('// This file was generated automatically using geoFoils v1.0 (https://github.com/Paul-Dech/geoFoils)\n')
        f.write('// @date: ' + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')
        f.write('// @author: Paul Dechamps\n\n')
        f.write('// Geometry\n')
        f.write('DefineConstant[ xLgt = { 5.0, Name "Domain length (x-dir)" }  ];\n')
        f.write('DefineConstant[ yLgt = { 5.0, Name "Domain length (y-dir)" }  ];\n')
        f.write('\n')
        f.write('// Mesh\n')
        if gr:
            f.write('DefineConstant[ growthRatio = { 1.5, Name "Growth Ratio" }  ];\n')
        else:
            f.write('DefineConstant[ msF = { 1.0, Name "Farfield mesh size" }  ];\n')
        f.write('DefineConstant[ msTe = { 0.01, Name "Airfoil TE mesh size" }  ];\n')
        f.write('DefineConstant[ msLe = { 0.01, Name "Airfoil LE mesh size" }  ];\n')
        f.write('\n')
        f.write('// Rotation\n')
        f.write('DefineConstant[ xRot = { 0.25, Name "Center of rotation" }  ];\n')
        f.write('DefineConstant[ angle = { 0*Pi/180, Name "Angle of rotation" }  ];\n')
        f.write('Geometry.AutoCoherence = 0; // Needed so that gmsh does not remove duplicate\n')
        f.write('\n')
        if gr:
            f.write('If (growthRatio == 1.0)\n')
            f.write('   msF = msLe;\n')
            f.write('Else\n')
            f.write('   n = Log(1 - (1 - growthRatio) * xLgt / msLe) / Log(growthRatio);\n')
            f.write('   msF = msLe * growthRatio^(n - 1);\n')
            f.write('EndIf\n')
        ## Airfoil
        f.write('\n')
        f.write('/**************\n Geometry\n **************/\n')
        f.write('Te = 1; // trailing edge\n')
        # Find where the leading edge is 
        f.write(f'Le = {np.where(data[:,0] == 0)[0][0] + 1}; // leading edge\n')
        f.write('\n')
        for i in range(data.shape[0]):
            if i == data.shape[0]-1:
                f.write(f'// Point( {i+1} ) = {{ {data[i,0]}, {data[i,1]}, 0.0, msTe }};\n')
            elif data[i,0] == 0.:
                f.write(f'Point( {i+1} ) = {{ {data[i,0]}, {data[i,1]}, 0.0, msLe }};\n')
            elif data[i,0] == np.max(data[:,0]):
                f.write(f'Point( {i+1} ) = {{ {data[i,0]}, {data[i,1]}, 0.0, msTe }};\n')
            else:
                f.write(f'Point( {i+1} ) = {{ {data[i,0]}, {data[i,1]}, 0.0}};\n')
        
        f.write('\n')
        # Spline goes from 1 to the number of the leading edge point in {0,0,0}
        f.write(f'Spline(1) = {{Le:1}}; // upper side\n')
        f.write(f'Spline(2) = {{1, {data.shape[0]-1}:Le}}; // lower side\n')
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
        f.write('Line Loop(20001) = {10008, 10001, 10002, 10003, -10007, 1};\n')
        f.write('Line Loop(20002) = {10007, 10004, 10005, 10006, -10008, 2};\n')
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
        raise RuntimeError('Error: The input file must contain two columns')
    # Check that the airfoil is in Selig format
    if np.all(data[0,:] != data[-1,:]):
        raise RuntimeError('Error: The airfoil must be in Selig format')
    if not np.any(data[:,0] == 0.):
        raise RuntimeError('Error: The airfoil has no point on the leading edge')
    # Check if the trailing edge is sharp
    if data[0,1] != data[-1,1]:
        raise RuntimeError('Error: The airfoil has a blunt trailing edge')
    # Check if leading edge point is not duplicated
    if np.sum(data[:,0] == 0) > 1:
        raise RuntimeError('Error: The leading edge point is duplicated')
    # Check if upper side is before lower side
    if data[-2,1] > data[1,1]:
        #write this warning in yellow
        print('\033[93m' + 'Warning: The airfoil is probably not in selig format.' + '\033[0m')

if __name__ == '__main__':
    main()
