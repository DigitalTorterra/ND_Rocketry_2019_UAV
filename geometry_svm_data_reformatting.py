import cv2
import numpy as np
from math import log10, copysign

posset = list(np.load('pos_set.npy'))
negset = list(np.load('neg_set.npy'))

def calc_features(mask):
	#converting the mask to the right datatype
	im = mask.astype(np.uint8)
	
	#finds the contours of an image
	im2, contours, heirarchy = cv2.findContours(im, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	#print(contours)
	cnt = contours[0]
	
	#calculates all the moments of an images
	#M_pq=double integral from -inf to inf x^p*y^q*f(x,y)dxdy
	#for image-M_ij=sum over all x and y of x^i*y^i*I(x,y) where I is the intensity
	M = cv2.moments(cnt)
	#M-dict of moments for different is and js-can be used to compute centroid(center of mass)
	#as below.
	try:
		cx = int(M['m10']/M['m00'])
		cy = int(M['m01']/M['m00'])
	except:
		cx = 0
		cy = 0

	#area of the image, equivalent to M['m00']
	area = cv2.contourArea(cnt) 
	
	#perimeter/arclength of an image-second arg asks if shape or arclength
	perimeter = cv2.arcLength(cnt, True)
	
	#approximating contours
	epsilon = .1*cv2.arcLength(cnt, True)
	approx = cv2.approxPolyDP(cnt, epsilon, True)
	
	#attempts to correct for convexities
	hull = cv2.convexHull(cnt)
	
	#bounding rectangles
	#x,y-top left point, w, h-width/height
	x,y,w,h = cv2.boundingRect(cnt)
	rectangle = cv2.rectangle(im2, (x,y), (x+w, y+h), 1, 3)
	
	#draws a rotated rectangle around the image
	rect = cv2.minAreaRect(cnt)
	box = cv2.boxPoints(rect)
	box = np.int0(box)
	rotated_rectangle = cv2.drawContours(im2, [box], 0,255,2)
	
	
	
	#Aspect Ratio: Width/Height of bounding rect to each object
	#calculated based on non-rotated rectangle, may not be useful
	aspect_ratio = float(w)/h
	
	#Extent: Object Area/Bounding Rectangle Area
	rect_area = w*h
	rotated_rect_area = cv2.contourArea(box)
	try:
		extent_rotated = float(area)/rotated_rect_area
		extent = float(area)/rect_area
	except:
		extent_rotated = 0
		extent = 0
	
	#Solidity: Ratio of Contour Area to Convex Hull Area
	hull_area = cv2.contourArea(hull)
	try:
		solidity = float(area)/hull_area
	except:
		solidity = 0
	
	#Equivalent Diameter: diameter of circle whose area is same as contour area
	#ED=sqrt(4*contour area/pi)
	equi_diameter = np.sqrt(4*area/np.pi)
	
	#Orientation: Angle at which object is directed-also gives major/minor axis lengths
	try:
		(x1, y1), (MA, ma), angle = cv2.fitEllipse(cnt)
	except:
		(x1,y1,MA,ma,angle) = (0,0,0,0,0)
	#very useful, just not now
	#min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(imgray, mask=mask)
	
	#compactness=perimeter^2/area
	try:
		compactness = perimeter ** 2 / area
	except:
		compactness = 0
	
	#Eccentricity: major axis/minor axis
	try:
		eccentricity = MA/ma
	except:
		eccentricity = 0
	
	#Hu moments-invariant to transformation in an object
	huMoments = cv2.HuMoments(M)
	
	#logscaled huMoments
	loghuMoments = huMoments
	try:
		for i in range(0,7):
			loghuMoments[i] = -1* copysign(1.0, huMoments[i]) * log10(abs(huMoments[i]))
	except:
		pass
	"""
	What to include in SVM?
	
	Aspect Ratio, Extent, Solidity, Compactness, Eccentricity, Log Hu Moments
	Based on Mask Itself:
	Aspect Ratio
	Solidity
	Compactness
	Eccentricity
	Log Hu Moments
	
	Based on Mask+Bounding Rectangle:
	Extent
	
	Add a rotated extent
	"""
		
	features = {
	'Contours':contours,
	'Moments':M,
	'Centroid':(cx,cy),
	'Area':area,
	'Perimeter':perimeter,
	'Epsilon':epsilon,
	'Approximate Contours':approx,
	'Hull':hull,
	'Bounding Rectangle Def':(x,y,w,h),
	'Rectangle':rectangle,
	'Min Area Rectangle':rect,
	'Box':box,
	'Rotated Rectangle':rotated_rectangle,
	
	'Aspect Ratio':aspect_ratio,
	'Rectangle Area':rect_area,
	'Rotated Extent':extent_rotated,
	'Extent':extent,
	'Hull Area':hull_area,
	'Solidity':solidity,
	'Equivalent Diameter':equi_diameter,
	'Major Axis':MA,
	'Minor Axis':ma,
	'Angle':angle,
	'Compactness':compactness,
	'Eccentricity':eccentricity,
	'Hu Moments':huMoments,
	'Log Hu Moments':loghuMoments	
	}
	return(features)

dataset = []
#[Aspect Ratio, Rotated Extent, Solidity, Compactness, Eccentricity, Log Hu Moments 1-7, Label]
for i in range(len(posset)):
	try:
		features = calc_features(posset[i])
		vec = [features['Aspect Ratio'],features['Rotated Extent'],
				features['Solidity'],features['Compactness'],
				features['Eccentricity']]
		vec += list(features['Log Hu Moments'].T[0])+[1]
		dataset.append(vec)
		print(i)
	except:
		pass

for i in range(len(negset)):
	try:
		features = calc_features(negset[i])
		vec = [features['Aspect Ratio'],features['Rotated Extent'],
				features['Solidity'],features['Compactness'],
				features['Eccentricity']]
		vec += list(features['Log Hu Moments'].T[0])+[0]
		dataset.append(vec)
		print(i)
	except:
		pass

np.save('dataset.npy',np.array(dataset))