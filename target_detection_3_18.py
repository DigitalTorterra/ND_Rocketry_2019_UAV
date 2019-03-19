from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
import numpy as np
import pickle
import cv2

class TargetDetection():
	def __init__(self):
		self.filename = 'finalized_model.sav'
		self.loaded_model = pickle.load(open(self.filename, 'rb'))
	
	def image_to_mask(self, img):
		#input: BGR image 
		#output: image after color shift, binary masking, and morphologies	
		hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
		
		lower = np.array([25, 159, 158])
		upper = np.array([31, 230, 255])
	
		objmask = cv2.inRange(hsv, lower, upper)
		
		kernel = np.ones((5,5), np.uint8)
		#objmask = cv2.morphologyEx(objmask, cv2.MORPH_OPEN, kernel=kernel)
		objmask = cv2.morphologyEx(objmask, cv2.MORPH_DILATE, kernel=kernel)
		objmask = cv2.morphologyEx(objmask, cv2.MORPH_CLOSE, kernel=kernel)
		objmask = cv2.morphologyEx(objmask, cv2.MORPH_ERODE, kernel=kernel)
	
		return(objmask)
	
	def mask_to_features(self, mask):
		#input: binary mask image
		#output: all relevant geometric features
	
		#converting the mask to the right datatype
		im = mask.astype(np.uint8)
		im2 = im
		#finds the contours of an image
		contours, heirarchy = cv2.findContours(im, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

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
		
		#attempts to correct for convexities
		hull = cv2.convexHull(cnt)
		
		#bounding rectangles
		#x,y-top left point, w, h-width/height
		x,y,w,h = cv2.boundingRect(cnt)
		rectangle = cv2.rectangle(im2, (x,y), (x+w, y+h), 1, 3)
		
		#draws a rotated rectangle around the image
		rect = cv2.minAreaRect(cnt)
		box = cv2.cv.BoxPoints(rect)
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
		except:
			extent_rotated = 0
		
		#Solidity: Ratio of Contour Area to Convex Hull Area
		hull_area = cv2.contourArea(hull)
		try:
			solidity = float(area)/hull_area
		except:
			solidity = 0

		
		#Orientation: Angle at which object is directed-also gives major/minor axis lengths
		
		if len(cnt) >= 5:

			try:
				(x1, y1), (MA, ma), angle = cv2.fitEllipse(cnt)
		    	except:
				(x1,y1,MA,ma,angle) = (0,0,0,0,0)
		else:
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
		'Hull':hull,
		'Bounding Rectangle Def':(x,y,w,h),
		'Rectangle':rectangle,
		'Min Area Rectangle':rect,
		'Box':box,
		'Rotated Rectangle':rotated_rectangle,
		
		'Aspect Ratio':aspect_ratio,
		'Rectangle Area':rect_area,
		'Rotated Extent':extent_rotated,
		'Hull Area':hull_area,
		'Solidity':solidity,
		'Major Axis':MA,
		'Minor Axis':ma,
		'Angle':angle,
		'Compactness':compactness,
		'Eccentricity':eccentricity,
		'Hu Moments':huMoments,
		'Log Hu Moments':loghuMoments	
		}
		return(features)	
	
	def svm(self, features):
		vec = [features['Aspect Ratio'],features['Rotated Extent'],
				features['Solidity'],features['Compactness'],
				features['Eccentricity']]
		vec += list(features['Log Hu Moments'].T[0])
		
		vec = np.array(vec)
		vec = np.expand_dims(vec,0)
		
		prediction = self.loaded_model.predict(vec)

		return(prediction)
	
	def detect_target(self, img):
		#input: an image
		#output: center of mass of output image plus SVM classification
		#note: resizes to 240x320 in the process, keep in mind w/centroid
		res_scale = 0.5  # rescale the input image if it's too large
		img = cv2.resize(img, (0, 0), fx=res_scale, fy=res_scale)

		objmask = self.image_to_mask(img)
		
		try:
			features = self.mask_to_features(objmask)
		
			svm_result = self.svm(features)
		except Exception as e:
			print e
			#if features receives a blank objmask, just say it's 0
			return((0,0),np.array([0]))
			
		return(features['Centroid'],svm_result)
"""	
images = np.load('images.npy')

target = TargetDetection()
scaled_image, objmask, centroid, svm_result = target.detect_target(images[0])		

x_cm, y_cm = centroid
output_image = np.copy(scaled_image)

output_image[y_cm-4:y_cm+4,x_cm-4:x_cm+4] = np.zeros_like(output_image[y_cm-4:y_cm+4,x_cm-4:x_cm+4])

cv2.imshow('Image Before Transformation',scaled_image)
cv2.imshow('Object Mask of Image',objmask)
cv2.imshow('Image Annotated with Determined Center',output_image)

cv2.waitKey(0)
"""
