import png

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
def getSeamCost(energyImage):
    #PROVISIONAL UNTIL I WRITE THE DECODER FOR TYPE 0 COLOR AND THE RECEIVED IMAGE
    #IS ALREADY GREYSCALE
    energyImage = getGreyscale(energyImage)
    #Initializing the values of the pixels in the top scanline
    seamCost = energyImage[0]
    previousSeamCost = energyImage[0]
    #The indexes of he pixels within each row that are chosen in each iteration
    #are stored here so we have a means for reconstructing the solution after computing
    #the optimal cost
    chosenPixels = []
    #Now, iterate through all the rows from row 2 to n and through
    #all the pixels in each row
    for i in range(1, len(energyImage)):
            chosenPixels.append([])
            for j in range(len(energyImage[0])):
                #Compute the minimum seam cost up to each pixel of the row
                if(j == 0):
                    seamCost[j] = min(previousSeamCost[j],
                                      previousSeamCost[j + 1]) + energyImage[i][j]
                if(j == len(energyImage[0]) - 1):
                    seamCost[j] = min(previousSeamCost[j - 1],
                                      previousSeamCost[j]) + energyImage[i][j]
                seamCost[j] = min(previousSeamCost[j - 1],
                                  previousSeamCost[j],
                                  previousSeamCost[j + 1]) + energyImage[i][j]
            previousSeamCost = seamCost
    return seamCost


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

# Receives 3 energy matrices and returns a single greyscale image obtaines by adding
# the 3, each divided by 3 so the result doesn't overflow the bit depth
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