def almost_eq_2darray(arr1,arr2):
    alltrue = True
    for i in range(len(arr1)):
        for j in range(3):
            val = abs(int(arr1[i][j]) - int(arr2[i][j]))
            if val > 30:
                alltrue=False
                #print("{0} and {1} at i={2}, {3}, {4}".format(arr1[i],arr2[i],i,arr1[i][j],arr2[i][j]))
                return False
    return alltrue

# Original functionality
"""
import cv2,io,pickle
import numpy as np
im1 = cv2.imread("https://cdn.discordapp.com/attachments/426069322293706754/653690508316508160/image0.png")
im2 = cv2.imread("https://cdn.discordapp.com/attachments/426069322293706754/653690517216821249/image0.png")

im1 = None
with open("im1.pickle","rb") as file:
    im1 = pickle.load(file)

#cv2.imwrite("test.png",im1)


ind = -1
for i in range(len(im1)):
    works = True
    for j in range(i,len(im1)):
        if not almost_eq_2darray(im1[j],im2[j-i]):
            works = False
            break
    if works == True:
        ind = i
        break

comboarr = np.array(im1.tolist()[:ind] + im2.tolist())

print(comboarr.shape)

is_success, buff = cv2.imencode(".png",comboarr)

with io.BytesIO(buff) as file:
    file.seek(0)
    with open("test.png","wb") as rf:
        rf.write(file.read())

"""