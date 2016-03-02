#read docs picamera 
import io
import time
import dlib
import scipy.misc
import sys
from PIL import Image
from skimage import io
from alignment import AlignDlib 
from matplotlib import pyplot as plt
import numpy as np
import urllib
import base64
import numpy as np
import os
import StringIO
import imagehash
import fileinput
#capture



class Detection():

#	def __init__(self):
		#threading.Thread.__init__(self)
#		self.instance = instance


	def detect(self, img, model):
		img_np = np.array(img)
		recognition = model 
		faces = recognition.getLargestFaceBoundingBox(img_np)
		#print faces
		#  plt.imshow(test,interpolation='nearest')
		#  plt.show()
		print faces
		print type(faces)
		test = recognition.align(96,img_np,faces)
		return test


	def detectXML(self, img, faces,imgTP):
		img_np = np.array(img)
		test = imgTP.align(96,img_np,faces)
		return test

	# def processFrame(self, dataURL, identity):
 #        head = "data:image/jpeg;base64,"
 #        assert(dataURL.startswith(head))
 #        imgdata = base64.b64decode(dataURL[len(head):])
 #        imgF = StringIO.StringIO()
 #        imgF.write(imgdata)
 #        imgF.seek(0)
 #        img = Image.open(imgF)

 #        buf = np.fliplr(np.asarray(img))
 #        rgbFrame = np.zeros((300, 400, 3), dtype=np.uint8)
 #        rgbFrame[:, :, 0] = buf[:, :, 2]
 #        rgbFrame[:, :, 1] = buf[:, :, 1]
 #        rgbFrame[:, :, 2] = buf[:, :, 0]

 #        if not self.training:
 #            annotatedFrame = np.copy(buf)

 #        # cv2.imshow('frame', rgbFrame)
 #        # if cv2.waitKey(1) & 0xFF == ord('q'):
 #        #     return

 #        identities = []
 #        # bbs = align.getAllFaceBoundingBoxes(rgbFrame)
 #        bb = align.getLargestFaceBoundingBox(rgbFrame)
 #        bbs = [bb] if bb is not None else []
 #        for bb in bbs:
 #            # print(len(bbs))
 #            alignedFace = align.alignImg("affine", 96, rgbFrame, bb)
 #            if alignedFace is None:
 #                continue

 #            phash = str(imagehash.phash(Image.fromarray(alignedFace)))
 #            if phash in self.images:
 #                identity = self.images[phash].identity
 #            else:
 #                rep = net.forwardImage(alignedFace)
 #                # print(rep)
 #                if self.training:
 #                    self.images[phash] = Face(rep, identity)
 #                    # TODO: Transferring as a string is suboptimal.
 #                    # content = [str(x) for x in cv2.resize(alignedFace, (0,0),
 #                    # fx=0.5, fy=0.5).flatten()]
 #                    content = [str(x) for x in alignedFace.flatten()]
 #                    msg = {
 #                        "type": "NEW_IMAGE",
 #                        "hash": phash,
 #                        "content": content,
 #                        "identity": identity,
 #                        "representation": rep.tolist()
 #                    }
 #                    self.sendMessage(json.dumps(msg))
 #                else:
 #                    if len(self.people) == 0:
 #                        identity = -1
 #                    elif len(self.people) == 1:
 #                        identity = 0
 #                    elif self.svm:
 #                        identity = self.svm.predict(rep)[0]
 #                    else:
 #                        print("hhh")
 #                        identity = -1
 #                    if identity not in identities:
 #                        identities.append(identity)

 #            if not self.training:
 #                bl = (bb.left(), bb.bottom())
 #                tr = (bb.right(), bb.top())
 #                cv2.rectangle(annotatedFrame, bl, tr, color=(153, 255, 204),
 #                              thickness=3)
 #                if identity == -1:
 #                    if len(self.people) == 1:
 #                        name = self.people[0]
 #                    else:
 #                        name = "Unknown"
 #                else:
 #                    name = self.people[identity]
 #                cv2.putText(annotatedFrame, name, (bb.left(), bb.top() - 10),
 #                            cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.75,
 #                            color=(152, 255, 204), thickness=2)

 #        if not self.training:
 #            msg = {
 #                "type": "IDENTITIES",
 #                "identities": identities
 #            }
 #            self.sendMessage(json.dumps(msg))

 #            plt.figure()
 #            plt.imshow(annotatedFrame)
 #            plt.xticks([])
 #            plt.yticks([])

 #            imgdata = StringIO.StringIO()
 #            plt.savefig(imgdata, format='png')
 #            imgdata.seek(0)
 #            content = 'data:image/png;base64,' + \
 #                urllib.quote(base64.b64encode(imgdata.buf))
 #            msg = {
 #                "type": "ANNOTATED",
 #                "content": content
 #            }
 #            self.sendMessage(json.dumps(msg))

if __name__ == '__main__':
	detect = Detection()
	test =  ''
	for line in fileinput.input():
		test = line
	sys.stdout.write('Received message')

