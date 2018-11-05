from PNGDecoder import PNGDecoder
import png
import ImageUtility

def generateEnergyImages(filename, imageType):
    decoder = PNGDecoder("Assets\\" + filename + ".png")
    decoder.printParameters()
    bitDepth = decoder.getBitDepth()
    imageRGB = decoder.getRGBImage()

    if imageType == "Greyscale":
        print("Greyscale start")
        greyscaleImage = ImageUtility.getGreyscale(imageRGB)
        print("Greyscale end")

        encodedImage = []
        if bitDepth == 8:
            encodedImage = png.from_array(greyscaleImage, "L;8")
        elif bitDepth == 16:
            encodedImage = png.from_array(greyscaleImage, "L;16")
        encodedImage.save("Results\\" + filename + "\\greyscaleVersion.png")

        #print("Greyscale energy start")
        #greyScaleEnergy = ImageUtility.getSimpleEnergy(greyscaleImage)
        #Now we would need to divide all values in greyscale energy module 2**BitDepth so
        #they don't overflow, but this is disabled for now, as the benefits from stracting
        #the energy from a greycale version of the image in contrast with obtaining them from the
        #RGB version are not clear
        #greyScaleEnergy = ImageUtility.getRGBVersion(greyScaleEnergy)
        #print("Greyscale energy end")
        #if bitDepth == 8:
        #    encodedImage = png.from_array(greyScaleEnergy, "RGB;8")
        #elif bitDepth == 16:
        #    encodedImage = png.from_array(greyScaleEnergy, "RGB;16")
        #encodedImage.save("Results\\" + filename + "\\energyFromGreyScale.png")

        #del(greyScaleEnergy)
        #del(greyscaleImage)

    if imageType == "Simple":
        print("Simple energy start")
        energy = ImageUtility.getSimpleEnergyRGBInRange(imageRGB, bitDepth)
        #An RGB color version is saved instead of the greyscale as my png decoder
        #does not provide greyscale decoding functionality yet
        energy = ImageUtility.getRGBVersion(energy)
        print("Simple energy end")
        encodedImage = None
        if bitDepth == 8:
            encodedImage = png.from_array(energy, "RGB;8")
        elif bitDepth == 16:
            encodedImage = png.from_array(energy, "RGB;16")
        encodedImage.save("Results\\" + filename + "\\simple_energy.png")

        del(energy)

    if imageType == "Module":
        print("Module energy start")
        energy = ImageUtility.getEnergyRGBAsModuleInRange(imageRGB, bitDepth)
        #An RGB color version is saved instead of the greyscale as my png decoder
        #does not provide greyscale decoding functionality yet
        energy = ImageUtility.getRGBVersion(energy)
        print("Module energy end")
        encodedImage = None
        if bitDepth == 8:
            encodedImage = png.from_array(energy, "RGB;8")
        elif bitDepth == 16:
            encodedImage = png.from_array(energy, "RGB;16")
        encodedImage.save("Results\\" + filename + "\\module_energy.png")

        del(energy)


######################### MAIN ##############################
imageName = "suiza_cuarto"

#generateEnergyImages(imageName, "Simple")
#generateEnergyImages(imageName, "Module")

decoder = PNGDecoder("Assets\\" + imageName + ".png")
imageRGB = decoder.getRGBImage()
print("Computing image energy")
energy = ImageUtility.getEnergyRGBAsModule(imageRGB)
#energy = ImageUtility.getSimpleEnergyRGB(imageRGB)
#energy = ImageUtility.getSimpleEnergyRGBInRange(imageRGB, 8)
print("Finished image energy")

#Draw seams in the initial image
#seamsImage = ImageUtility.drawSeams(energy, imageRGB)
#encodedImage = png.from_array(seamsImage, "RGB;8")
#encodedImage.save("Results\\seamsRGB.png")

#remove some seams
for i in range(200):
    print(i)
    #Draw seams in the image
    #seamsImage = ImageUtility.drawSeams(energyImage, imageRGB)
    #encodedImage = png.from_array(seamsImage, "RGB;8")
    #filename = "Results\\" + imageName + "\\SeamSelection\\" + str(i) + ".png"
    #encodedImage.save(filename)
    energy, imageRGB = ImageUtility.removeMinimalSeam(energy, imageRGB)

encodedImage = png.from_array(imageRGB, "RGB;8")
encodedImage.save("Results\\" + imageName + "\\seamCarved.png")



























