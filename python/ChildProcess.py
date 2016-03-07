
import zerorpc
import numpy as np
from sklearn.svm import SVC
from PIL import Image
from detect import Detection
from alignment import AlignDlib
import time
import openface
from classifier import trainSVM
from sklearn.grid_search import GridSearchCV
import openface
import cv2
import socket
import StringIO
import base64
import json
import io
import sys
import os
import dlib
import imagehash
fileDir = os.path.dirname(os.path.realpath(__file__))

align = AlignDlib('model/shape_predictor_68_face_landmarks.dat')
modelDir = os.path.join(fileDir,"model","nn4.small2.v1.t7")
net = openface.TorchNeuralNet(modelDir,96,False)


class Recognition(object):

	def __init__(self):
		self.images = {}
		self.training = True
		self.people = []
		self.svm = None
		self.unknownImgs = np.load("unknown.npy")

	def hello(self,name):
		return "Helloe, %s" % name

	def trainingToggle(self,train):
		if train == 'true':
			self.training = True
		else:
			self.training = False
		return
	def addPerson(self,peep):
		self.people.append(peep)
		return

	def trainSVM(self):
		print("+ Training SVM on {} labeled images.".format(len(self.images)))
		d = self.getData()
		if d is None:
			self.svm = None
			return
		else:
			(X, y) = d
			print y
			print "end y"
			print X
			y = y.astype(np.float)
			numIdentities = len(set(y + [-1]))
			print numIdentities
			if numIdentities <= 1:
				return

			param_grid = [
				{'C': [1, 10, 100, 1000],
				 'kernel': ['linear']},
				{'C': [1, 10, 100, 1000],
				 'gamma': [0.001, 0.0001],
				 'kernel': ['rbf']}
			]
			self.svm = GridSearchCV(SVC(C=1), param_grid, cv=5).fit(X, y)
			print "Svm has been trained"
			print self.svm


	def getData(self):
		X = []
		y = []
		for img in self.images.values():
			X.append(img.rep)
			y.append(img.identity)

		numIdentities = len(set(y + [-1])) - 1
		if numIdentities == 0:
			return None

		
		numUnknown = y.count(-1)
		numIdentified = len(y) - numUnknown
		numUnknownAdd = (numIdentified / numIdentities) - numUnknown
		if numUnknownAdd > 0:
			print("+ Augmenting with {} unknown images.".format(numUnknownAdd))
			for rep in self.unknownImgs[:numUnknownAdd]:
				# print(rep)
				X.append(rep)
				y.append(-1)

		X = np.vstack(X)
		y = np.array(y)
		return (X, y)


	def processFrame(self, dataURL, identity):
		head = "data:image/jpeg;base64,"
		assert(dataURL.startswith(head))
		imgdata = base64.b64decode(dataURL[len(head):])
		imgF = StringIO.StringIO()
		imgF.write(imgdata)
		imgF.seek(0)
		img = Image.open(imgF)

		buf = np.fliplr(np.asarray(img))
		rgbFrame = np.zeros((300, 400, 3), dtype=np.uint8)
		rgbFrame[:, :, 0] = buf[:, :, 2]
		rgbFrame[:, :, 1] = buf[:, :, 1]
		rgbFrame[:, :, 2] = buf[:, :, 0]

		if not self.training:
			annotatedFrame = np.copy(buf)

		# cv2.imshow('frame', rgbFrame)
		# if cv2.waitKey(1) & 0xFF == ord('q'):
		#     return

		identities = []

		#bbs for when we want to do multiple people at once
		# bbs = align.getAllFaceBoundingBoxes(rgbFrame)

		bb = align.getLargestFaceBoundingBox(rgbFrame)
		bbs = [bb] if bb is not None else []
		bl = None
		tr = None
		for bb in bbs:
			# print(len(bbs))
			alignedFace = align.align(96, rgbFrame, bb)
			if alignedFace is None:
				continue
			phash = str(imagehash.phash(Image.fromarray(alignedFace))) 
			if phash in self.images:
				identity = self.images[phash].identity
			else:
				rep = net.forward(alignedFace)

	
				if self.training:
					print "Training is true"
					self.images[phash] = Face(rep, identity)

				else:
					print "Training is false"
					print type(self.svm)
					if len(self.people) == 0:
						identity = -1
					elif len(self.people) == 1:
						identity = 0
					if self.svm is not None:
						print "identifying person"
						identity = self.svm.predict(rep)[0]
						bl = (bb.left(), bb.bottom())
						tr = (bb.right(), bb.top())
					else:
						print("hhh")
						identity = -1
					if identity not in identities:
						identities.append(identity)
		temp = self.people[int(float(identity))]
		return temp,bl,tr

class Face:

	def __init__(self, rep, identity):
		self.rep = rep
		self.identity = identity

	def __repr__(self):
		return "{{id: {}, rep[0:5]: {}}}".format(
			str(self.identity),
			self.rep[0:5]
		)

s = zerorpc.Server(Recognition())
s.bind("tcp://0.0.0.0:4242")
s.run()
