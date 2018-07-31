# Photo Importer

A Python script for organizing pictures and videos from one or many locations
to another target location structured according to the date when the pictures 
were taken.
Can be used for organizing photos directly from a SD card, a camera or another device.
It creates a folder structure according to dates in which the picture or 
video was taken. 
Import structure is following: _YEAR -> YYYY-MM-DD_ eg. _2017 -> 2017-11-20_.
Videos has to include the information about the date when they were taken in
the file name in format _20YYMMDD_. Valid video names can be: 20201113.mp4 or 
p_20110130-auto.m2ts etc.
Script don't copy files to the date folders without file _.opened_ inside.
This file is created automatically when a new date folder is created. So it
is possible to delete the file in order to ignore the folder from next 
updates.

## Setup

config.ini file has to exist next to the script file: photosImport.py
Three items have to be included in the config file:
* source folders - one or more existing paths with pictures to be organized delimited
by column
* target folder - existing path for newly organized pictures are to be copied
* video types - suffixes of video files which are to be imported 

## Dependecies

Pillow: https://pillow.readthedocs.io/en/latest/
