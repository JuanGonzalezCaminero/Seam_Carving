image = open("C:\\Users\\Juan\\Desktop\\Trabajo ALGC\\Test_png.png", "rb")  # Al abrirla en modo binario,
# no se efectuan transformaciones no deseadas de los datos al leerlo
print(image.read(8))

chunkLength = int.from_bytes(image.read(4), byteorder='big', signed=False)
chunkType = image.read(4).decode("utf-8")
width = int.from_bytes(image.read(4), byteorder='big', signed=False)
height = int.from_bytes(image.read(4), byteorder='big', signed=False)
bitDepth = int.from_bytes(image.read(1), byteorder='big', signed=False)
colorType = int.from_bytes(image.read(1), byteorder='big', signed=False)
compressionMethod = int.from_bytes(image.read(1), byteorder='big', signed=False)
filterMethod = int.from_bytes(image.read(1), byteorder='big', signed=False)
interlaceMethod = int.from_bytes(image.read(1), byteorder='big', signed=False)

print("Chunk lenght: %d\n"
      "Chunk type: %s\n"
      "Image width: %d\n"
      "Image height: %d\n"
      "Bit depth: %d\n"
      "Color type: %d\n"
      "Compression method: %d\n"
      "Filter method: %d\n"
      "Interlace method: %d\n" %
      (chunkLength, chunkType, width, height, bitDepth, colorType, compressionMethod, filterMethod, interlaceMethod))



