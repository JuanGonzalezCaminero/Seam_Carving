from PNGDecoder import PNGDecoder
import png
import  ImageUtility

def generateEnergyImages(filename):
    decoder = PNGDecoder("Assets\\" + filename + ".png")
    decoder.printParameters()
    bitDepth = decoder.getBitDepth()
    imageRGB = decoder.getRGBImage()

    print("Greyscale start")
    greyscaleImage = ImageUtility.getGreyscale(imageRGB)
    print("Greyscale end")

    encodedImage = []
    if bitDepth == 8:
        encodedImage = png.from_array(greyscaleImage, "L;8")
    elif bitDepth == 16:
        encodedImage = png.from_array(greyscaleImage, "L;16")
    encodedImage.save("Results\\greyscaleVersion.png")

    print("Greyscale energy start")
    greyScaleEnergy = ImageUtility.getEnergy(greyscaleImage)
    greyScaleEnergy = ImageUtility.getRGBVersion(greyScaleEnergy)
    print("Greyscale energy end")
    if bitDepth == 8:
        encodedImage = png.from_array(greyScaleEnergy, "RGB;8")
    elif bitDepth == 16:
        encodedImage = png.from_array(greyScaleEnergy, "RGB;16")
    encodedImage.save("Results\\energyFromGreyScale.png")

    del(greyScaleEnergy)
    del(greyscaleImage)

    print("RGB energy start")
    energyRGB = ImageUtility.getEnergyRGB(imageRGB)
    energyRGB = ImageUtility.getRGBVersion(energyRGB)
    print("RGB energy end")
    if bitDepth == 8:
        encodedImage = png.from_array(energyRGB, "RGB;8")
    elif bitDepth == 16:
        encodedImage = png.from_array(energyRGB, "RGB;16")
    encodedImage.save("Results\\energyFromRGB.png")

    del(energyRGB)

    print("RGB mod energy start")
    energyRGBMod = ImageUtility.getEnergyRGBWithMod(imageRGB, bitDepth)
    energyRGBMod = ImageUtility.getRGBVersion(energyRGBMod)
    print("RGB mod energy end")
    if bitDepth == 8:
        encodedImage = png.from_array(energyRGBMod, "RGB;8")
    elif bitDepth == 16:
        encodedImage = png.from_array(energyRGBMod, "RGB;16")
    encodedImage.save("Results\\energyFromRGBWithMod.png")

    del(energyRGBMod)

    print("RGB mod mod energy start")
    energyRGBFullMod = ImageUtility.getEnergyRGBWithFullMod(imageRGB, bitDepth)
    energyRGBFullMod = ImageUtility.getRGBVersion(energyRGBFullMod)
    print("RGB mod mod energy end")
    if bitDepth == 8:
        encodedImage = png.from_array(energyRGBFullMod, "RGB;8")
    elif bitDepth == 16:
        encodedImage = png.from_array(energyRGBFullMod, "RGB;16")
    encodedImage.save("Results\\energyFromRGBFullMod.png")

######################### MAIN ##############################
decoder = PNGDecoder("Results\\energyFromRGBFullMod.png")
decoder2 = PNGDecoder("Assets\\castillo.png")
energyImage = decoder.getRGBImage()
imageRGB = decoder2.getRGBImage()
#generateEnergyImages("castillo")

#remove some seams
for i in range(150):
    print(i)
    energyImage, imageRGB = ImageUtility.removeMinimalSeam(energyImage, imageRGB)

encodedImage = png.from_array(imageRGB, "RGB;8")
encodedImage.save("Results\\seamCarvedFullMod.png")



























