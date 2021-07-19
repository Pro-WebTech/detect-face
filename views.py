from django.shortcuts import render, redirect
from django import forms

from django.http import HttpResponseRedirect
from django.http import HttpResponse

from django.urls import reverse_lazy
from django.views.generic import TemplateView
from employee.forms import EmployeeForm

from django.views.generic import DetailView
from employee.models import Employee

import face_recognition
from PIL import Image, ImageDraw
import numpy as np
import cv2

import os
import json
import filetype

from employee.models import Client
from hashlib import md5

IMAGES_DIR = 'images/known'
Target_DIR = 'media/images'
user_photo = []
user_photo_name = []

def login(request):
    if request.session.has_key('user'):
        return redirect('/landing')
    return render(request, 'login.html')
def login_submit(request):
    login_data = request.POST.dict()
    username = login_data.get('username')
    password = login_data.get('password')
    try:
        client = Client.objects.get(username=username, password=md5(password.encode("UTF-8")).hexdigest())
        request.session['user'] = username
    except Client.DoesNotExist:
        client = None
    if client != None:
        return redirect('/landing')
    else:
        return redirect('/')
def logout(request):
    del request.session['user']
    return redirect('/')
def landing(request):
    if request.session.has_key('user'):
        return render(request, 'landing.html')
    else:
        return redirect('/')
def works(request):
    return render(request, 'works.html')
def digital_makeup(request):
    image = face_recognition.load_image_file(request.GET['tar_image'])

    # Find all facial features in all the faces in the image
    face_landmarks_list = face_recognition.face_landmarks(image)

    pil_image = Image.fromarray(image)
    for face_landmarks in face_landmarks_list:
        d = ImageDraw.Draw(pil_image, 'RGBA')

        # Make the eyebrows into a nightmare
        d.polygon(face_landmarks['left_eyebrow'], fill=(68, 54, 39, 128))
        d.polygon(face_landmarks['right_eyebrow'], fill=(68, 54, 39, 128))
        d.line(face_landmarks['left_eyebrow'], fill=(68, 54, 39, 150), width=5)
        d.line(face_landmarks['right_eyebrow'], fill=(68, 54, 39, 150), width=5)

        # Gloss the lips
        d.polygon(face_landmarks['top_lip'], fill=(150, 0, 0, 128))
        d.polygon(face_landmarks['bottom_lip'], fill=(150, 0, 0, 128))
        d.line(face_landmarks['top_lip'], fill=(150, 0, 0, 64), width=8)
        d.line(face_landmarks['bottom_lip'], fill=(150, 0, 0, 64), width=8)

        # Sparkle the eyes
        d.polygon(face_landmarks['left_eye'], fill=(255, 255, 255, 30))
        d.polygon(face_landmarks['right_eye'], fill=(255, 255, 255, 30))

        # Apply some eyeliner
        d.line(face_landmarks['left_eye'] + [face_landmarks['left_eye'][0]], fill=(0, 0, 0, 110), width=6)
        d.line(face_landmarks['right_eye'] + [face_landmarks['right_eye'][0]], fill=(0, 0, 0, 110), width=6)

        pil_image.show()
    return HttpResponse('success')

def find_facial_feature(request):
    # Load the jpg file into a numpy array
    image = face_recognition.load_image_file(request.GET['tar_image'])

    # Find all facial features in all the faces in the image
    face_landmarks_list = face_recognition.face_landmarks(image)

    print("I found {} face(s) in this photograph.".format(len(face_landmarks_list)))

    # Create a PIL imagedraw object so we can draw on the picture
    pil_image = Image.fromarray(image)
    d = ImageDraw.Draw(pil_image)

    for face_landmarks in face_landmarks_list:

        # Print the location of each facial feature in this image
        for facial_feature in face_landmarks.keys():
            print("The {} in this face has the following points: {}".format(facial_feature, face_landmarks[facial_feature]))

        # Let's trace out each facial feature in the image with a line!
        for facial_feature in face_landmarks.keys():
            d.line(face_landmarks[facial_feature], width=5)

    # Show the picture
    pil_image.show()
    return HttpResponse('success')

def find_face(request):
    image = face_recognition.load_image_file(request.GET['tar_image'])

    # Find all the faces in the image using the default HOG-based model.
    # This method is fairly accurate, but not as accurate as the CNN model and not GPU accelerated.
    # See also: find_faces_in_picture_cnn.py
    face_locations = face_recognition.face_locations(image)

    print("I found {} face(s) in this photograph.".format(len(face_locations)))

    for face_location in face_locations:

        # Print the location of each face in this image
        top, right, bottom, left = face_location
        print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom, right))

        # You can access the actual face itself like this:
        face_image = image[top:bottom, left:right]
        pil_image = Image.fromarray(face_image)
        pil_image.show()
    return HttpResponse('success')

def face_recog(request):
    unknown_image = face_recognition.load_image_file(request.GET['tar_image'])

    # Find all the faces and face encodings in the unknown image
    face_locations = face_recognition.face_locations(unknown_image)
    face_encodings = face_recognition.face_encodings(unknown_image, face_locations)

    # Convert the image to a PIL-format image so that we can draw on top of it with the Pillow library
    # See http://pillow.readthedocs.io/ for more about PIL/Pillow
    pil_image = Image.fromarray(unknown_image)
    # Create a Pillow ImageDraw Draw instance to draw with
    draw = ImageDraw.Draw(pil_image)

    # Loop through each face found in the unknown image
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(user_photo, face_encoding)

        name = "Unknown"

        # If a match was found in known_face_encodings, just use the first one.
        # if True in matches:
        #     first_match_index = matches.index(True)
        #     name = known_face_names[first_match_index]

        # Or instead, use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(user_photo, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = user_photo_name[best_match_index]

        # Draw a box around the face using the Pillow module
        draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))

        # Draw a label with a name below the face
        text_width, text_height = draw.textsize(name)
        draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
        draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))


    # Remove the drawing library from memory as per the Pillow docs
    del draw

    # Display the resulting image
    pil_image.show()
    return HttpResponse('success')


def video_detection(request):
    video_capture = cv2.VideoCapture(request.GET['tar_image'])



    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_frame = frame[:, :, ::-1]

        # Find all the faces and face enqcodings in the frame of video
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        # Loop through each face in this frame of video
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(user_photo, face_encoding)

            name = "Unknown"

            # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(user_photo, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = user_photo_name[best_match_index]

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()

    return HttpResponse('success')




def verifyPhoto():

    context = {}
    #DEBUG CODE TO FIND DIRECTORY TREES
    # for dirName, subdirList, fileList in os.walk(rootDir):
    #     print('Found directory: %s' % dirName)
    #     for fname in fileList:
    #         print('\t%s' % fname)

    '''Loop over images in directory, add to lists
    '''
    print("Loading registered faces database!")
    for file in os.listdir(IMAGES_DIR):
        if file.endswith(('.jpg', '.jpeg', '.png')):
            image = face_recognition.load_image_file(f"{IMAGES_DIR}/{file}")

            try:
                # encodes all found faces
                encoding = face_recognition.face_encodings(image)[0]
            except IndexError:
                print("\n\nSeems one or more images didnt contain any faces!\n\n")
                pass

            # add encodings to list 
            user_photo.append(encoding)
            # add photo name to list
            user_photo_name.append(file)

            # DEBUG print
            print(user_photo)
            print(user_photo_name)

            continue



class EmployeeImage(TemplateView):

    form = EmployeeForm
    template_name = 'emp_image.html'
    def face_detection(self, request, *args, **kwargs):
        print("hello this is face detection")

    def post(self, request, *args, **kwargs):
        # verifyPhoto()
        form = EmployeeForm(request.POST, request.FILES)

        if form.is_valid():
            obj = form.save()
            kind = filetype.guess(f"{Target_DIR}/{request.FILES['emp_image']}")
            kindtype = kind.mime.split('/')[0]
            if kindtype == 'image':
                unknown_image = face_recognition.load_image_file(f"{Target_DIR}/{request.FILES['emp_image']}")
                unknown_face_encoding = face_recognition.face_encodings(unknown_image)[0]
                results = face_recognition.compare_faces(user_photo, unknown_face_encoding)
                i = 0
                checkflag = False
                checkphotoname = " "
                for tmp in results:
                    if tmp:
                        checkflag = True
                        checkphotoname =checkphotoname + user_photo_name[i].split('.')[0]
                        print(user_photo_name[i])
                    i = i + 1
                if checkflag == False:
                    checkphotoname = "unknown"
                # return HttpResponseRedirect(reverse_lazy('emp_image_display', kwargs={'data':checkphotoname,'pk': obj.id}))
                return render(request,'emp_image.html',{'data':checkphotoname,'url': f"{Target_DIR}/{request.FILES['emp_image']}"})
            elif kindtype == 'video':
                return render(request,'emp_image.html',{'video_url': f"{Target_DIR}/{request.FILES['emp_image']}"})
        context = self.get_context_data(form=form)
        return self.render_to_response(context)     

    def get(self, request, *args, **kwargs):
        
        return self.post(request, *args, **kwargs)


        '''Decides where user is redirected based on return of takePhoto()
        if true - redirect to login
        if false - redirect to register
        '''

class EmpImageDisplay(DetailView):
    model = Employee
    template_name = 'emp_image_display.html'
    context_object_name = 'emp'  

    verifyPhoto()