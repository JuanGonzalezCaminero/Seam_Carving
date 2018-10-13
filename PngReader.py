import zlib

#image = open("C:\\Users\\JuanG\\Desktop\\readTest.png", "rb") #Al abrirla en modo binario,
image = open("Assets\\testbn4.png", "rb") #Al abrirla en modo binario,
# no se efectuan transformaciones no deseadas de los datos al leerlo
print(image.read(8)) #Skips the first 8 bytes
chunkType = ""
imageWidth = 0
imageHeight = 0
bitDepth = 0
colorType = 0
compressionMethod = 0
filterMethod = 0
interlaceMethod = 0
palette = []
imageBytes = bytearray()
decodedImage = []
unfilteredImage = bytearray()

#Reading the image and extracting the main parameters
while chunkType != "IEND":
       #Reads the next chunk content length
       chunkLength = int.from_bytes(image.read(4), byteorder='big', signed=False)
       #Reads the chunk type
       chunkType = image.read(4).decode("utf-8")
       #Switch using the chunk type
       if chunkType == "IHDR":
              imageWidth = int.from_bytes(image.read(4), byteorder='big', signed=False)
              imageHeight = int.from_bytes(image.read(4), byteorder='big', signed=False)
              bitDepth = int.from_bytes(image.read(1), byteorder='big', signed=False)
              colorType = int.from_bytes(image.read(1), byteorder='big', signed=False)
              compressionMethod = int.from_bytes(image.read(1), byteorder='big', signed=False)
              filterMethod = int.from_bytes(image.read(1), byteorder='big', signed=False)
              interlaceMethod = int.from_bytes(image.read(1), byteorder='big', signed=False)
              #Skips the CRC
              image.read(4)
       elif chunkType == "PLTE":
              #Will appear for colour type 3 (indexed colour), may appear for types 2 and 6
              #Types 2 and 6 don't need the palette, but can resource to it if, for some reason,
              #the image cannot be displayed directly
              #The palette contains groups of 3 bytes, representing the values of Red, Green and Blue
              #for each colour.
              for i in range(0, chunkLength, 3):
                     #adds a (R,G,B) tuple to the palette
                     palette.append((int.from_bytes(image.read(1), byteorder='big', signed=False),
                                     int.from_bytes(image.read(1), byteorder='big', signed=False),
                                     int.from_bytes(image.read(1), byteorder='big', signed=False)))
              # Skips the CRC
              image.read(4)

       elif chunkType == "IDAT":
              print(chunkLength)
              imageBytes += bytearray(image.read(chunkLength))
              # Skips the CRC
              image.read(4)

       #Non-essential chunks, for now I will just ignore them
       else:
              image.read(chunkLength)
              image.read(4)



print("Image width: %d\n"
      "Image height: %d\n"
      "Bit depth: %d\n"
      "Color type: %d\n"
      "Compression method: %d\n"
      "Filter method: %d\n"
      "Interlace method: %d\n" %
      (imageWidth, imageHeight, bitDepth, colorType, compressionMethod, filterMethod, interlaceMethod))

#Now the image data is stored in a bytearray. The image data is first filtered and compressed after that,
#we need to decode it before it can be used. The data in png is compressed using the zlib "deflate" algorithm,
#I will use a library to decompress it
decompressedData = zlib.decompress(imageBytes, wbits=zlib.MAX_WBITS, bufsize=zlib.DEF_BUF_SIZE)
#decompressedData is the decompressed version of the filtered image, it is a bytes object
#The scanlines of the image may still be filtered, so that would have to be decoded
print("Decompressed image:")
print(decompressedData)

#Filters are applied scanline to scanline, filter method 0 indicates the standard filtering
#is used, with 5 possible options, the filter used in each scanline is defined by a byte before it
#Te length of the scanlines stored within the data depends on the interlacing method
if interlaceMethod == 0:
    #No interlacing was applied, each scanline is as long as the image width, and there are
    #imageHeight scanlines
    #The bit depth determines how many pixels represent each channel, the color type determines
    #the number of channels for a pixel, this variables affect the indexes within the array of
    #bytes that contains the data

    #Naming:

    #x: the byte being filtered
    #a: the byte corresponding to x in the pixel immediately before the pixel containing x
    #(or the byte immediately before x, when the bit depth is less than 8)
    #b: the byte corresponding to x in the previous scanline;
    #c: the byte corresponding to b in the pixel immediately before the pixel containing b
    #(or the byte immediately before b, when the bit depth is less than 8).

    #All the operations are performed using unsigned modulo 256 arithmetic
    if colorType == 2:
        #for color type 2 there are 2 possibilities for the bit depth, 8 and 16
        if bitDepth == 8:
            #Número de píxels por scanline * número de bytes por píxel + 1 byte de filtro
            scanlineLength = imageWidth * 3 + 1
            for i in range(imageHeight):
                #línea que queremos leer * tamaño de la scanline
                scanlineBase = i * scanlineLength

                print(scanlineBase)
                scanlineFilter = decompressedData[scanlineBase]
                if scanlineFilter == 0:
                    #No filter was applied
                    unfilteredImage += (decompressedData[scanlineBase + 1 : scanlineLength + scanlineBase])
                elif scanlineFilter == 1:
                    print("Filter type 1")
                    # Name: Sub
                    # Filt(x) = Orig(x) - Orig(a)
                    # Recon(x) = Filt(x) + Recon(a)
                    unfilteredImage += (decompressedData[scanlineBase + 1: scanlineBase + 3 + 1])
                    for j in range(scanlineBase + 4, scanlineLength + scanlineBase + 1 - 3, 3):
                        print([(a + b)%256 for a, b in zip(decompressedData[j: j + 3], unfilteredImage[-3:])])
                        unfilteredImage += (bytearray([(filteredByte + reconstructedByte)%256 for
                                                       filteredByte, reconstructedByte in
                                                       zip(decompressedData[j: j + 3], unfilteredImage[-3:])]))
                elif scanlineFilter == 2:
                    print("Filter type 2")
                    # Name: Up
                    # Filt(x) = Orig(x) - Orig(b)
                    # Recon(x) = Filt(x) + Recon(b)
                    # All the bytes in the previous scanline have already been decoded, we can do this with
                    # a simple yet elegant list comprehension
                    unfilteredImage += (bytearray([(filteredByte + reconstructedByte)%256 for
                                                   filteredByte, reconstructedByte in
                                                   zip(decompressedData[scanlineBase + 1:
                                                                        scanlineLength + scanlineBase + 1],
                                                       unfilteredImage[-scanlineLength + 1:])]))
                elif scanlineFilter == 3:
                    print("Filter type 3")
                elif scanlineFilter == 4:
                    print("Filter type 4")
        else:
            #Número de píxels por scanline * número de bytes por canal * número de canales por píxel + 1 byte de filtro
            scanlineLength = imageWidth * 3 * 2 + 1
            for i in range(imageHeight):
                # línea que queremos leer * tamaño de la scanline
                scanlineBase = i * scanlineLength

                scanlineFilter = decompressedData[scanlineBase]
                #print(i * imageWidth * 3 * 2 + i)
                #print(scanlineFilter)
                if scanlineFilter == 0:
                    print("Filter type 0:")
                    #No filter was applied
                    unfilteredImage += (decompressedData[scanlineBase + 1 : scanlineLength + scanlineBase])
                elif scanlineFilter == 1:
                    print("Filter type 1:")
                    #Name: Sub
                    #Filt(x) = Orig(x) - Orig(a)
                    #Recon(x) = Filt(x) + Recon(a)
                    #What we have here are the Filt(x) values for each byte
                    #The first pixel is already in its original codification
                    unfilteredImage += (decompressedData[scanlineBase + 1 : scanlineBase + 2 * 3 + 1])
                    for j in range(scanlineBase + 7, scanlineLength + scanlineBase + 1 - 6, 2 * 3):
                        #6 is the number of bytes per pixel, the filters are applied byte by byte, but
                        #the values referred in the formulas are relative to the pixels
                        #starting at 7 because the values in the first pixel are the original ones, as it
                        #has no pixels to its left
                        #the for loop ends at scanlineLength + scanlineBase - 6, because the next 6 bytes
                        #will be picked in that last iteration, after that starts the following scanline,
                        #+1 because range doesn't include the last number
                        print([a + b for a,b in zip(decompressedData[j : j + 6], unfilteredImage[-6 :])])
                        unfilteredImage += (bytearray([(filteredByte + reconstructedByte)%256 for
                                                       filteredByte, reconstructedByte in
                                                       zip(decompressedData[j : j + 6], unfilteredImage[-6 :])]))
                        print("Filtered line: ")
                        print(decompressedData[scanlineBase + 1 : scanlineBase + scanlineLength])
                        print("Unfiltered line: ")
                        print(unfilteredImage[-scanlineLength + 1:])
                elif scanlineFilter == 2:
                    print("Filter type 2:")
                    # Name: Up
                    # Filt(x) = Orig(x) - Orig(b)
                    # Recon(x) = Filt(x) + Recon(b)
                    #All the bytes in the previous scanline have already been decoded, we can do this with
                    #a simple yet elegant list comprehension
                    unfilteredImage += (bytearray([(filteredByte + reconstructedByte)%256 for
                                                   filteredByte, reconstructedByte in
                                                   zip(decompressedData[scanlineBase + 1 :
                                                                        scanlineLength + scanlineBase + 1],
                                                       unfilteredImage[-scanlineLength + 1:])]))
                elif scanlineFilter == 3:
                    print("Filter type 3 not yet implemented")
                elif scanlineFilter == 4:
                    print("Filter type 4 not yet implemented")
else:
    print("Interlaced images decoding not yet implemented")

print("Unfiltered image:")
print(unfilteredImage)

#We now have the image data with the scanlines unfiltered. The scanlines are serialized within
#this data. The last step is decoding the interlacing, if any was applied
if interlaceMethod == 0:
    #No interlacing was applied
    if colorType == 2:
        scanlineLength8 = imageWidth * 3
        scanlineLength16 = imageWidth * 2 * 3
        for i in range(imageHeight):
            # Appending a new empty list to the list of lists
            decodedImage.append([])
            for j in range(imageWidth):
                # Treat the unfiltered data vector as a pointer to the start of a matrix
                # The data is appended to the list i of the list of lists "decodedImage", thanks python!
                #Depending on the bit depth, each channel will be made up of 8 or 16 bits, (in truecolour)
                if bitDepth == 8:
                    decodedImage[i].append((unfilteredImage[i * scanlineLength8 + 3 * j],
                                            unfilteredImage[i * scanlineLength8 + 3 * j + 1],
                                            unfilteredImage[i * scanlineLength8 + 3 * j + 2]))
                else:
                    #print("i: ",  i)
                    #print("j: ",  j)
                    #print(i * imageWidth * 2 * 3 + 3 * j * 2)
                    #scanline * ancho de la imagen * 2 bytes por canal * número de canales +
                    #  numero de canales * posicion del pixel * 2 bytes por canal
                    decodedImage[i].append((unfilteredImage[i * scanlineLength16 + 3 * j * 2:
                                                            i * scanlineLength16 + 3 * j * 2 + 2],
                                            unfilteredImage[i * scanlineLength16 + 3 * j * 2 + 2:
                                                            i * scanlineLength16 + 3 * j * 2 + 4],
                                            unfilteredImage[i * scanlineLength16 + 3 * j * 2 + 4:
                                                            i * scanlineLength16 + 3 * j * 2 + 6]))
else:
    print("Interlace decoding not yet implemented")
    exit()

if bitDepth == 16:
    for i in range(len(decodedImage)):
        print()
        for j in range(len(decodedImage[0])):
            print("%40s" % ((bytes(decodedImage[i][j][0]),
                            bytes(decodedImage[i][j][1]),
                            bytes(decodedImage[i][j][2])),), end = " ")
            #print("%3d" % (int.from_bytes(decodedImage[i][j][0],byteorder='big', signed=False)+
             #               int.from_bytes(decodedImage[i][j][1],byteorder='big', signed=False)+
              #              int.from_bytes(decodedImage[i][j][2],byteorder='big', signed=False)), end=" ")
else:
    for i in range(len(decodedImage)):
        print()
        for j in range(len(decodedImage[0])):
            print("%20s" % ((decodedImage[i][j][0],
                            decodedImage[i][j][1],
                            decodedImage[i][j][2]),), end = " ")