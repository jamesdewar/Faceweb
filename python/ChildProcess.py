
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
					else:
						print("hhh")
						identity = -1
					if identity not in identities:
						identities.append(identity)
		temp = "identity %s", identity
		print self.training
		return temp

		# 	if not self.training:
		# 		bl = (bb.left(), bb.bottom())
		# 		tr = (bb.right(), bb.top())
		# 		cv2.rectangle(annotatedFrame, bl, tr, color=(153, 255, 204),
		# 					  thickness=3)
		# 		if identity == -1:
		# 			if len(self.people) == 1:
		# 				name = self.people[0]
		# 			else:
		# 				name = "Unknown"
		# 		else:
		# 			name = self.people[identity]
		# 		cv2.putText(annotatedFrame, name, (bb.left(), bb.top() - 10),
		# 					cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.75,
		# 					color=(152, 255, 204), thickness=2)

		# if not self.training:
		# 	msg = {
		# 		"type": "IDENTITIES",
		# 		"identities": identities
		# 	}
		# 	#self.sendMessage(json.dumps(msg))

		# 	# plt.figure()
		# 	# plt.imshow(annotatedFrame)
		# 	# plt.xticks([])
		# 	# plt.yticks([])

		# 	imgdata = StringIO.StringIO()
		# 	#plt.savefig(imgdata, format='png')
		# 	imgdata.seek(0)
		# 	content = 'data:image/png;base64,' + \
		# 		urllib.quote(base64.b64encode(imgdata.buf))
		# 	msg = {
		# 		"type": "ANNOTATED",
		# 		"content": content
		# 	}
		# 	#self.sendMessage(json.dumps(msg))

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