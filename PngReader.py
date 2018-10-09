import zlib

#image = open("C:\\Users\\JuanG\\Desktop\\readTest.png", "rb") #Al abrirla en modo binario,
image = open("C:\\Users\\Juan\\Desktop\\Trabajo ALGC\\test_blanco.png", "rb") #Al abrirla en modo binario,
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
    if colorType == 2:
        #for color type 2 there are 2 possibilities for the bit depth, 8 and 16
        if bitDepth == 8:
            for i in range(imageHeight):
                #línea que queremos leer * ancho de la imágen  * número de canales +
                # + línea que queremos leer (ya que los bytes que contienen el filtro
                # hacen que las lineas sean 1 byte más largas y hay que compensarlo) , de
                #esta forma obtenemos la posición del inicio de la siguiente scanline
                scanlineFilter = decompressedData[i * imageWidth * 3 + i]
                if scanlineFilter == 0:
                    #No filter was applied
                    unfilteredImage += (decompressedData[i * imageWidth * 3 + i + 1 : (i + 1) * imageWidth * 3 + i + 1])
                else:
                    print("Filter decoding not yet implemented")
        else:
            for i in range(imageHeight):
                # línea que queremos leer * ancho de la imágen  * número de canales * 2 +
                # + línea que queremos leer (ya que los bytes que contienen el filtro
                # hacen que las lineas sean 1 byte más largas y hay que compensarlo) , de
                # esta forma obtenemos la posición del inicio de la siguiente scanline
                #Se multiplica por 2 ya que cada posición contiene un byte y con esta profundidad
                #de bits cada canal tiene 2 bytes
                scanlineFilter = decompressedData[i * imageWidth * 3 * 2 + i]
                #print(i * imageWidth * 3 * 2 + i)
                #print(scanlineFilter)
                if scanlineFilter == 0:
                    #No filter was applied
                    unfilteredImage += (decompressedData[i * imageWidth * 3 * 2 + i + 1 : (i + 1) * imageWidth * 3 * 2 + i + 1])
                else:
                    print("Filter decoding not yet implemented")
else:
    print("Interlaced images decoding not yet implemented")

print("Unfiltered image:")
print(unfilteredImage)

#We now have the image data with the scanlines unfiltered. The scanlines are serialized within
#this data. The last step is decoding the interlacing, if any was applied
if interlaceMethod == 0:
    #No interlacing was applied
    if colorType == 2:
        for i in range(imageHeight):
            # Appending a new empty list to the list of lists
            decodedImage.append([])
            for j in range(imageWidth):
                # Treat the unfiltered data vector as a pointer to the start of a matrix
                # The data is appended to the list i of the list of lists "decodedImage", thanks python!
                #Depending on the bit depth, each channel will be made up of 8 or 16 bits, (in truecolour)
                if bitDepth == 8:
                    decodedImage[i].append((unfilteredImage[i * imageWidth * 3 + 3 * j],
                                            unfilteredImage[i * imageWidth * 3 + 3 * j + 1],
                                            unfilteredImage[i * imageWidth * 3 + 3 * j + 2]))
                else:
                    #print("i: ",  i)
                    #print("j: ",  j)
                    #print(i * imageWidth * 2 * 3 + 3 * j * 2)
                    #scanline * ancho de la imagen * 2 bytes por canal * número de canales +
                    #  numero de canales * posicion del pixel * 2 bytes por canal
                    decodedImage[i].append((unfilteredImage[i * imageWidth * 2 * 3 + 3 * j * 2:
                                                            i * imageWidth * 2 * 3 + 3 * j * 2 + 2],
                                            unfilteredImage[i * imageWidth * 2 * 3 + 3 * j * 2 + 2:
                                                            i * imageWidth * 2 * 3 + 3 * j * 2 + 4],
                                            unfilteredImage[i * imageWidth * 2 * 3 + 3 * j * 2 + 4:
                                                            i * imageWidth * 2 * 3 + 3 * j * 2 + 6]))
else:
    print("Interlace decoding not yet implemented")
    exit()

for i in range(len(decodedImage)):
    print()
    for j in range(len(decodedImage[0])):
        print("%10s" % ((bytes(decodedImage[i][j][0]),
                        bytes(decodedImage[i][j][0]),
                        bytes(decodedImage[i][j][0])),), end = " ")
        #print("%3d" % (int.from_bytes(decodedImage[i][j][0],byteorder='big', signed=False)+
         #               int.from_bytes(decodedImage[i][j][1],byteorder='big', signed=False)+
          #              int.from_bytes(decodedImage[i][j][2],byteorder='big', signed=False)), end=" ")