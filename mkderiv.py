#!/usr/bin/python
#-*-coding: utf-8-*-
"""
Utility for generating derivative images for the PUDL website.

For safety, this should be run be a user that has read-only access to the source
file system (i.e., source TIFFs).
"""
import os
import logging
import subprocess

## Configuration - Set these ##################################################

# Generic location in the pudl file system - e.g., pudl0001 or pudl0001/4609321 
# DO NOT include a leading slash, e.g., "/pudl0001".
PUDL_LOCATOR = "pudl0002"

# True if we want to replace existing files, otherwise False
OVERWRITE_EXISTING = False

# Location for temporary half-size TIFFs, required for setting color profile.
TMP_DIR = "/tmp"

# Location of source images. "pudlXXXX" directories should be directly inside.
SOURCE_ROOT = "/home/jstroop/workspace/img-deriv-maker/test-images"

# Location of target images. "pudlXXXX" directories and subdirectories will be
# created.  
TARGET_ROOT = "/home/jstroop/workspace/img-deriv-maker/out"

# Recipes for Image Magick and Kakadu.
IMAGEMAGICK_OPTS = "-colorspace sRGB -quality 100 -resize 50%"
KDU_RECIPE = "\
-rate 1.71 Clevels=5 Clayers=5 Stiles=\{256,256\} Cprecincts=\{256,256\} \
-jp2_space sRGB \
-no_weights \
-quiet"

################################################################################
# Code. Leave this alone :).

LIB = os.getcwd() + "/lib"
ENV = {"LD_LIBRARY_PATH":LIB, "PATH":LIB + ":$PATH"}

## Logging
# INFO goes to stdout (default handler)
format = '%(asctime)s %(levelname)-5s: %(message)s'
dateFormat = '%a, %d %b %Y %H:%M:%S'
logging.basicConfig(level=logging.INFO,
                    format=format,
                    datefmt=dateFormat,
                    stream=os.sys.stdout)

# ERRORs go to stderr
err = logging.StreamHandler(os.sys.stderr)
err.setLevel(logging.ERROR)
err.setFormatter(logging.Formatter(format, dateFormat))
logging.getLogger("").addHandler(err)

class DerivativeMaker(object):
        def __init__(self):
            self.__files = []
            
        
        @staticmethod
        def _dirFilter(dir_name):
            return not dir_name.startswith(".")
        
        @staticmethod
        def _tiffFilter(file_name):
            return file_name.endswith(".tif") and not file_name.startswith(".")
        
        @staticmethod
        def _changeExtension(oldPath, newExtenstion):
            """
            Given a path with an image at the end (e.g., foo/bar/00000007.tif)
            and a new extension (e.g. ".jpg") returns the path with the new 
            extension (e.g., foo/bar/00000007.jpg
            """
            lastStop = oldPath.rfind(".")
            return oldPath[0:lastStop] + newExtenstion
        
        def buildFileList(self, dir=None):
            if dir == None: 
                dir = os.path.join(SOURCE_ROOT, PUDL_LOCATOR)
            
            for node in os.listdir(dir):
                absPath = os.path.join(dir, node)
                
                if os.path.isdir(absPath) and DerivativeMaker._dirFilter(node):
                     self.buildFileList(dir=absPath) #recursive call
                elif os.path.isfile(absPath) and DerivativeMaker._tiffFilter(node):
                    self.__files.append(absPath)
                else:
                    pass
        
        def makeDerivs(self):
            for tiffPath in self.__files:
                
                outTmpTiffPath = TMP_DIR + tiffPath[len(SOURCE_ROOT):]
                
                outJp2WrongExt = TARGET_ROOT + outTmpTiffPath[len(TMP_DIR):]
                outJp2Path = DerivativeMaker._changeExtension(outJp2WrongExt, ".jp2")
                
                if not os.path.exists(outJp2Path) or OVERWRITE_EXISTING == True: 
                    tiffSuccess = DerivativeMaker._makeTmpTiff(tiffPath, outTmpTiffPath)
                    if tiffSuccess:
                        DerivativeMaker._makeJp2(outTmpTiffPath, outJp2Path)
                        os.remove(outTmpTiffPath)
                        logging.info("Removed temporary file: " + outTmpTiffPath)
                else:
                    logging.warn("File exists: " + outJp2Path)
                
        @staticmethod
        def _makeTmpTiff(inPath, outPath):
            '''
            Returns the path to the TIFF that was created.
            '''
            #TODO: untested
            newDirPath = os.path.dirname(outPath)
            if not os.path.exists(newDirPath): os.makedirs(newDirPath, 0755)
            
            cmd = "convert " + inPath + " " + IMAGEMAGICK_OPTS + " " + outPath
            proc = subprocess.Popen(cmd, shell=True, \
                stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            return_code = proc.wait()
            
            # Read from pipes
            for line in proc.stdout:
                logging.info(line.rstrip())
            for line in proc.stderr:
                logging.error(line.rstrip())
                                
            if os.path.exists(outPath):
                logging.info("Created temporary file: " + outPath)
                return True
            else:
                logging.warn("Failed to create temporary file: " + outPath)
                return False
            
            
                
        @staticmethod
        def _makeJp2(inPath, outPath):
            '''
            Returns the path to the TIFF that was created.
            '''
            #TODO: untested
            newDirPath = os.path.dirname(outPath)
            if not os.path.exists(newDirPath): os.makedirs(newDirPath, 0755)
            
            
            cmd = "kdu_compress -i " + inPath + " -o " + outPath + " " + KDU_RECIPE
            
            proc = subprocess.Popen(cmd, shell=True, env=ENV, \
                    stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            return_code = proc.wait()
            
            # Read from pipes
            for line in proc.stdout:
                logging.info(line.rstrip())
            for line in proc.stderr:
                logging.error(line.rstrip())
                
            if os.path.exists(outPath):
                logging.info("Created: " + outPath)
                os.chmod(outPath, 0644)
                return True
            else:
                logging.warn("Failed to create: " + outPath)
                return False

        
if __name__ == "__main__":
    dMaker = DerivativeMaker()
    dMaker.buildFileList()
    dMaker.makeDerivs()

