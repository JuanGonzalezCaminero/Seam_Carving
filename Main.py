from PNGDecoder import PNGDecoder
import png
import  ImageUtility

######################### MAIN ##############################
decoder = PNGDecoder("Results\\energyFromRGB.png")
energyImage = decoder.getRGBImage()
ImageUtility.getSeamCost(energyImage)

decoder = PNGDecoder("Assets\\clara.png")
decoder.printParameters()
bitDepth = decoder.getBitDepth()
imageRGB = decoder.getRGBImage()

greyscaleImage = ImageUtility.getGreyscale(imageRGB)

encodedImage = []
if bitDepth == 8:
    encodedImage = png.from_array(greyscaleImage, "L;8")
elif bitDepth == 16:
    encodedImage = png.from_array(greyscaleImage, "L;16")
encodedImage.save("Results\\greyscaleVersion.png")

greyScaleEnergy = ImageUtility.getEnergy(greyscaleImage)
greyScaleEnergy = ImageUtility.getRGBVersion(greyScaleEnergy)
if bitDepth == 8:
    encodedImage = png.from_array(greyScaleEnergy, "RGB;8")
elif bitDepth == 16:
    encodedImage = png.from_array(greyScaleEnergy, "RGB;16")
encodedImage.save("Results\\energyFromGreyScale.png")

energyRGB = ImageUtility.getEnergyRGB(imageRGB)
energyRGB = ImageUtility.getRGBVersion(energyRGB)
if bitDepth == 8:
    encodedImage = png.from_array(energyRGB, "RGB;8")
elif bitDepth == 16:
    encodedImage = png.from_array(energyRGB, "RGB;16")
encodedImage.save("Results\\energyFromRGB.png")

energyRGBMod = ImageUtility.getEnergyRGBWithMod(imageRGB, bitDepth)
energyRGBMod = ImageUtility.getRGBVersion(energyRGBMod)
if bitDepth == 8:
    encodedImage = png.from_array(energyRGBMod, "RGB;8")
elif bitDepth == 16:
    encodedImage = png.from_array(energyRGBMod, "RGB;16")
encodedImage.save("Results\\energyFromRGBWithMod.png")

energyRGBFullMod = ImageUtility.getEnergyRGBWithFullMod(imageRGB, bitDepth)
energyRGBFullMod = ImageUtility.getRGBVersion(energyRGBFullMod)
if bitDepth == 8:
    encodedImage = png.from_array(energyRGBFullMod, "RGB;8")
elif bitDepth == 16:
    encodedImage = png.from_array(energyRGBFullMod, "RGB;16")
encodedImage.save("Results\\energyFromRGBFullMod.png")


















