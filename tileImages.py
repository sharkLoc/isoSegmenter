#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""


    Copyright (C) 2013-2015 ITB - CNR

    This file is part of isochoreFinder.

    isochoreFinder is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    isochoreFinder is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with isochoreFinder.  If not, see <http://www.gnu.org/licenses/>.


Created on Tue Jun 16 21:27:51 2015

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.org>

A simple program in order to put more image together

"""

import os
import argparse

import GClib
from GClib.Graphs import MoreGraphsError

from PIL import Image

__author__ = "Paolo Cozzi <paolo.cozzi@tecnoparco.org>"

from GClib import __copyright__, __license__, __version__

parser = argparse.ArgumentParser(description='Put more images in the same files')
parser.add_argument('--image_files', metavar='image_file', type=str, nargs='+', help='One or more image to put together')
parser.add_argument('-o', '--output', type=str, required=True, help="Output graph filename (PNG)")
args = parser.parse_args()

#A class instance in order to record useful variables
class Tile():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.image = None
        self.n_of_graphs = 0
        
    def SaveFigure(self, filename, check=True):
        """Save figure to a file. Check file existance"""
        
        if self.image == None:
            #I have no image to save
            raise MoreGraphsError, "No BaseGraph or derivate were added to this class instance"
        
        #checking for file existance
        if os.path.exists(filename) and check == True:
            raise MoreGraphsError, "File %s exists!!!" %(filename)
        
        #Determing if the Image is already drawn in temporary files
        self.image.save(filename)
        
        GClib.logger.log(1, "Image saved in %s" %(filename))
    

if __name__ == "__main__":
    #instantiate a tile class
    tile = Tile()    
    
    #For each image files
    for image_file in args.image_files:
        #Open the image file
        image = Image.open(image_file)
        
        #get current size
        x, y = image.size
        
        if tile.n_of_graphs == 0:
            #read first image for the first time
            tile.image = image
            
        else:
            #create a new temporary image
            tmp_image = Image.new('RGB',(max(x,tile.x),y+tile.y),color=(255,255,255))
            
            #copy the old image in the new temporary image   
            box = (0,0,tile.x, tile.y)
            region = tile.image.crop(box)
            tmp_image.paste(region, box)
            
            #cut the current graph_image. Define a box
            box = (0,0,x,y)
            region = image.crop(box)
        
            #Define a box in which put an image. X will ne 0, by Y will be image heigth
            box = (0,tile.y, x, y+tile.y)
            tmp_image.paste(region, box)
            
            #Set tile image as temporary image
            tile.image = tmp_image
        
        #updating class attributes
        tile.n_of_graphs += 1
        tile.x, tile.y = tile.image.size
        
    #Outside the cicle, save the image
    tile.SaveFigure(args.output)

