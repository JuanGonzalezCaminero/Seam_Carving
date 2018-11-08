from PNGDecoder import PNGDecoder
import png
import ImageUtility
import tqdm
import os

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
        #they don't overflow, but this is disabled for now, as the benefits from extracting
        #the energy from a greyscale version of the image in contrast with obtaining them from the
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

######################### MAIN ##############################
#Run options:
#Image generation options, just to see the process
GENERATE_SIMPLE_ENERGY_IMAGE = 1
GENERATE_MODULE_ENERGY_IMAGE = 0
GENERATE_BLURRED = 1
GENERATE_SIMPLE_ENERGY_FROM_BLURRED = 1
GENERATE_MODULE_ENERGY_FROM_BLURRED = 0
GENERATE_GREYSCALE = 0
GENERATE_SEAM_SELECTION_IMAGES = 0
#Gaussian blur options
GAUSSIAN_BLUR_BEFORE_ENERGY = 0
GAUSSIAN_BLUR_DEVIATION = 4
#Energy function selection, choose one
CARVE_WITH_SIMPLE_ENERGY = 1
CARVE_WITH_MODULE_ENERGY = 0
#New image dimensions, leave ratio at 1 for no rescale
REDUCTION_RATIO_X = 0.8
REDUCTION_RATIO_Y = 1

imageName = "tren1008x756"
decoder = PNGDecoder("Assets\\" + imageName + ".png")
print("Decoding image")
imageRGB = decoder.getRGBImage()
seams_to_remove_x = int(len(imageRGB[0]) - len(imageRGB[0]) * REDUCTION_RATIO_X)
seams_to_remove_y = int(len(imageRGB) - len(imageRGB) * REDUCTION_RATIO_Y)
energy = None
encodedImage = None
blurredImg = None
simpleImage = None
moduleImage = None

#Creating the needed directories
try:
    os.mkdir("Results\\" + imageName)
    os.mkdir("Results\\" + imageName + "\\SeamSelection")
except FileExistsError:
    pass


if GENERATE_SIMPLE_ENERGY_IMAGE:
    print("Generating simple energy image")
    simpleImage = ImageUtility.getSimpleEnergyImage(imageRGB, decoder.bitDepth)
    if decoder.bitDepth == 8:
        encodedImage = png.from_array(simpleImage, "L;8")
    elif decoder.bitDepth == 16:
        encodedImage = png.from_array(simpleImage, "L;16")
    encodedImage.save("Results\\" + imageName + "\\simple_energy.png")

if GENERATE_MODULE_ENERGY_IMAGE:
    print("Generating module energy image")
    moduleImage = ImageUtility.getModuleEnergyImage(imageRGB, decoder.bitDepth)
    if decoder.bitDepth == 8:
        encodedImage = png.from_array(moduleImage, "L;8")
    elif decoder.bitDepth == 16:
        encodedImage = png.from_array(moduleImage, "L;16")
    encodedImage.save("Results\\" + imageName + "\\module_energy.png")

if GENERATE_BLURRED:
    print("Generating blurred image")
    blurredImg = ImageUtility.getBlurredImage(imageRGB, GAUSSIAN_BLUR_DEVIATION, decoder.bitDepth)
    if decoder.bitDepth == 8:
        encodedImage = png.from_array(blurredImg, "RGB;8")
    elif decoder.bitDepth == 16:
        encodedImage = png.from_array(blurredImg, "RGB;16")
    encodedImage.save("Results\\" + imageName + "\\blurred.png")

if GENERATE_SIMPLE_ENERGY_FROM_BLURRED:
    if blurredImg is None:
        print("Generating blurred image")
        blurredImg = ImageUtility.getBlurredImage(imageRGB, GAUSSIAN_BLUR_DEVIATION, decoder.bitDepth)
    print("Generating simple energy image from blurred image")
    simpleImage = ImageUtility.getSimpleEnergyImage(blurredImg, decoder.bitDepth)
    if decoder.bitDepth == 8:
        encodedImage = png.from_array(simpleImage, "L;8")
    elif decoder.bitDepth == 16:
        encodedImage = png.from_array(simpleImage, "L;16")
    encodedImage.save("Results\\" + imageName + "\\simple_energy_from_blurred.png")

if GENERATE_MODULE_ENERGY_FROM_BLURRED:
    if blurredImg is None:
        print("Generating blurred image")
        blurredImg = ImageUtility.getBlurredImage(imageRGB, GAUSSIAN_BLUR_DEVIATION, decoder.bitDepth)
    print("Generating module energy image from blurred image")
    moduleImage = ImageUtility.getModuleEnergyImage(blurredImg, decoder.bitDepth)
    if decoder.bitDepth == 8:
        encodedImage = png.from_array(moduleImage, "L;8")
    elif decoder.bitDepth == 16:
        encodedImage = png.from_array(moduleImage, "L;16")
    encodedImage.save("Results\\" + imageName + "\\module_energy_from_blurred.png")

if CARVE_WITH_SIMPLE_ENERGY:
    if GAUSSIAN_BLUR_BEFORE_ENERGY:
        print("Computing Gaussian blur")
        blur_r, blur_g, blur_b = ImageUtility.gaussianBlurRGB(imageRGB, GAUSSIAN_BLUR_DEVIATION)
        blurred = ImageUtility.combineRGBChannels(blur_r, blur_g, blur_b)
        print("Computing simple energy")
        energy = ImageUtility.getSimpleEnergyRGB(blurred)
    else:
        print("Computing simple energy")
        energy = ImageUtility.getSimpleEnergyRGB(imageRGB)

elif CARVE_WITH_MODULE_ENERGY:
    if GAUSSIAN_BLUR_BEFORE_ENERGY:
        print("Computing Gaussian blur")
        blur_r, blur_g, blur_b = ImageUtility.gaussianBlurRGB(imageRGB, GAUSSIAN_BLUR_DEVIATION)
        blurred = ImageUtility.combineRGBChannels(blur_r, blur_g, blur_b)
        print("Computing simple energy")
        energy = ImageUtility.getEnergyRGBAsModule(blurred)
    else:
        print("Computing simple energy")
        energy = ImageUtility.getEnergyRGBAsModule(imageRGB)

else:
    print("Please select an energy function")

#remove vertical seams until the new ratio is achieved
#The trange method from tqdm shows the progress bar
print("Rescaling x")
for i in tqdm.trange(seams_to_remove_x):

    if GENERATE_SEAM_SELECTION_IMAGES:
        #Draw seams in the image
        seamsImage = ImageUtility.drawSeams(energy, imageRGB)
        encodedImage = png.from_array(seamsImage, "RGB;8")
        filename = "Results\\" + imageName + "\\SeamSelection\\" + str(i) + ".png"
        encodedImage.save(filename)

    energy, imageRGB = ImageUtility.removeMinimalSeam(energy, imageRGB)

#To remove horizontal seams, we transpose the matrices before passing them to the algorithm
energy = [list(t) for t in zip(*energy)]
imageRGB = [list(t) for t in zip(*imageRGB)]

#remove horizontal seams until the new ratio is achieved
#The trange method from tqdm shows the progress bar
print("Rescaling y")
for i in tqdm.trange(seams_to_remove_y):

    if GENERATE_SEAM_SELECTION_IMAGES:
        #Draw seams in the image
        seamsImage = ImageUtility.drawSeams(energy, imageRGB)
        encodedImage = png.from_array(seamsImage, "RGB;8")
        filename = "Results\\" + imageName + "\\SeamSelection\\" + str(i) + ".png"
        encodedImage.save(filename)

    energy, imageRGB = ImageUtility.removeMinimalSeam(energy, imageRGB)

#Reverting the transposition
energy = [list(t) for t in zip(*energy)]
imageRGB = [list(t) for t in zip(*imageRGB)]

#Save the final result
encodedImage = png.from_array(imageRGB, "RGB;8")
if CARVE_WITH_SIMPLE_ENERGY:
    if GAUSSIAN_BLUR_BEFORE_ENERGY:
        encodedImage.save("Results\\" + imageName + "\\seam_carved_simple_with_blur.png")
    else:
        encodedImage.save("Results\\" + imageName + "\\seam_carved_simple.png")
else:
    if GAUSSIAN_BLUR_BEFORE_ENERGY:
        encodedImage.save("Results\\" + imageName + "\\seam_carved_module_with_blur.png")
    else:
        encodedImage.save("Results\\" + imageName + "\\seam_carved_module.png")


























