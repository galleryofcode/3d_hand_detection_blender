import cv2
import numpy as np
import time
import bpy
import random

#Open Camera object
cap = cv2.VideoCapture(0)

def nothing(x):
    pass

# Function to find angle between two vectors
def Angle(v1,v2):
    dot = np.dot(v1,v2)
    x_modulus = np.sqrt((v1*v1).sum())
    y_modulus = np.sqrt((v2*v2).sum())
    cos_angle = dot / x_modulus / y_modulus
    angle = np.degrees(np.arccos(cos_angle))
    return angle

# Function to find distance between two points in a list of lists
def FindDistance(A,B): 
    return np.sqrt(np.power((A[0][0]-B[0][0]),2) + np.power((A[0][1]-B[0][1]),2)) 

def runcam():
    
    ret,img = cap.read()
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(5,5),0)
    ret,thresh1 = cv2.threshold(blur,70,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
 
    contours, hierarchy = cv2.findContours(thresh1,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    drawing = np.zeros(img.shape,np.uint8)
    max_area=0
    for i in range(len(contours)):
        cnt=contours[i]
        area = cv2.contourArea(cnt)
        if(area>max_area):
            max_area=area
            ci=i
            
    cnt=contours[ci]

    hull = cv2.convexHull(cnt)
    prev_hull = cv2.convexHull(cnt)
    prev_cnt = cnt
    moments = cv2.moments(cnt)
    if moments['m00']!=0:
        cx = int(moments['m10']/moments['m00']) # cx = M10/M00
        cy = int(moments['m01']/moments['m00']) # cy = M01/M00
           
    centr=(cx,cy)
    bpy.data.objects['boxnijo'].location.x = ((cx*-1)/100)*10 + 35
    bpy.data.objects['boxnijo'].location.z = (cy/100)*(-10) + 30
    bpy.data.objects['boxnijo'].location.y = 0
    cv2.circle(img,centr,5,[0,0,255],2)
    cv2.drawContours(drawing,[cnt],0,(0,255,0),2) 
    cv2.drawContours(drawing,[hull],0,(255,0,255),2) 
    
    cnt = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)
    hull = cv2.convexHull(cnt,returnPoints = False)
 
    if(1):
        defects = cv2.convexityDefects(cnt,hull)
        mind=0
        maxd=0
        for i in range(defects.shape[0]):
             s,e,f,d = defects[i,0]
             start = tuple(cnt[s][0])
             end = tuple(cnt[e][0])
             far = tuple(cnt[f][0])
             dist = cv2.pointPolygonTest(cnt,centr,True)
             cv2.line(img,start,end,[0,255,0],2)
             cv2.circle(img,far,5,[0,0,255],-1)
            #print "i=",i,"area=",area,"hull",hull,"prev_hull",prev_hull
            #print "Points=",prev_hull
        i=0
    #change_image[hull] = Clear[hull]
    #cv2.imshow('final_game',change_image)
    cv2.imshow('output',drawing)
    #cv2.imshow('input',img)
    

class ModalTimerOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"

    _timer = None

    def modal(self, context, event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            # change theme color, silly!
            #color = context.preferences.themes[0].view_3d.space.gradients.high_gradient
            #color.s = 1.0
            #color.h += 0.01
            #bpy.data.objects['boxnijo'].location.x = random.randint(1,10)
            #bpy.data.objects['boxnijo'].location.y = random.randint(1,5)
            runcam()

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


def register():
    bpy.utils.register_class(ModalTimerOperator)


def unregister():
    bpy.utils.unregister_class(ModalTimerOperator)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.wm.modal_timer_operator()