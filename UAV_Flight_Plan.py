import numpy as np

def takeOff():
    pass

def gotoFEA():
    pass

def locateTarget():
    def find_cm(image):
        #image is an mxn binary mask
        x = [0,0]
        y = [0,0]
        
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                if image[i,j] == 1:
                    x[0] += i
                    y[0] += j
                    x[1] += 1
                    y[1] += 1
        return([int(x[0]/x[1]),int(y[0]/y[1])])
        
    pass

def adjustPosition():
    pass

def descend():
    pass

def deployBeacon():
    pass

def safeLand():
    pass


def main():
    takeOff()
    
    gotoFEA()
    
    centered = False
    
    while not centered:      
        locateTarget()
    
        adjustPosition()
    
    descend()
    
    deployBeacon()
    
    safeLand()
    