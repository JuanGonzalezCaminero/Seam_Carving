import zlib

image = open("C:\\Users\\JuanG\\Desktop\\readTest.png", "rb") #Al abrirla en modo binario,
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
decodedImage = [][]

#Reading the image and extracting the main parameters
while chunkType != "IEND":
       #Reads the next chunk content length
       chunkLength = int.from_bytes(image.read(4), byteorder='big', signed=False)
       #Reads the chunk type
       chunkType = image.read(4).decode("utf-8")
       #Switch using the chunk type
       if chunkType == "IHDR":
              width = int.from_bytes(image.read(4), byteorder='big', signed=False)
              height = int.from_bytes(image.read(4), byteorder='big', signed=False)
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
              imageBytes += bytearray(image.read(chunkLength))
              # Skips the CRC
              image.read(4)

       #Non-essential chunks, for now I will just ignore them
       else:
              image.read(chunkLength)
              image.read(4)

#Now the image data is stored in a bytearray. The image data is first filtered and compressed after that,
#we need to decode it before it can be used. The data in png is compressed using the zlib "deflate" algorithm,
#I will use a library to decompress it
decompressedData = zlib.decompress(imageBytes, wbits=zlib.MAX_WBITS, bufsize=zlib.DEF_BUF_SIZE)
#decompressedData is the decompressed version of the filtered image, which means we still have to decode
#the filtering to access the actual data
print(len(decompressedData))
print(decompressedData)


#This applies if truecolour is used, for indexed colour a different method must be applied
if(filterMethod == 0):
       #If the filtering method is 0, no filtering was applied
       for i in range(imageHeight):
              for j in range(imageWidth):
                     decodedImage[imageHeight][imageWidth] =
                            
else:
       print("Filter decoding not yet implemented")
