import png
import functools
import ImageUtility
import copy
import math

#Our goal with seam carving is to compute, for each pixel along the top scanline
#the seam with the lowest energy, once we have all the seams computed we can use
#that information to remove as many as we want and even do it dynamically
#(I believe the paper explains it as computing the lowest energy seam ending
#at each pixel of the bottom scanline, I don't think it makes much difference)
#we only need 1 seam per pixel, obviously, since when we remove that seam we no longer
#have the pixel
#
#The problem with computing the seams is that, for each pixel in a scanlines we have
#a really big number of seams that start at the opposite side of the image and end at that
#pixel, we need an efficient approach to computing them
#
#Dynamic programming approach:
#In dynamic programming, we solve a problem recursively, dividing a problem into subproblems
#and so on until we reach base cases, the difference is that, in this case, the subproblems
#overlap, that is, they share subproblems, so the solutions to a subproblem are stored, and thus
#only solved the first time we encounter them
#
#Sn(j) -> Cost of the seam  with less energy from that pixel (the pixel at row n, column j)
#to the side of the image from which seams are computed
#
#-Step 1: initialize the values of the pixels of the first row, S1(j)=e(1, j) for j = 1 to m,
#where m is the width of the image
#
#-Step 2: for each subsequent row, compute Sn(j) as the sum of the energy of the pixel (n,j) plus
#min(Sn-1(j-1), Sn(j), Sn+1(j+1)) (The diagram at wikipedia is really easy to understand)
#
#When we have computed the energy for the minimal seams arriving at each pixel, we can easily identify
#and remove the seam with the minimum energy, of course, after we do this the other values are no longer
#valid, and we would have to run the algorithm again to find the next lowest energy seam. Here we can use
#previously computed values to simplify the next step
#
#This method for computing the seams is called a bottom-up approach in dynamic programming, the solution to
#each subproblem (which is the cost of the less energy seam leading to this pixel from the start row?) depends
#only on the solution of the previous subproblems, thus when we want to solve it we just look at the previous
#solutions and calculate the result, and there are multiple subproblems that use the same previous solutions

# We define the energy of a pixel as Ei = |dI/dx| + |dI/dy|, being I the
# energy function of the image, a multivariate function that provides the intensity
# values for the image (in a greyscale image, in a RGB image we would have 3 separate functions)
# We only know the values obtained from the evaluation of this function in each of the pixels

#Returns an array indicating the cost of the less energy seam for each of the bottom-scanline pixels
def removeMinimalSeam(energyImage, imageRGB):
    #PROVISIONAL UNTIL I WRITE THE DECODER FOR TYPE 0 COLOR AND THE RECEIVED IMAGE
    #IS ALREADY GREYSCALE
    if(type(energyImage[0][0]) != int):
        energyImage = getGreyscale(energyImage)

    #print("Seam cost generation started")

    seamCost = []
    #Initializing the values of the pixels in the top scanline
    seamCost.append(energyImage[0])
    #Now, iterate through all the rows from row 2 to n and through
    #all the pixels in each row
    for i in range(1, len(energyImage)):
            seamCost.append([])
            for j in range(len(energyImage[0])):
                #Compute the minimum seam cost up to each pixel of the row
                if j == 0:
                    seamCost[i].append(min(seamCost[i - 1][j],
                                      seamCost[i - 1][j + 1]) + energyImage[i][j])
                elif j == len(energyImage[0]) - 1:
                    seamCost[i].append(min(seamCost[i - 1][j - 1],
                                      seamCost[i - 1][j]) + energyImage[i][j])
                else:
                    seamCost[i].append(min(seamCost[i - 1][j - 1],
                                      seamCost[i - 1][j],
                                      seamCost[i - 1][j + 1]) + energyImage[i][j])
    #We now have a matrix that contains the cost of the seam to each pixel for each scanline,
    #to determine the least expensive seam just pick the pixel with the smallest value in the last
    #scanline (there may be more than one), and to remove it, repeat the algorithm in reverse removing
    #the corresponding pixels

    #print(seamCost[len(energyImage) - 1])

    #ImageUtility.printChannel(seamCost, "Coste")

    #print("")

    #ImageUtility.printChannel(energyImage, "Energía")

    #print("")

    #print("Seam cost generation finished")

    minElement = min(seamCost[len(energyImage) - 1])
    indexOfMin = seamCost[len(energyImage) - 1].index(minElement)
    previousIndex = indexOfMin

    #Reverse search, removing elements after we find the next
    for i in range(len(energyImage) - 1, -1, -1):

        #print("Min: ", minElement, "Line: ", i, "Index: ", indexOfMin)

        #The search for the index is restricted to the 3 elements from which the minimum
        #element was extracted since there could be another element of the same value in
        #other position of the scanline and we dont want that to be returned. Maybe 2 or even
        #the 3 of them have the same value, thats irrelevant as then all the routes would yield
        #a result of the same value
        if indexOfMin == 0:
            minElement = min(seamCost[i - 1][indexOfMin],
                             seamCost[i - 1][indexOfMin + 1])
            energyImage[i].pop(indexOfMin)
            imageRGB[i].pop(indexOfMin)
            previousIndex = indexOfMin
            indexOfMin = seamCost[i - 1].index(minElement, previousIndex, previousIndex + 2)

        elif indexOfMin == len(seamCost[0]) - 1:
            minElement = min(seamCost[i - 1][indexOfMin - 1],
                             seamCost[i - 1][indexOfMin])
            energyImage[i].pop(indexOfMin)
            imageRGB[i].pop(indexOfMin)
            previousIndex = indexOfMin
            indexOfMin = seamCost[i - 1].index(minElement, previousIndex - 1, previousIndex + 1)

        else:
            minElement = min(seamCost[i - 1][indexOfMin - 1],
                             seamCost[i - 1][indexOfMin],
                             seamCost[i - 1][indexOfMin + 1])
            energyImage[i].pop(indexOfMin)
            imageRGB[i].pop(indexOfMin)
            previousIndex = indexOfMin
            indexOfMin = seamCost[i - 1].index(minElement, previousIndex - 1, previousIndex + 2)

    #ImageUtility.printChannel(seamCost, "Coste final")

    #ImageUtility.printChannel(energyImage, "Energía final")

    #print("Backtracking finished")
    return energyImage, imageRGB

#Calculates the minimal seams in an image and marks them red (not the same thing
#shown in typical examples, those mark in red the removed seams in succesive steps)
def drawSeams(energyImage, imageRGB):
    imageSeams = copy.deepcopy(imageRGB)
    # PROVISIONAL UNTIL I WRITE THE DECODER FOR TYPE 0 COLOR AND THE RECEIVED IMAGE
    # IS ALREADY GREYSCALE
    if (type(energyImage[0][0]) != int):
        energyImage = getGreyscale(energyImage)
    # print("Seam cost generation started")
    seamCost = []
    # Initializing the values of the pixels in the top scanline
    seamCost.append(energyImage[0])
    # Now, iterate through all the rows from row 2 to n and through
    # all the pixels in each row
    for i in range(1, len(energyImage)):
        seamCost.append([])
        for j in range(len(energyImage[0])):
            # Compute the minimum seam cost up to each pixel of the row
            if j == 0:
                seamCost[i].append(min(seamCost[i - 1][j],
                                       seamCost[i - 1][j + 1]) + energyImage[i][j])
            elif j == len(energyImage[0]) - 1:
                seamCost[i].append(min(seamCost[i - 1][j - 1],
                                       seamCost[i - 1][j]) + energyImage[i][j])
            else:
                seamCost[i].append(min(seamCost[i - 1][j - 1],
                                       seamCost[i - 1][j],
                                       seamCost[i - 1][j + 1]) + energyImage[i][j])
    # We now have a matrix that contains the cost of the seam to each pixel for each scanline,
    # to determine the least expensive seam just pick the pixel with the smallest value in the last
    # scanline (there may be more than one), and to remove it, repeat the algorithm in reverse removing
    # the corresponding pixels

    for j in range(len(energyImage[0])):
        pixel = seamCost[len(energyImage) - 1][j]
        indexOfPixel = seamCost[len(energyImage) - 1].index(pixel, j, j + 1)
        previousIndex = indexOfPixel
        for i in range(len(energyImage) - 1, -1, -1):
            if indexOfPixel == 0:
                pixel = min(seamCost[i - 1][indexOfPixel],
                                 seamCost[i - 1][indexOfPixel + 1])
                imageSeams[i][indexOfPixel] = (255,0,0)
                previousIndex = indexOfPixel
                indexOfPixel = seamCost[i - 1].index(pixel, previousIndex, previousIndex + 2)

            elif indexOfPixel == len(seamCost[0]) - 1:
                pixel = min(seamCost[i - 1][indexOfPixel - 1],
                                 seamCost[i - 1][indexOfPixel])
                imageSeams[i][indexOfPixel] = (255, 0, 0)
                previousIndex = indexOfPixel
                indexOfPixel = seamCost[i - 1].index(pixel, previousIndex - 1, previousIndex + 1)

            else:
                pixel = min(seamCost[i - 1][indexOfPixel - 1],
                                 seamCost[i - 1][indexOfPixel],
                                 seamCost[i - 1][indexOfPixel + 1])
                imageSeams[i][indexOfPixel] = (255, 0, 0)
                previousIndex = indexOfPixel
                indexOfPixel = seamCost[i - 1].index(pixel, previousIndex - 1, previousIndex + 2)

    imageSeams = drawChosenSeam(energyImage, seamCost, imageSeams)

    return imageSeams

#Paints the minimal cost seam in a glorious yellow
def drawChosenSeam(energyImage, seamCost, imageSeams):
    minElement = min(seamCost[len(energyImage) - 1])
    indexOfMin = seamCost[len(energyImage) - 1].index(minElement)
    previousIndex = indexOfMin
    for i in range(len(energyImage) - 1, -1, -1):
        if indexOfMin == 0:
            minElement = min(seamCost[i - 1][indexOfMin],
                        seamCost[i - 1][indexOfMin + 1])
            imageSeams[i][indexOfMin] = (255, 255, 0)
            previousIndex = indexOfMin
            indexOfMin = seamCost[i - 1].index(minElement, previousIndex, previousIndex + 2)

        elif indexOfMin == len(seamCost[0]) - 1:
            minElement = min(seamCost[i - 1][indexOfMin - 1],
                        seamCost[i - 1][indexOfMin])
            imageSeams[i][indexOfMin] = (255, 255, 0)
            previousIndex = indexOfMin
            indexOfMin = seamCost[i - 1].index(minElement, previousIndex - 1, previousIndex + 1)

        else:
            minElement = min(seamCost[i - 1][indexOfMin - 1],
                        seamCost[i - 1][indexOfMin],
                        seamCost[i - 1][indexOfMin + 1])
            imageSeams[i][indexOfMin] = (255, 255, 0)
            previousIndex = indexOfMin
            indexOfMin = seamCost[i - 1].index(minElement, previousIndex - 1, previousIndex + 2)

    return imageSeams

#Returns an RGB version of a greyscale image, esentially, returns a 3 channel
#image with the same value in the 3 channels of each pixel
def getRGBVersion(imageGrey):
    rgbImage = []
    for i in range(len(imageGrey)):
        rgbImage.append([])
        for j in range(len(imageGrey[0])):
            rgbImage[i].append((imageGrey[i][j], imageGrey[i][j], imageGrey[i][j]))
    return rgbImage

# Returns an int matrix for each of the color channels in imageRGB
def getSeparateChannels(imageRGB):
    imageR = []
    imageG = []
    imageB = []

    for i in range(len(imageRGB)):
        imageR.append([])
        imageG.append([])
        imageB.append([])
        for j in range(len(imageRGB[0])):
            imageR[i].append(imageRGB[i][j][0])
            imageG[i].append(imageRGB[i][j][1])
            imageB[i].append(imageRGB[i][j][2])

    return (imageR, imageG, imageB)

# prints a RGB image, represented as a 3-tuple matrix
def printImage(imageRGB):
    for i in range(len(imageRGB)):
        print("")
        for j in range(len(imageRGB[0])):
            print("%21s" % (imageRGB[i][j],), end=" ")

    print("\n\n8 bit channel values:")
    for i in range(len(imageRGB)):
        print("")
        for j in range(len(imageRGB[0])):
            print("(", end="")
            for n in range(len(imageRGB[0][0])):
                print(imageRGB[i][j][n] // 256, end=" ")
            print(")", end="")

# Prints an image channel, represented as an int matrix, prints printMessage
# before the matrix
def printChannel(channel, printMessage):
    print("\n\n", printMessage, end="")
    for i in range(len(channel)):
        print("")
        for j in range(len(channel[0])):
            print("%5d" % channel[i][j], end=" ")

# the energy of each pixel is calculated as the sum of the intensity difference between
# the previous and next pixels in both x and y axis, for the pixels in the border of the
# image, the intensity of the pixels that would be outside the image is taken as the intensity
# of the pixel in the border
# The intensity difference in x and y is divided by 2, since the value could overflow the
# bit depth used to codify the image
def getEnergy(image):
    energyMatrix = []
    for i in range(len(image)):
        energyMatrix.append([])
        for j in range(len(image[i])):
            pixelEnergyX = 0
            pixelEnergyY = 0
            if i == 0 or i == len(image) - 1:
                if i == 0:
                    pixelEnergyY = abs(image[i][j] - image[i + 1][j])
                if i == len(image) - 1:
                    pixelEnergyY = abs(image[i - 1][j] - image[i][j])
            else:
                pixelEnergyY = abs(image[i - 1][j] - image[i + 1][j])

            if j == 0 or j == len(image[i]) - 1:
                if j == 0:
                    pixelEnergyX = abs(image[i][j] - image[i][j + 1])
                if j == len(image[i]) - 1:
                    pixelEnergyX = abs(image[i][j - 1] - image[i][j])
            else:
                pixelEnergyX = abs(image[i][j - 1] - image[i][j + 1])

            energyMatrix[i].append(pixelEnergyX // 2 + pixelEnergyY // 2)

    return energyMatrix

#Calcula el gradiente de la imagen como la raiz de la magnitud en (y/2)^2 + (x/2)^2
def getEnergyWithRoot(image):
    energyMatrix = []
    for i in range(len(image)):
        energyMatrix.append([])
        for j in range(len(image[i])):
            pixelEnergyX = 0
            pixelEnergyY = 0
            if i == 0 or i == len(image) - 1:
                if i == 0:
                    pixelEnergyY = abs(image[i][j] - image[i + 1][j])
                if i == len(image) - 1:
                    pixelEnergyY = abs(image[i - 1][j] - image[i][j])
            else:
                pixelEnergyY = abs(image[i - 1][j] - image[i + 1][j])

            if j == 0 or j == len(image[i]) - 1:
                if j == 0:
                    pixelEnergyX = abs(image[i][j] - image[i][j + 1])
                if j == len(image[i]) - 1:
                    pixelEnergyX = abs(image[i][j - 1] - image[i][j])
            else:
                pixelEnergyX = abs(image[i][j - 1] - image[i][j + 1])

            energyMatrix[i].append(math.floor(math.sqrt(( pixelEnergyX // 2)**2 + (pixelEnergyY // 2)**2 )))

    return energyMatrix

# The energy of a pixel in this function is the sum of the gradients in both x
# and y axis module the number of bits per channel(So it doesn't overflow), this
# way, a big change in one axis with a small change in the other will get a big
# energy value
def getEnergyUsingModule(image, bitDepth):
    # the energy of each pixel is calculated as the sum of the intensity difference between
    # the previous and next pixels in both x and y axis, for the pixels in the border of the
    # image, the intensity of the pixels that would be outside the image is taken as the intensity
    # of the pixel in the border
    bitsPerChannel = 2 ** bitDepth
    energyMatrix = []
    for i in range(len(image)):
        energyMatrix.append([])
        for j in range(len(image[i])):
            pixelEnergyX = 0
            pixelEnergyY = 0
            if i == 0 or i == len(image) - 1:
                if i == 0:
                    pixelEnergyY = abs(image[i][j] - image[i + 1][j])
                if i == len(image) - 1:
                    pixelEnergyY = abs(image[i - 1][j] - image[i][j])
            else:
                pixelEnergyY = abs(image[i - 1][j] - image[i + 1][j])

            if j == 0 or j == len(image[i]) - 1:
                if j == 0:
                    pixelEnergyX = abs(image[i][j] - image[i][j + 1])
                if j == len(image[i]) - 1:
                    pixelEnergyX = abs(image[i][j - 1] - image[i][j])
            else:
                pixelEnergyX = abs(image[i][j - 1] - image[i][j + 1])

            energyMatrix[i].append((pixelEnergyX + pixelEnergyY) % bitsPerChannel)

    return energyMatrix

# Returns the greyscale version of imageRGB, obtained by adding the values of all 3
# color channels into a single channel (divided by 3, so the result doesn't overflow)
def getGreyscale(imageRGB):
    greyscaleImage = []
    (imageR, imageG, imageB) = getSeparateChannels(imageRGB)
    # Combining the channels into a single greyscale image
    for i in range(len(imageR)):
        greyscaleImage.append([])
        for j in range(len(imageR[0])):
            greyscaleImage[i].append(imageR[i][j] // 3 + imageG[i][j] // 3 + imageB[i][j] // 3)
    return greyscaleImage

# Gets an energy matrix for each channel in imageRGB and combines them into a
# single greyscale image
def getEnergyRGB(imageRGB):
    (imageR, imageG, imageB) = getSeparateChannels(imageRGB)
    energyR = getEnergy(imageR)
    energyG = getEnergy(imageG)
    energyB = getEnergy(imageB)
    energyImage = combineEnergyChannels(energyR, energyG, energyB)
    return energyImage

#Uses the version of the gradient using the square root of the gradients in both directions
def getEnergyRGBWithRoot(imageRGB):
    (imageR, imageG, imageB) = getSeparateChannels(imageRGB)
    energyR = getEnergyWithRoot(imageR)
    energyG = getEnergyWithRoot(imageG)
    energyB = getEnergyWithRoot(imageB)
    energyImage = combineEnergyChannels(energyR, energyG, energyB)
    return energyImage

def getEnergyRGBWithMod(imageRGB, bitDepth):
    (imageR, imageG, imageB) = getSeparateChannels(imageRGB)
    energyR = getEnergy(imageR)
    energyG = getEnergy(imageG)
    energyB = getEnergy(imageB)
    energyImage = combineEnergyChannelsMod(energyR, energyG, energyB, bitDepth)
    return energyImage

# Combines the channels mod 2^BitDepth and uses mod 2^BitDepth for the value of the gradient
def getEnergyRGBWithFullMod(imageRGB, bitDepth):
    (imageR, imageG, imageB) = getSeparateChannels(imageRGB)
    energyR = getEnergyUsingModule(imageR, bitDepth)
    energyG = getEnergyUsingModule(imageG, bitDepth)
    energyB = getEnergyUsingModule(imageB, bitDepth)
    energyImage = combineEnergyChannelsMod(energyR, energyG, energyB, bitDepth)
    return energyImage

# Combines the channels /3 and uses mod 2^BitDepth for the value of the gradient
def getEnergyRGBWithGradientMod(imageRGB, bitDepth):
    (imageR, imageG, imageB) = getSeparateChannels(imageRGB)
    energyR = getEnergyUsingModule(imageR, bitDepth)
    energyG = getEnergyUsingModule(imageG, bitDepth)
    energyB = getEnergyUsingModule(imageB, bitDepth)
    energyImage = combineEnergyChannels(energyR, energyG, energyB)
    return energyImage

#Receives 3 energy matrices and returns a single greyscale image obtaines by adding
#the 3, each divided by 3 so the result doesn't overflow the bit depth
def combineEnergyChannels(energyR, energyG, energyB):
    energyImage = []
    for i in range(len(energyR)):
        energyImage.append([])
        for j in range(len(energyR[0])):
            energyImage[i].append(energyR[i][j] // 3 + energyG[i][j] // 3 + energyB[i][j] // 3)
    return energyImage

# Receives 3 energy matrices and returns a single greyscale image obtaines by adding
# the 3 and dividing module the number of bits per channel
def combineEnergyChannelsMod(energyR, energyG, energyB, bitDepth):
    # In this version, an important change in any of the channels results in a higher intensity for that
    # pixel, whereas, if we give the same weight to all channels a big change in one of them with small
    # changes in the others may go unnoticed
    bitsPerChannel = 2 ** bitDepth
    energyImage = []
    for i in range(len(energyR)):
        energyImage.append([])
        for j in range(len(energyR[0])):
            energyImage[i].append((energyR[i][j] + energyG[i][j] + energyB[i][j]) % bitsPerChannel)
    return energyImage

