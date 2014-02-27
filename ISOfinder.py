#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""


    Copyright (C) 2013 ITB - CNR

    This file is part of ISOfinder.

    ISOfinder is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ISOfinder is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with ISOfinder.  If not, see <http://www.gnu.org/licenses/>.


Created on Wed Jun 12 16:31:27 2013

@author: Paolo Cozzi <paolo.cozzi@tecnoparco.it>

Main program for Isochore Definition

"""

import os
import csv
import argparse

#Modules for dealing with GC content and graph
import GClib
import GClib.Graphs
import GClib.Utility
import GClib.Elements

#To define ReadReference2006 function
from GClib.Elements import Isochore, CalcClass

parser = argparse.ArgumentParser(description='Find Isochores in sequences')
parser.add_argument('-i', '--infile', type=str, required=True, help="Input Fasta File (even compressed)")
parser.add_argument('-o', '--outfile', type=str, required=False, help="Output isochores CSV file")
parser.add_argument('-g', '--graphfile', type=str, required=False, help="Output graph filename (PNG)")
parser.add_argument('-w', '--windowfile', type=str, required=False, help="Output windows CSV file")
parser.add_argument('-v', '--verbose', action="count", required=False, default=0, help="Verbosity level")
parser.add_argument('--windowgraph', type=str, required=False, help="Output windows Graph file")
parser.add_argument('--draw_legend', action='store_true', help="Draw legend on the right side of the image")
parser.add_argument('--force_overwrite', action='store_true', help="Force overwrite")
parser.add_argument('--sequence_start', type=int, required=False, default=1, help="Start segmentation from this position (1-based coordinates)")
parser.add_argument('--draw_chname', type=str, required=False, default=None, help="Draw chromosome name in figure")
parser.add_argument('--window_size', type=int, required=False, default=GClib.WINDOW_SIZE, help="Set window size in bp (default: '%(default)s')")
args = parser.parse_args()

#debug
#print args

#TODO: Change GAP tolerance
#TODO: Setting sequence start and end
#TODO: Draw window
#TODO: Write GAP CSV file
#TODO: Change isochore class boundaries
#TODO: Switch to Isochore Profile and Isochore Rectangle Boxes
#TODO: Calculating a determined chromosome from a multi fasta file

#A function to read Genome Reasearch 2006 isochore profile. Will override Chromosome.LoadIsochore function
def ReadReference2006(self, filename="Supp_Table_2006.csv", chrom="21"):
    """Read the 2006 reference isochore table and instantiate a Chromosome with
    isochores"""
    
    #debug
    GClib.logger.log(1, "Loading %s reference file. Scan for chromosome %s" %(filename, chrom))
    
    filein = open(filename, "rU")
    csvin = csv.reader(filein)
    
    #resetting isochores
    self.isochores = []
    
    for line in csvin:
        #se la prima colonna coincide con il cromosoma specificato, leggo i dati
        #altrimenti continuo. Devo però agire solo sulle colonne dove ho un cromosoma
        try:
            if line[0] != str(chrom):
                #in questo caso il cromosoma non mi interessa
                continue
        
        except ValueError:
            #in questo caso ho a che fare con una riga vuota o di intestazione
            continue
        
        #le colonne che mi servono sono la [2], [3], [5]. Attenzione alle Mb
        start = int(round(float(line[2]) * 1000000))
        end = int(round(float(line[3]) * 1000000))
        avg_GClevel = round(float(line[5]),6)
        stddev_GClevel = round(float(line[7]),6)
        
        #Instantiating a new isochore
        isochore = Isochore()
        isochore.start = start - 1 #beware to the 1 based coordinate
        isochore.end = end
        isochore.size = end-start
        isochore.Class = CalcClass(avg_GClevel)
        isochore.avg_GClevel = avg_GClevel
        isochore.stddev_GClevel = stddev_GClevel
        
        #adding this isochore to isochore list
        self.isochores += [isochore]
        
    #Closing input file
    filein.close()
    
#Setting my function to Isochore Class
GClib.Elements.Chromosome.LoadIsochores = ReadReference2006

if __name__ == "__main__":
    #To continue work, I need almost one file to write
    if args.outfile == None and args.graphfile == None:
        raise Exception, "You must specify an output isochore file while calling this program, by graphfile or outfile option"
        
    #verify verbosity level
    if args.verbose != GClib.logger.threshold:
        #setting user defined threshold of verbosity
        GClib.logger.threshold = args.verbose
    
    #Chromosome istance will not Dump isochore if file exist. So I can verify this 
    #before reading fasta file. Outfile is a required option
    if args.outfile != None and os.path.exists(args.outfile):
        if args.force_overwrite == False:
            raise Exception, "file %s exists!!!" %(args.outfile)
        else:
            #remove the file before calculation
            os.remove(args.outfile)
    
    #Checking for graph file existance
    if args.graphfile != None and os.path.exists(args.graphfile):
        if args.force_overwrite == False:
            raise Exception, "file %s exists!!!" %(args.graphfile)
        else:
            #remove the file before calculation
            os.remove(args.graphfile)
    
    #Checking for window file existance
    if args.windowfile != None and os.path.exists(args.windowfile):
        if args.force_overwrite == False:
            raise Exception, "file %s exists!!!" %(args.windowfile)
        else:
            #remove the file before calculation
            os.remove(args.windowfile)
        
    #Checking for window graph file existance
    if args.windowgraph != None and os.path.exists(args.windowgraph):
        if args.force_overwrite == False:
            raise Exception, "file %s exists!!!" %(args.windowgraph)
        else:
            #remove the file before calculation
            os.remove(args.windowgraph)
        
    
    #sequence_start can't be negative
    if args.sequence_start <= 0:
        raise Exception, "Sequence start must be 1-based and > 0"
    
    #Internal coordinates are 0-based, not 1-based
    args.sequence_start -= 1
    
    #Open the sequence file
    FastaFile = GClib.Utility.FastaFile(args.infile)
    
    #Seq Record object
    seqRecord = None
    
    #TODO: Deal with more than 1 sequence in input file
    if FastaFile.n_of_sequences == 0:
        raise Exception, "No sequence found"
        
    elif FastaFile.n_of_sequences == 1:
        seqRecord = FastaFile.GetNextSeq()
        
    else:
        raise Exception, "Cannot handle %s sequences" %(FastaFile.n_of_sequences)
        
    #Instantiating Chromosome Class with seqRecord object (gaps are determined automatically)
    Chrom = GClib.Elements.Chromosome(seqRecord)
    
    #Instantiate a Chromosome class for 2006 isochore reference
    Ref2006 = GClib.Elements.Chromosome()
    
    #TODO: define the possibility to specify the chromosome to analyze
    Ref2006.LoadIsochores()
    
    #Segmenting Sequence in windows
    if args.window_size == GClib.WINDOW_SIZE:
        #This call only to print the warning string when we use the default window size
        Chrom.ValueWindows(From=args.sequence_start)
        
    else:
        #Call valuewindos with user defined window size
        Chrom.ValueWindows(window_size=args.window_size, From=args.sequence_start)
    
    #Writing windows in a file (if I need it)
    if args.windowfile != None:
        Chrom.DumpWindows(args.windowfile)
    
    #Writing the window graph file, if is needed
    if args.windowgraph != None:
        #Instantiating DrawChromosome Class. Look at sequence start (0-based sequence start, this has been fixed in the top of this main block)
        Graph = GClib.Graphs.DrawChromosome(sequence_start=args.sequence_start)
        
        #Fixing appropriate values
        Graph.SetSequenceLength(Chrom.size)
        Graph.InitPicture()
        Graph.SetHorizontalLines([37, 41, 46, 53])
        Graph.SetColorsList(colorbyclass=True)
        
        #Draw the correct values
        Graph.DrawWindowRectangles(windows=Chrom.windows)
        
        #Draw legend or not
        if args.draw_legend == True:
            Graph.DrawLegend()
            
        #Draw ChName
        if args.draw_chname != None:
            Graph.DrawChName(args.draw_chname)
        
        #Finishing picture
        Graph.FinishPicture(drawlabels=False)
        Graph.EnlargeLabels()
        Graph.SaveFigure(args.windowgraph)

    #Finding Isochores. This program tries to segmenting genome into isochores, and so this calculation is always done
    Chrom.FindIsochores()
    
    if args.outfile != None:
        #Writing Isochores in file
        Chrom.DumpIsochores(args.outfile)
    
    #Instantiating graph if it is necessary
    if args.graphfile != None:
        #Instantiating DrawChromosome Class. Look at sequence start (0-based sequence start, this has been fixed in the top of this main block)
        Graph = GClib.Graphs.DrawChromosome(sequence_start=args.sequence_start)
        
        #Fixing appropriate values
        Graph.SetSequenceLength(Chrom.size)
        Graph.InitPicture()
        Graph.SetHorizontalLines([37, 41, 46, 53])
        Graph.SetColorsList(colorbyclass=True)
        
        #Draw the correct values
        Graph.DrawIsochoreRectangles(isochores=Chrom.isochores)
        
        #Draw the reference profile
        Graph.DrawIsochoreProfile(isochores=Ref2006.isochores)
        
        #Draw legend or not
        if args.draw_legend == True:
            Graph.DrawLegend()
            
        #Draw ChName
        if args.draw_chname != None:
            Graph.DrawChName(args.draw_chname)
        
        Graph.FinishPicture(drawlabels=False)
        Graph.EnlargeLabels()
        Graph.SaveFigure(args.graphfile)
    
    
