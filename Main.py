from PNGDecoder import PNGDecoder
import png

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

def printChannel(channel, printMessage):
    print("\n\n", printMessage, end="")
    for i in range(len(channel)):
        print("")
        for j in range(len(channel[0])):
            print("%5d" % channel[i][j], end=" ")

def getEnergy(image):
    #the energy of each pixel is calculated as the sum of the intensity difference between
    #the previous and next pixels in both x and y axis, for the pixels in the border of the
    #image, the intensity of the pixels that would be outside the image is taken as the intensity
    #of the pixel in the border
    #The intensity difference in x and y is divided by 2, since the value could overflow the
    #bit depth used to codify the image
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

            energyMatrix[i].append(pixelEnergyX//2 + pixelEnergyY//2)

    return energyMatrix

######################### MAIN ##############################

decoder = PNGDecoder("Assets/portatil.png")

decoder.printParameters()
bitDepth = decoder.getBitDepth()
imageRGB = decoder.getRGBImage()
#printImage(imageRGB)

#If the image is rgb, we need the energy of the pixels for each channel
(imageR, imageG, imageB) = getSeparateChannels(imageRGB)

#printChannel(imageR, "R channel:")
#printChannel(imageG, "G channel:")
#printChannel(imageB, "B channel:")

#We define the energy of a pixel as Ei = |dI/dx| + |dI/dy|, being I the
#energy function of the image, a multivariate function that provides the intensity
#values for the image (in a greyscale image, in a RGB image we would have 3 separate functions)
#We only know the values obtained from the evaluation of this function in each of the pixels

#printChannel(energyR, "R energy:")
#printChannel(energyG, "G energy:")
#printChannel(energyB, "B energy:")

greyscaleImage = []
#Combining the channels into a single greyscale image
for i in range(len(imageR)):
    greyscaleImage.append([])
    for j in range(len(imageR[0])):
        greyscaleImage[i].append(imageR[i][j]//3 + imageG[i][j]//3 + imageB[i][j]//3)

#Getting the energy of the pixels
energyImage = getEnergy(greyscaleImage)


#printChannel(energyImage, "energy:")

#Using the png module to encode the new image
print("Encoding started")
encodedImage = png.from_array(energyImage, "L;8")
encodedImage.save("Assets/energyTest2.png")




















