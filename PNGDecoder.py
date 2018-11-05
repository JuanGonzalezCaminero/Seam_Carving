import zlib

class PNGDecoder:
    def __init__(self, filename):
        self.image = open(filename, "rb")
        self.imageWidth = 0
        self.imageHeight = 0
        self.bitDepth = 0
        self.colorType = 0
        self.compressionMethod = 0
        self.filterMethod = 0
        self.interlaceMethod = 0
        self.palette = []
        self.compressedImage = bytearray()
        self.loadImage()
        self.numberOfChannels = self.getNumberOfChannels()
        self.pixelSize = self.getPixelSize()
        self.scanlineLength = self.pixelSize * self.imageWidth + 1

    #Returns the number of color channels per pixel based in the color type
    def getNumberOfChannels(self):
        if self.colorType == 0:
            return 1
        elif self.colorType == 2:
            return 3
        elif self.colorType == 3:
            return 1
        elif self.colorType == 4:
            return 2
        elif self.colorType == 6:
            return 4

    #Returns the size of a pixel in bytes
    def getPixelSize(self):
        return (self.bitDepth * self.numberOfChannels) // 8

    def getBitDepth(self):
        return self.bitDepth

    #Reads the file at self.filename, and initializes the decoder's parameter using its contents,
    #also reads the data itself and loads it into a bytearray. This may cause problems with larger
    #files, an iterable that reads data chunks of arbitrary length from the file may be a better option
    def loadImage(self):
        chunkType = ""
        self.image.seek(8)  # Skips the first 8 bytes
        # Reading the image and extracting the main parameters
        while chunkType != "IEND":
            # Reads the next chunk content length
            self.chunkLength = int.from_bytes(self.image.read(4), byteorder='big', signed=False)
            # Reads the chunk type
            chunkType = self.image.read(4).decode("utf-8")
            # Switch using the chunk type
            if chunkType == "IHDR":
                self.imageWidth = int.from_bytes(self.image.read(4), byteorder='big', signed=False)
                self.imageHeight = int.from_bytes(self.image.read(4), byteorder='big', signed=False)
                self.bitDepth = int.from_bytes(self.image.read(1), byteorder='big', signed=False)
                self.colorType = int.from_bytes(self.image.read(1), byteorder='big', signed=False)
                self.compressionMethod = int.from_bytes(self.image.read(1), byteorder='big', signed=False)
                self.filterMethod = int.from_bytes(self.image.read(1), byteorder='big', signed=False)
                self.interlaceMethod = int.from_bytes(self.image.read(1), byteorder='big', signed=False)
                # Skips the CRC
                self.image.read(4)
            elif chunkType == "PLTE":
                # Will appear for colour type 3 (indexed colour), may appear for types 2 and 6
                # Types 2 and 6 don't need the palette, but can resource to it if, for some reason,
                # the image cannot be displayed directly
                # The palette contains groups of 3 bytes, representing the values of Red, Green and Blue
                # for each colour.
                for i in range(0, self.chunkLength, 3):
                    # adds a (R,G,B) tuple to the palette
                    self.palette.append((int.from_bytes(self.image.read(1), byteorder='big', signed=False),
                                    int.from_bytes(self.image.read(1), byteorder='big', signed=False),
                                    int.from_bytes(self.image.read(1), byteorder='big', signed=False)))
                # Skips the CRC
                self.image.read(4)

            elif chunkType == "IDAT":
                self.compressedImage += bytearray(self.image.read(self.chunkLength))
                # Skips the CRC
                self.image.read(4)

            # Non-essential chunks, for now I will just ignore them
            else:
                self.image.read(self.chunkLength)
                self.image.read(4)

    #Prints the image parameters to the standard output
    def printParameters(self):
        print("Image width: %d\n"
              "Image height: %d\n"
              "Bit depth: %d\n"
              "Color type: %d\n"
              "Compression method: %d\n"
              "Filter method: %d\n"
              "Interlace method: %d\n" %
              (self.imageWidth, self.imageHeight, self.bitDepth, self.colorType,
               self.compressionMethod, self.filterMethod, self.interlaceMethod))

    #Decompresses the image data using zlib
    def getDecompressedData(self):
        # The image data is stored in a bytearray. This data is compressed using a deflate compression
        #algorith, this library decodes it
        decompressedData = zlib.decompress(self.compressedImage, wbits=zlib.MAX_WBITS, bufsize=zlib.DEF_BUF_SIZE)
        return decompressedData

    #Paeth predictor function, refer to the png specification
    def paethPredictor(self, a, b, c):
        p = a + b - c
        pa = abs(p - a)
        pb = abs(p - b)
        pc = abs(p - c)
        if pa <= pb and pa <= pc:
            pr = a
        elif pb <= pc:
            pr = b
        else:
            pr = c
        return pr

    #Unfilters the data using an iterator that receives a stream of filtered data and returns an unfiltered
    #scanline with each call, may be cleaner than the regular solution, but it doesn't seem to be any faster
    def getUnfilteredDataWithIterator(self, decompressedData):
        #Returns a matrix containing a bytearray for each scanline of the image
        decompressedData = bytearray(decompressedData)
        unfilteredImage = []
        scanlineLength = self.imageWidth * self.pixelSize + 1
        # Filters are applied scanline to scanline, filter method 0 indicates the standard filtering
        # is used, with 5 possible options, the filter used in each scanline is defined by a byte before it
        # The length of the scanlines stored within the data depends on the interlacing method
        if self.interlaceMethod == 0:
            # No interlacing was applied, each scanline is as long as the image width, and there are
            # imageHeight scanlines
            # The bit depth determines how many pixels represent each channel, the color type determines
            # the number of channels for a pixel, this variables affect the indexes within the array of
            # bytes that contains the data
            unfilteredImage = [scanline for scanline in self.unfilterIterator(decompressedData)]

        else:
            print("Interlaced images decoding not yet implemented")

        return unfilteredImage

    #iterator that receives a stream of filtered data and returns an unfiltered
    #scanline with each call
    def unfilterIterator(self, filteredData):
        #Iterator that yields unfiltered scanlines, filtered data is a bytearray containing
        #all the decompressed data from the image
        previousScanline = None #There is no problem in passing this to unfilter scanline
        #the first time, as the first scanline will not have a filter type that uses the
        #previous for decoding
        while(len(filteredData) >= self.scanlineLenght):
            previousScanline = self.unfilterScanline(filteredData[0],
                                                     filteredData[1: self.scanlineLenght],
                                                     previousScanline)
            #Remove the already decoded scanline
            filteredData = filteredData[self.scanlineLenght:]
            #Each call to the iterator will return an unfiltered scanline, until the entry data list
            #is empty and this yield is not reached
            print(len(filteredData))
            yield previousScanline

    #Receives a stream of filtered data and returns it unfiltered
    def getUnfilteredData(self, decompressedData):
        decompressedData = bytearray(decompressedData)
        unfilteredImage = bytearray()
        scanlineLength = self.imageWidth * self.pixelSize + 1
        # Filters are applied scanline to scanline, filter method 0 indicates the standard filtering
        # is used, with 5 possible options, the filter used in each scanline is defined by a byte before it
        # The length of the scanlines stored within the data depends on the interlacing method
        if self.interlaceMethod == 0:
            # No interlacing was applied, each scanline is as long as the image width, and there are
            # imageHeight scanlines
            # The bit depth determines how many pixels represent each channel, the color type determines
            # the number of channels for a pixel, this variables affect the indexes within the array of
            # bytes that contains the data

            #First iteration, unfiltered image is still empty so we can't pass the previous scanline
            #to unfilter scanline
            scanlineFilter = decompressedData[0]
            unfilteredImage += self.unfilterScanline(scanlineFilter, decompressedData[1: scanlineLength], [])
            #print("Filtered: ", decompressedData[1: scanlineLength])
            #print("Unfiltered: ", unfilteredImage)

            for i in range(1, self.imageHeight):
                #línea que queremos leer * tamaño de la scanline
                scanlineBase = i * scanlineLength
                scanlineFilter = decompressedData[scanlineBase]
                unfilteredImage += self.unfilterScanline(scanlineFilter,
                                                         decompressedData[scanlineBase + 1:
                                                                          scanlineLength + scanlineBase],
                                                         unfilteredImage[-scanlineLength + 1:])

        else:
            print("Interlaced images decoding not yet implemented")

        return unfilteredImage

    #Receives a filter type, from 0 to 4, a filtered scanline and the previous scanline to that one,
    #unfiltered, returns the scanline unfiltered
    def unfilterScanline(self, filter_type, scanline, previous_scanline):
        # Naming:
        # x: the byte being filtered
        # a: the byte corresponding to x in the pixel immediately before the pixel containing x
        # (or the byte immediately before x, when the bit depth is less than 8)
        # b: the byte corresponding to x in the previous scanline;
        # c: the byte corresponding to b in the pixel immediately before the pixel containing b
        # (or the byte immediately before b, when the bit depth is less than 8).

        # All the operations are performed using unsigned modulo 256 arithmetic
        result = scanline
        if filter_type == 0:
            return result
        elif filter_type == 1:
            # Name: Sub
            # Filt(x) = Orig(x) - Orig(a)
            # Recon(x) = Filt(x) + Recon(a)
            prev_byte_index = 0
            #Starting at the second pixel, as the first one already has the right values
            for i in range(self.pixelSize, len(scanline)):
                #Using 0xff as a mask to get the modulo 256 of the operation
                result[i] = (scanline[i] + scanline[prev_byte_index]) & 0xff
                prev_byte_index += 1
            return result

        elif filter_type == 2:
            # Name: Up
            # Filt(x) = Orig(x) - Orig(b)
            # Recon(x) = Filt(x) + Recon(b)
            result = [(filteredByte + reconstructedByte) & 0xff for
                                           filteredByte, reconstructedByte in
                                           zip(scanline, previous_scanline)]
            return bytearray(result)
            #Uncool solution that doesnt use python's cool haskal-like thingies
            #for i in range(len(scanline)):
            #    result[i] = (scanline[i] + previous_scanline[i]) & 0xff

        elif filter_type == 3:
            # Name: Average
            # Filt(x) = Orig(x) - floor((Orig(a) + Orig(b)) / 2)
            # Recon(x) = Filt(x) + floor((Recon(a) + Recon(b)) / 2)

            # For the first pixel we only have values for b, as a will be 0 in all cases, so the
            # result is Filt(x) + Recon(b)/2
            for i in range(len(scanline)):
                if i < self.pixelSize:
                    a = 0
                else:
                    a = scanline[i - self.pixelSize]
                b = previous_scanline[i]
                result[i] = (scanline[i] + ((a + b)>>1)) & 0xff
            return result

        elif filter_type == 4:
            # Name: Paeth
            # Filt(x) = Orig(x) - PaethPredictor(Orig(a), Orig(b), Orig(c))
            # Recon(x) = Filt(x) + PaethPredictor(Recon(a), Recon(b), Recon(c))
            for i in range(len(scanline)):
                if i < self.pixelSize:
                    a = 0
                    c = 0
                else:
                    a = scanline[i - self.pixelSize]
                    c = previous_scanline[i - self.pixelSize]
                b = previous_scanline[i]
                #Paeth Predictor:
                p = a + b - c
                pa = abs(p - a)
                pb = abs(p - b)
                pc = abs(p - c)
                if pa <= pb and pa <= pc:
                    pr = a
                elif pb <= pc:
                    pr = b
                else:
                    pr = c
                result[i] = (scanline[i] + pr) & 0xff
            return result

    #De-serializes scanlines from a stream of unfiltered data, returns a multi-dimensional array with the
    #pixel values in tuples containing bytearrays
    def getDeinterlacedData(self, unfilteredData):
        # We now have the image data with the scanlines unfiltered. The scanlines are serialized within
        # this data. The last step is decoding the interlacing, if any was applied
        deinterlacedImage = []

        if self.interlaceMethod == 0:
            # No interlacing was applied
            if self.colorType == 0:
                print("Color type 0 decoding not yet implemented")
                return
            elif self.colorType == 2:
                scanlineLength8 = self.imageWidth * 3
                scanlineLength16 = self.imageWidth * 2 * 3
                for i in range(self.imageHeight):
                    # Appending a new empty list to the list of lists
                    deinterlacedImage.append([])
                    for j in range(self.imageWidth):
                        # Treat the unfiltered data vector as a pointer to the start of a matrix
                        # The data is appended to the list i of the list of lists "deinterlacedImage", thanks python!
                        # Depending on the bit depth, each channel will be made up of 8 or 16 bits, (in truecolour)
                        if self.bitDepth == 8:
                            deinterlacedImage[i].append((unfilteredData[i * scanlineLength8 + 3 * j:
                                                                        i * scanlineLength8 + 3 * j + 3]))
                            #Its unnecessary to put the values in a tuple in the commented way, since, with this bit
                            #depth, each tuple element corresponds to one bytearray element anyway, so, by storing that
                            #section of the bytearray in a tuple we are creating a 3-element tuple
                            #deinterlacedImage[i].append((unfilteredData[i * scanlineLength8 + 3 * j],
                            #                        unfilteredData[i * scanlineLength8 + 3 * j + 1],
                            #                        unfilteredData[i * scanlineLength8 + 3 * j + 2]))
                        else:
                            # scanline * ancho de la imagen * 2 bytes por canal * número de canales +
                            #  numero de canales * posicion del pixel * 2 bytes por canal
                            deinterlacedImage[i].append((unfilteredData[i * scanlineLength16 + 3 * j * 2:
                                                                    i * scanlineLength16 + 3 * j * 2 + 2],
                                                    unfilteredData[i * scanlineLength16 + 3 * j * 2 + 2:
                                                                    i * scanlineLength16 + 3 * j * 2 + 4],
                                                    unfilteredData[i * scanlineLength16 + 3 * j * 2 + 4:
                                                                    i * scanlineLength16 + 3 * j * 2 + 6]))
                return deinterlacedImage
            elif self.colorType == 3:
                print("Color type 3 decoding not yet implemented")
                return
            elif self.colorType == 4:
                print("Color type 4 decoding not yet implemented")
                return
            elif self.colorType == 6:
                #This clearly has some issue, here or while formatting to RGB
                scanlineLength8 = self.imageWidth * self.pixelSize
                scanlineLength16 = self.imageWidth * 2 * self.pixelSize
                for i in range(self.imageHeight):
                    # Appending a new empty list to the list of lists
                    deinterlacedImage.append([])
                    for j in range(self.imageWidth):
                        # Treat the unfiltered data vector as a pointer to the start of a matrix
                        # The data is appended to the list i of the list of lists "deinterlacedImage", thanks python!
                        # Depending on the bit depth, each channel will be made up of 8 or 16 bits, (in truecolour)
                        if self.bitDepth == 8:
                            deinterlacedImage[i].append((unfilteredData[i * scanlineLength8 + self.pixelSize * j:
                                                                        i * scanlineLength8 + self.pixelSize * j + self.pixelSize + 1]))
                            # Its unnecessary to put the values in a tuple in the commented way, since, with this bit
                            # depth, each tuple element corresponds to one bytearray element anyway, so, by storing that
                            # section of the bytearray in a tuple we are creating a 3-element tuple
                            # deinterlacedImage[i].append((unfilteredData[i * scanlineLength8 + 3 * j],
                            #                        unfilteredData[i * scanlineLength8 + 3 * j + 1],
                            #                        unfilteredData[i * scanlineLength8 + 3 * j + 2]))
                        else:
                            print("Color type 6 decoding with 16 bit color depth not yet implemented")
                            # scanline * ancho de la imagen * 2 bytes por canal * número de canales +
                            #  numero de canales * posicion del pixel * 2 bytes por canal
                            #deinterlacedImage[i].append((unfilteredData[i * scanlineLength16 + 3 * j * 2:
                            #                                            i * scanlineLength16 + 3 * j * 2 + 2],
                            #                             unfilteredData[i * scanlineLength16 + 3 * j * 2 + 2:
                            #                                            i * scanlineLength16 + 3 * j * 2 + 4],
                            #                             unfilteredData[i * scanlineLength16 + 3 * j * 2 + 4:
                            #                                            i * scanlineLength16 + 3 * j * 2 + 6]))


                return deinterlacedImage
        else:
            print("Interlace decoding not yet implemented")
            exit()

    #Returns a matrix containing a tuple for each pixel, which
    #stores the values of the R G and B channels as ints, if the image contains any transparency,
    #that information is not recorded
    def getRGBImage(self):
        #print("Decompressing")
        decompressedImage = self.getDecompressedData()
        #print("Unfiltering")
        unfilteredImage = self. getUnfilteredData(decompressedImage)
        #unfilteredImage = self.getUnfilteredDataWithIterator(decompressedImage)
        #print("Deinterlacing")
        deinterlacedImage = self.getDeinterlacedData(unfilteredImage)
        #print("Formatting")
        rgbImage = []

        if self.colorType == 0:
            print("Color type 0 decoding not yet implemented")
            return
        elif self.colorType == 2:
            if self.bitDepth == 16:
                for i in range(len(deinterlacedImage)):
                    rgbImage.append([])
                    for j in range(len(deinterlacedImage[0])):
                        rgbImage[i].append((int.from_bytes(deinterlacedImage[i][j][0], byteorder='big', signed=False),
                                            int.from_bytes(deinterlacedImage[i][j][1], byteorder='big', signed=False),
                                            int.from_bytes(deinterlacedImage[i][j][2], byteorder='big', signed=False)))
            else:
                for i in range(len(deinterlacedImage)):
                    rgbImage.append([])
                    for j in range(len(deinterlacedImage[0])):
                        rgbImage[i].append((deinterlacedImage[i][j][0],
                                            deinterlacedImage[i][j][1],
                                            deinterlacedImage[i][j][2]))
            return rgbImage

        elif self.colorType == 3:
            print("Color type 3 decoding not yet implemented")
            return
        elif self.colorType == 4:
            print("Color type 4 decoding not yet implemented")
            return
        elif self.colorType == 6:
            if self.bitDepth == 8:
                for i in range(len(deinterlacedImage)):
                    rgbImage.append([])
                    for j in range(len(deinterlacedImage[0])):
                        rgbImage[i].append((deinterlacedImage[i][j][0],
                                            deinterlacedImage[i][j][1],
                                            deinterlacedImage[i][j][2]))
            else:
                print("Color type 6 decoding with 16 bit color depth not yet implemented")
            return rgbImage

























