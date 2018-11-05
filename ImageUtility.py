import png
import functools
import ImageUtility
import copy
import math
from datetime import *
from scipy import ndimage

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
def getSeamCostAlt(energyImage):
    outer_for_iterations = 0
    inner_for_iterations = 0

    startTime = datetime.now()

    seamCost = []
    seamCost = copy.copy(energyImage)

    # Now, iterate through all the rows from row 2 to n and through
    # all the pixels in each row
    for i in range(1, len(energyImage)):

        prevRow = i - 1

        # Cost at the first pixel of the row, computed here for efficiency
        seamCost[i][0] = min(seamCost[prevRow][0], seamCost[prevRow][1]) + energyImage[i][0]

        for j in range(1 , len(energyImage[0]) - 1):
            # Compute the minimum seam cost up to each pixel of the row
            seamCost[i][j] = min(seamCost[prevRow][j - 1],
                                   seamCost[prevRow][j],
                                   seamCost[prevRow][j + 1]) + energyImage[i][j]

        #Cost at the last pixel of the row, computed here for efficiency
        seamCost[i][len(energyImage[0]) - 1] = min(seamCost[prevRow][len(energyImage[0]) - 1 - 1],
                                seamCost[prevRow][len(energyImage[0]) - 1]) + energyImage[i][len(energyImage[0]) - 1]

    endTime = datetime.now()
    timeDifference = endTime - startTime
    elapsedTimeMicro = timeDifference.microseconds + timeDifference.seconds * 1000000
    #print("Elapsed: %d" % elapsedTimeMicro)
    #print("Height: %d\nWidth: %d" % (len(energyImage), len(energyImage[0])))
    #print("Outer: %d\nInner: %d" % (outer_for_iterations, inner_for_iterations))

    return seamCost


#Returns an array indicating the cost of the less energy seam for each of the bottom-scanline pixels
#(Old)
def getSeamCost(energyImage):
    outer_for_iterations = 0
    inner_for_iterations = 0
    # PROVISIONAL UNTIL I WRITE THE DECODER FOR TYPE 0 COLOR AND THE RECEIVED IMAGE
    # IS ALREADY GREYSCALE
    if (type(energyImage[0][0]) != int):
        energyImage = getGreyscale(energyImage)

    startTime = datetime.now()
    seamCost = []
    # Initializing the values of the pixels in the top scanline
    seamCost.append(energyImage[0])
    # Now, iterate through all the rows from row 2 to n and through
    # all the pixels in each row
    for i in range(1, len(energyImage)):
        outer_for_iterations += 1
        seamCost.append([])
        for j in range(len(energyImage[0])):
            inner_for_iterations += 1
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

    endTime = datetime.now()
    timeDifference = endTime - startTime
    elapsedTimeMicro = timeDifference.microseconds + timeDifference.seconds * 1000000
    print("Elapsed: %d" % elapsedTimeMicro)
    print("Height: %d\nWidth: %d" % (len(energyImage), len(energyImage[0])))
    print("Outer: %d\nInner: %d" % (outer_for_iterations, inner_for_iterations))

    return seamCost

#Receives a multi-dimensional array containing the energy values from the pixels of imageRGB, another multi-
#dimensional array, and a last muñti-dimensional array which contains the minimum seam cost from each pixel
#to the top scanline, returns energyImage and imageRGB with the least cost seam removed
def removeMinimalSeamAlt(energyImage, imageRGB, seamCost):

    minElement = min(seamCost[len(energyImage) - 1])
    indexOfMin = seamCost[len(energyImage) - 1].index(minElement)
    previousIndex = indexOfMin

    #Reverse search, removing elements after we find the next
    for i in range(len(energyImage) - 1, -1, -1):
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

    return energyImage, imageRGB

#Receives a multi-dimensional array containing the energy values from the pixels of imageRGB, another multi-
#dimensional array, and a last muñti-dimensional array which contains the minimum seam cost from each pixel
#to the top scanline, returns energyImage and imageRGB with the least cost seam removed
def removeMinimalSeam(energyImage, imageRGB):
    seamCost = getSeamCostAlt(energyImage)
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

#Returns an RGB version of a greyscale image, essentially, returns a 3 channel
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

#Receives a greyscale image, or a channel from an RGB image, indistinctly, and returns an
#approximation to the values of the gradient (the derivatives with respect to x and y) computed
#using the Sobel-Feldman Operator
#https://en.wikipedia.org/wiki/Kernel_(image_processing)#Convolution
#https://en.wikipedia.org/wiki/Sobel_operator
def getSobelDerivativeApproximations(image):
    sobel_filter_x = [[1,0,-1],[2,0,-2],[1,0,-1]]
    sobel_filter_y = [[1,2,1],[0,0,0],[-1,-2,-1]]
    #By default, the convolution takes values outside of the array as being the same as the
    #border values
    #Derivatives with respect to x:
    dx = ndimage.convolve(image, sobel_filter_x)
    #Derivatives with respect to y
    dy = ndimage.convolve(image, sobel_filter_y)
    #Combine both matrices in a single matrix containing the approximations to the gradient
    #in each point
    result = []
    for i in range(len(dx)):
        result.append(list(zip(dx[i], dy[i])))
    return result


#Receives an approximation to the gradient values in each pixel of an image, that is the
#values of the derivatives with respect to both x and y for each pixel, and computes the energy
#as being the sum of the absolute values of both derivatives.
#Note that the values returned may be well over the bit depth range
def getSimpleEnergy(gradient):
    energyMatrix = []
    for i in range(len(gradient)):
        energyMatrix.append([])
        for j in range(len(gradient[i])):
            energyMatrix[i].append(abs(gradient[i][j][0]) + abs(gradient[i][j][1]))

    return energyMatrix

#Receives an approximation to the gradient values in each pixel of an image, that is the
#values of the derivatives with respect to both x and y for each pixel.
#Computes the energy of a pixel as the root of the squares of the gradient components in both
#x and y, ((dy/2)^2 + (dx/2)^2), that is, the gradient's module
#Note that the values returned may be well over the bit depth range
def getEnergyAsModule(gradient):
    energyMatrix = []
    for i in range(len(gradient)):
        energyMatrix.append([])
        for j in range(len(gradient[i])):
            energyMatrix[i].append(math.floor(abs(math.sqrt((gradient[i][j][0])**2) +
                                                abs((gradient[i][j][1])**2 ))))

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


#Gets an energy matrix for each channel in imageRGB using the formula in the getSimpleEnergy function,
#sums them and returns a single energy matrix for the whole image
#Note that the values returned may be well over the bit depth range and not be suitable for a greyscale
#representation of the energy
def getSimpleEnergyRGB(imageRGB):
    (imageR, imageG, imageB) = getSeparateChannels(imageRGB)
    gradientR = getSobelDerivativeApproximations(imageR)
    gradientG = getSobelDerivativeApproximations(imageG)
    gradientB = getSobelDerivativeApproximations(imageB)
    energyR = getSimpleEnergy(gradientR)
    energyG = getSimpleEnergy(gradientG)
    energyB = getSimpleEnergy(gradientB)
    energyImage = combineEnergyChannels(energyR, energyG, energyB)
    return energyImage

#Gets an energy matrix for each channel in imageRGB using the formula in the getEnergyAsModule function,
#that is, the energy of a pixel as the module of the gradient in that point, sums them and returns a single
#energy matrix for the whole image
#Note that the values returned may be well over the bit depth range and not be suitable for a greyscale
#representation of the energy
def getEnergyRGBAsModule(imageRGB):
    (imageR, imageG, imageB) = getSeparateChannels(imageRGB)
    gradientR = getSobelDerivativeApproximations(imageR)
    gradientG = getSobelDerivativeApproximations(imageG)
    gradientB = getSobelDerivativeApproximations(imageB)
    energyR = getEnergyAsModule(gradientR)
    energyG = getEnergyAsModule(gradientG)
    energyB = getEnergyAsModule(gradientB)
    energyImage = combineEnergyChannels(energyR, energyG, energyB)
    return energyImage

#Gets the energy matrices from all 3 channels and combines them, fitting the values to the range
#[0, 2 ** bitDepth] so the result is suitable for storing as an image with a certain bitDepth and the
#values don't overflow
def getSimpleEnergyRGBInRange(imageRGB, bitDepth):
    bitsPerChannel = 2 ** bitDepth
    (imageR, imageG, imageB) = getSeparateChannels(imageRGB)
    gradientR = getSobelDerivativeApproximations(imageR)
    gradientG = getSobelDerivativeApproximations(imageG)
    gradientB = getSobelDerivativeApproximations(imageB)
    energyR = getSimpleEnergy(gradientR)
    energyG = getSimpleEnergy(gradientG)
    energyB = getSimpleEnergy(gradientB)
    energyImage = combineEnergyChannels(energyR, energyG, energyB)
    #We now have to fit the values in energyImage to the range 0-bitDepth ** 2
    minEnergy = min([min(row) for row in energyImage])
    maxEnergy = max([max(row) for row in energyImage])

    for i in range(len(energyImage)):
        for j in range(len(energyImage[0])):
            energyImage[i][j] = ((bitsPerChannel-1) * (energyImage[i][j] - minEnergy))//(maxEnergy - minEnergy)
            #I found this formula in:
            #https://stackoverflow.com/questions/5294955/how-to-scale-down-a-range-of-numbers-with-a-known-min-and-max-value
    return energyImage

#Gets the energy matrices from all 3 channels and combines them module 2**BitDepth, so
#The result is suitable for storing as an image with a certain bitDepth and the values don't
#overflow
def getEnergyRGBAsModuleInRange(imageRGB, bitDepth):
    bitsPerChannel = 2 ** bitDepth
    (imageR, imageG, imageB) = getSeparateChannels(imageRGB)
    gradientR = getSobelDerivativeApproximations(imageR)
    gradientG = getSobelDerivativeApproximations(imageG)
    gradientB = getSobelDerivativeApproximations(imageB)
    energyR = getEnergyAsModule(gradientR)
    energyG = getEnergyAsModule(gradientG)
    energyB = getEnergyAsModule(gradientB)
    energyImage = combineEnergyChannels(energyR, energyG, energyB)
    # We now have to fit the values in energyImage to the range 0-bitDepth ** 2
    minEnergy = min([min(row) for row in energyImage])
    maxEnergy = max([max(row) for row in energyImage])

    for i in range(len(energyImage)):
        for j in range(len(energyImage[0])):
            energyImage[i][j] = ((bitsPerChannel - 1) * (energyImage[i][j] - minEnergy)) // (maxEnergy - minEnergy)
            # I found this formula in:
            # https://stackoverflow.com/questions/5294955/how-to-scale-down-a-range-of-numbers-with-a-known-min-and-max-value
    return energyImage

#Receives 3 energy matrices and returns the sum of all 3, the values returned are not constrained by bit
#depth or any other consideration, they are simply the sum of the corresponding values from all matrices
def combineEnergyChannels(energyR, energyG, energyB):
    energySum = []
    for i in range(len(energyR)):
        energySum.append([])
        for j in range(len(energyR[0])):
            energySum[i].append(energyR[i][j] + energyG[i][j] + energyB[i][j])
    return energySum


