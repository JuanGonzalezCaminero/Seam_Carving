from PNGDecoder import PNGDecoder
import png

#We define the energy of a pixel as Ei = |dI/dx| + |dI/dy|, being I the
#energy function of the image, a multivariate function that provides the intensity
#values for the image (in a greyscale image, in a RGB image we would have 3 separate functions)
#We only know the values obtained from the evaluation of this function in each of the pixels

#Returns an int matrix for each of the color channels in imageRGB
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

#prints a RGB image, represented as a 3-tuple matrix
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

#Prints an image channel, represented as an int matrix, prints printMessage
#before the matrix
def printChannel(channel, printMessage):
    print("\n\n", printMessage, end="")
    for i in range(len(channel)):
        print("")
        for j in range(len(channel[0])):
            print("%5d" % channel[i][j], end=" ")

#the energy of each pixel is calculated as the sum of the intensity difference between
#the previous and next pixels in both x and y axis, for the pixels in the border of the
#image, the intensity of the pixels that would be outside the image is taken as the intensity
#of the pixel in the border
#The intensity difference in x and y is divided by 2, since the value could overflow the
#bit depth used to codify the image
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

            energyMatrix[i].append(pixelEnergyX//2 + pixelEnergyY//2)

    return energyMatrix

#The energy of a pixel in this function is the sum of the gradients in both x
#and y axis module the number of bits per channel(So it doesn't overflow), this
#way, a big change in one axis with a small change in the other will get a big
#energy value
def getEnergyUsingModule(image, bitDepth):
    #the energy of each pixel is calculated as the sum of the intensity difference between
    #the previous and next pixels in both x and y axis, for the pixels in the border of the
    #image, the intensity of the pixels that would be outside the image is taken as the intensity
    #of the pixel in the border
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

            energyMatrix[i].append((pixelEnergyX + pixelEnergyY)%bitsPerChannel)

    return energyMatrix

#Returns the greyscale version of imageRGB, obtained by adding the values of all 3
#color channels into a single channel (divided by 3, so the result doesn't overflow)
def getGreyscale(imageRGB):
    greyscaleImage = []
    (imageR, imageG, imageB) = getSeparateChannels(imageRGB)
    # Combining the channels into a single greyscale image
    for i in range(len(imageR)):
        greyscaleImage.append([])
        for j in range(len(imageR[0])):
            greyscaleImage[i].append(imageR[i][j] // 3 + imageG[i][j] // 3 + imageB[i][j] // 3)
    return greyscaleImage

#Gets an energy matrix for each channel in imageRGB and combines them into a
#single greyscale image
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

#Receives 3 energy matrices and returns a single greyscale image obtaines by adding
#the 3, each divided by 3 so the result doesn't overflow the bit depth
def combineEnergyChannels(energyR, energyG, energyB):
    energyImage = []
    for i in range(len(energyR)):
        energyImage.append([])
        for j in range(len(energyR[0])):
            energyImage[i].append(energyR[i][j]//3 + energyG[i][j]//3 + energyB[i][j]//3)
    return energyImage

#Receives 3 energy matrices and returns a single greyscale image obtaines by adding
#the 3 and dividing module the number of bits per channel
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

######################### MAIN ##############################

decoder = PNGDecoder("Assets\\calle.png")
decoder.printParameters()
bitDepth = decoder.getBitDepth()
imageRGB = decoder.getRGBImage()

greyscaleImage = getGreyscale(imageRGB)

encodedImage = []
if bitDepth == 8:
    encodedImage = png.from_array(greyscaleImage, "L;8")
elif bitDepth == 16:
    encodedImage = png.from_array(greyscaleImage, "L;16")
encodedImage.save("Results\\greyscaleVersion.png")

greyScaleEnergy = getEnergy(greyscaleImage)
if bitDepth == 8:
    encodedImage = png.from_array(greyScaleEnergy, "L;8")
elif bitDepth == 16:
    encodedImage = png.from_array(greyScaleEnergy, "L;16")
encodedImage.save("Results\\energyFromGreyScale.png")

energyRGB = getEnergyRGB(imageRGB)
if bitDepth == 8:
    encodedImage = png.from_array(energyRGB, "L;8")
elif bitDepth == 16:
    encodedImage = png.from_array(energyRGB, "L;16")
encodedImage.save("Results\\energyFromRGB.png")

energyRGBMod = getEnergyRGBWithMod(imageRGB, bitDepth)
if bitDepth == 8:
    encodedImage = png.from_array(energyRGBMod, "L;8")
elif bitDepth == 16:
    encodedImage = png.from_array(energyRGBMod, "L;16")
encodedImage.save("Results\\energyFromRGBWithMod.png")


















