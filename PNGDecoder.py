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

    def getBitDepth(self):
        return self.bitDepth

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

    def getDecompressedData(self):
        # The image data is stored in a bytearray. This data is compressed using a deflate compression
        #algorith, this library decodes it
        decompressedData = zlib.decompress(self.compressedImage, wbits=zlib.MAX_WBITS, bufsize=zlib.DEF_BUF_SIZE)
        return decompressedData

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

    def getUnfilteredData(self, decompressedData):
        unfilteredImage = bytearray()
        # Filters are applied scanline to scanline, filter method 0 indicates the standard filtering
        # is used, with 5 possible options, the filter used in each scanline is defined by a byte before it
        # The length of the scanlines stored within the data depends on the interlacing method
        if self.interlaceMethod == 0:
            # No interlacing was applied, each scanline is as long as the image width, and there are
            # imageHeight scanlines
            # The bit depth determines how many pixels represent each channel, the color type determines
            # the number of channels for a pixel, this variables affect the indexes within the array of
            # bytes that contains the data

            # Naming:

            # x: the byte being filtered
            # a: the byte corresponding to x in the pixel immediately before the pixel containing x
            # (or the byte immediately before x, when the bit depth is less than 8)
            # b: the byte corresponding to x in the previous scanline;
            # c: the byte corresponding to b in the pixel immediately before the pixel containing b
            # (or the byte immediately before b, when the bit depth is less than 8).

            # All the operations are performed using unsigned modulo 256 arithmetic
            if self.colorType == 0:
                print("Color type 0 decoding not yet implemented")
                return

            elif self.colorType == 2:
                # for color type 2 there are 2 possibilities for the bit depth, 8 and 16
                if self.bitDepth == 8:
                    # Número de píxels por scanline * número de bytes por píxel + 1 byte de filtro
                    scanlineLength = self.imageWidth * 3 + 1
                    for i in range(self.imageHeight):
                        # línea que queremos leer * tamaño de la scanline
                        scanlineBase = i * scanlineLength

                        #print(scanlineBase)
                        scanlineFilter = decompressedData[scanlineBase]
                        if scanlineFilter == 0:
                            #print("Filter type 0")
                            #print("This scanline:")
                            #print([a for a in decompressedData[scanlineBase + 1: scanlineLength + scanlineBase]])

                            # No filter was applied
                            unfilteredImage += (decompressedData[scanlineBase + 1: scanlineLength + scanlineBase])

                            #print("Decoded scanline:")
                            #print([a for a in unfilteredImage[-scanlineLength + 1:]])
                        elif scanlineFilter == 1:
                            #print("Filter type 1")
                            # Name: Sub
                            # Filt(x) = Orig(x) - Orig(a)
                            # Recon(x) = Filt(x) + Recon(a)

                            #print("Filter type 1")
                            #print("This scanline:")
                            #print([a for a in decompressedData[scanlineBase + 1: scanlineLength + scanlineBase]])

                            unfilteredImage += (decompressedData[scanlineBase + 1: scanlineBase + 3 + 1])
                            for j in range(scanlineBase + 4, scanlineLength + scanlineBase + 1 - 3, 3):
                                #print([(a + b) % 256 for a, b in zip(decompressedData[j: j + 3], unfilteredImage[-3:])])
                                unfilteredImage += (bytearray([(filteredByte + reconstructedByte) % 256 for
                                                               filteredByte, reconstructedByte in
                                                               zip(decompressedData[j: j + 3], unfilteredImage[-3:])]))

                            #print("Decoded scanline:")
                            #print([a for a in unfilteredImage[-scanlineLength + 1:]])

                        elif scanlineFilter == 2:
                            #print("Filter type 2")
                            # Name: Up
                            # Filt(x) = Orig(x) - Orig(b)
                            # Recon(x) = Filt(x) + Recon(b)

                            #print("Filter type 2")
                            #print("Previous scanline:")
                            #print([a for a in unfilteredImage[-scanlineLength + 1:]])
                            #print("This scanline:")
                            #print([a for a in decompressedData[scanlineBase + 1: scanlineLength + scanlineBase]])

                            # All the bytes in the previous scanline have already been decoded, we can do this with
                            # a simple yet elegant list comprehension
                            unfilteredImage += (bytearray([(filteredByte + reconstructedByte) % 256 for
                                                           filteredByte, reconstructedByte in
                                                           zip(decompressedData[scanlineBase + 1:
                                                                                scanlineLength + scanlineBase + 1],
                                                               unfilteredImage[-scanlineLength + 1:])]))

                            #print("Decoded scanline:")
                            #print([a for a in unfilteredImage[-scanlineLength + 1:]])

                        elif scanlineFilter == 3:
                            # Name: Average
                            # Filt(x) = Orig(x) - floor((Orig(a) + Orig(b)) / 2)
                            # Recon(x) = Filt(x) + floor((Recon(a) + Recon(b)) / 2)
                            #The sum shall be performed whithout overflow (no problem in python)
                            #print("Filter type 3")
                            #print("Previous scanline:")
                            #print([a for a in unfilteredImage[-scanlineLength + 1:]])
                            #print("This scanline:")
                            #print([a for a in decompressedData[scanlineBase + 1: scanlineLength + scanlineBase]])


                            #Temporarily storing a copy of the previos scanline here
                            tempPreviousScanline = unfilteredImage[-scanlineLength + 1:]
                            #For the first pixel we only have values for b, as a will be 0 in all cases, so the
                            #result is Filt(x) + Recon(b)/2
                            for j in range(scanlineBase + 1, scanlineLength + scanlineBase + 1 - 3, 3):
                                #print(decompressedData[j: j + 3])
                                #print(unfilteredImage[-3:])
                                #print(tempPreviousScanline[j - scanlineBase: j - scanlineBase + 3])
                                #if(j == scanlineBase + 4):
                                #    print(list(zip(decompressedData[j: j + 3],
                                #                unfilteredImage[-3:],
                                #                tempPreviousScanline[j - scanlineBase - 1: j - scanlineBase - 1 + 3])))
                                if(j == scanlineBase + 1):
                                    unfilteredImage += (bytearray([(filteredByte + b//2) % 256 for
                                                               filteredByte, b in
                                                               zip(decompressedData[j: j + 3],
                                                                   tempPreviousScanline[: 3])]))
                                    continue

                                unfilteredImage += (bytearray([(filteredByte + (a + b)//2) % 256 for
                                                               filteredByte, a, b in
                                                               zip(decompressedData[j: j + 3],
                                                                   unfilteredImage[-3:],
                                                                   tempPreviousScanline[j - scanlineBase - 1:
                                                                                        j - scanlineBase - 1 + 3])]))
                                #print([a for a in unfilteredImage[-3:]])

                            #print("Decoded scanline:")
                            #print([a for a in unfilteredImage[-scanlineLength + 1:]])

                        elif scanlineFilter == 4:
                            # Name: Paeth
                            # Filt(x) = Orig(x) - PaethPredictor(Orig(a), Orig(b), Orig(c))
                            # Recon(x) = Filt(x) + PaethPredictor(Recon(a), Recon(b), Recon(c))

                            #print("Filter type 4")
                            #print("Previous scanline:")
                            #print([a for a in unfilteredImage[-scanlineLength + 1:]])
                            #print("This scanline:")
                            #print([a for a in decompressedData[scanlineBase + 1: scanlineLength + scanlineBase]])

                            # Temporarily storing a copy of the previos scanline here
                            tempPreviousScanline = unfilteredImage[-scanlineLength + 1:]
                            #For the first pixel, we will only have values for b, as a and c would be outside of the image,
                            #in this situation, the paeth predictor will choose b as the predictor, so I will not bother
                            #calling the function as the result is already known
                            for j in range(scanlineBase + 1 , scanlineLength + scanlineBase + 1 - 3, 3):
                                if(j == scanlineBase + 1):
                                    unfilteredImage += (bytearray([(filteredByte + b) % 256 for
                                                                   filteredByte, b in
                                                                   zip(decompressedData[j: j + 3],
                                                                       tempPreviousScanline[: 3])]))
                                    continue
                                unfilteredImage += (bytearray([(filteredByte + self.paethPredictor(a, b, c)) % 256 for
                                                               filteredByte, a, b, c in
                                                               zip(decompressedData[j: j + 3],
                                                                   unfilteredImage[-3:],
                                                                   tempPreviousScanline[j - scanlineBase - 1:
                                                                                        j - scanlineBase - 1 + 3],
                                                                   tempPreviousScanline[j - scanlineBase - 1 - 3:
                                                                                        j - scanlineBase - 1])]))

                            #print("Decoded scanline:")
                            #print([a for a in unfilteredImage[-scanlineLength + 1:]])

                else:
                    # Número de píxels por scanline * número de bytes por canal * número de canales por píxel + 1 byte de filtro
                    scanlineLength = self.imageWidth * 3 * 2 + 1
                    for i in range(self.imageHeight):
                        # línea que queremos leer * tamaño de la scanline
                        scanlineBase = i * scanlineLength

                        scanlineFilter = decompressedData[scanlineBase]
                        # print(i * imageWidth * 3 * 2 + i)
                        # print(scanlineFilter)
                        if scanlineFilter == 0:
                            #print("Filter type 0:")
                            # No filter was applied
                            unfilteredImage += (decompressedData[scanlineBase + 1: scanlineLength + scanlineBase])
                        elif scanlineFilter == 1:
                            #print("Filter type 1:")
                            # Name: Sub
                            # Filt(x) = Orig(x) - Orig(a)
                            # Recon(x) = Filt(x) + Recon(a)
                            # What we have here are the Filt(x) values for each byte
                            # The first pixel is already in its original codification
                            unfilteredImage += (decompressedData[scanlineBase + 1: scanlineBase + 2 * 3 + 1])
                            for j in range(scanlineBase + 7, scanlineLength + scanlineBase + 1 - 6, 2 * 3):
                                # 6 is the number of bytes per pixel, the filters are applied byte by byte, but
                                # the values referred in the formulas are relative to the pixels
                                # starting at 7 because the values in the first pixel are the original ones, as it
                                # has no pixels to its left
                                # the for loop ends at scanlineLength + scanlineBase - 6, because the next 6 bytes
                                # will be picked in that last iteration, after that starts the following scanline,
                                # +1 because range doesn't include the last number
                                #print([a + b for a, b in zip(decompressedData[j: j + 6], unfilteredImage[-6:])])
                                unfilteredImage += (bytearray([(filteredByte + reconstructedByte) % 256 for
                                                               filteredByte, reconstructedByte in
                                                               zip(decompressedData[j: j + 6], unfilteredImage[-6:])]))
                                #print("Filtered line: ")
                                #print(decompressedData[scanlineBase + 1: scanlineBase + scanlineLength])
                                #print("Unfiltered line: ")
                                #print(unfilteredImage[-scanlineLength + 1:])
                        elif scanlineFilter == 2:
                            #print("Filter type 2:")
                            # Name: Up
                            # Filt(x) = Orig(x) - Orig(b)
                            # Recon(x) = Filt(x) + Recon(b)
                            # All the bytes in the previous scanline have already been decoded, we can do this with
                            # a simple yet elegant list comprehension
                            unfilteredImage += (bytearray([(filteredByte + reconstructedByte) % 256 for
                                                           filteredByte, reconstructedByte in
                                                           zip(decompressedData[scanlineBase + 1:
                                                                                scanlineLength + scanlineBase + 1],
                                                               unfilteredImage[-scanlineLength + 1:])]))
                        elif scanlineFilter == 3:
                            # Name: Average
                            # Filt(x) = Orig(x) - floor((Orig(a) + Orig(b)) / 2)
                            # Recon(x) = Filt(x) + floor((Recon(a) + Recon(b)) / 2)
                            # The sum shall be performed whithout overflow (no problem in python)
                            print("Previous scanline:")
                            print([a for a in unfilteredImage[-scanlineLength + 1:]])
                            print("This scanline:")
                            print([a for a in decompressedData[scanlineBase + 1: scanlineLength + scanlineBase]])

                            # Temporarily storing a copy of the previos scanline minus its first pixel here
                            tempPreviousScanline = [a for a in unfilteredImage[-scanlineLength + 1 + 2 * 3:]]
                            # I assume the first byte in the scanline is already in its original form
                            unfilteredImage += (decompressedData[scanlineBase + 1: scanlineBase + 2 * 3 + 1])
                            for j in range(scanlineBase + 7, scanlineLength + scanlineBase + 1 - 6, 2 * 3):
                                unfilteredImage += (bytearray([(filteredByte + (a + b) // 2) % 256 for
                                                               filteredByte, a, b in
                                                               zip(decompressedData[j: j + 6],
                                                                   unfilteredImage[-6:],
                                                                   tempPreviousScanline)]))

                            print("Decoded scanline:")
                            print([a for a in unfilteredImage[-scanlineLength + 1:]])
                        elif scanlineFilter == 4:
                            print("Filter type 4 not yet implemented")

                return unfilteredImage

            elif self.colorType == 3:
                print("Color type 3 decoding not yet implemented")
                return

            elif self.colorType == 4:
                print("Color type 4 decoding not yet implemented")
                return

            elif self.colorType == 6:
                print("Color type 6 decoding not yet implemented")
                return

        else:
            print("Interlaced images decoding not yet implemented")

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
                            deinterlacedImage[i].append((unfilteredData[i * scanlineLength8 + 3 * j],
                                                    unfilteredData[i * scanlineLength8 + 3 * j + 1],
                                                    unfilteredData[i * scanlineLength8 + 3 * j + 2]))
                        else:
                            # print("i: ",  i)
                            # print("j: ",  j)
                            # print(i * imageWidth * 2 * 3 + 3 * j * 2)
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
                print("Color type 6 decoding not yet implemented")
                return
        else:
            print("Interlace decoding not yet implemented")
            exit()

    #Returns a matrix containing a tuple for each pixel, which
    #stores the values of the R G and B channels as ints
    def getRGBImage(self):
        decompressedImage = self.getDecompressedData()
        unfilteredImage = self. getUnfilteredData(decompressedImage)
        deinterlacedImage = self.getDeinterlacedData(unfilteredImage)
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
            print("Color type 6 decoding not yet implemented")
            return

























