import cv2
import numpy as np

"""
Layout of this code: 
Load a video and the currently existing dataset
Jump a few frames at a time-have one key add a mask to the positive dataset,
other add it to the negative dataset, saving OFTEN
"""
cam = cv2.VideoCapture('crop3.mp4')

frame = 0
min_frame = 756800
try:
	posset = list(np.load('pos_set.npy'))
	negset = list(np.load('neg_set.npy'))
except:
	posset = []
	negset = []

stay = True

print("""Controls:
			y-include in positive set
			n-include in negative set
			s-save
			f-skip
			q-quit annotating
""")


def image_to_mask(img):
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
	
while stay:
	if frame % 100 == 0:
		retval, img = cam.read()
		res_scale = .5
		img = cv2.resize(img, (0,0), fx = res_scale, fy = res_scale)
			
		mask = image_to_mask(img)
		
		while True:
			cv2.imshow('Image',img)
			cv2.imshow('Mask',mask)
			key = cv2.waitKey(1) & 0xFF
			
			if key == ord('y'):
				posset.append(mask)
				break
			elif key == ord('n'):
				negset.append(mask)
				break
			elif key == ord('s'):
				np.save('pos_set.npy',np.array(posset))
				np.save('neg_set.npy',np.array(negset))
				print('Results Saved')
				print('Current Frame: ',str(frame))
			elif key == ord('f'):
				break
			elif key == ord('q'):
				stay = False
				break
			elif frame < min_frame:
				break
	frame += 1
	if frame % 100000 == 0:
		np.save('pos_set.npy',np.array(posset))
		np.save('neg_set.npy',np.array(negset))
	
	if not stay:
		cv2.destroyAllWindows()
				