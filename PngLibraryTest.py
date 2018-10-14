import png

pngReader = png.Reader(filename="Assets\\testbn.png")
print(list(pngReader.asRGB()[2]))