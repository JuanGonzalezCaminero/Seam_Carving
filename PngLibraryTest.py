import png


pngReader = png.Reader(filename="Assets\\calle.png")
image = pngReader.asRGB()
#print(list(pngReader.asRGB()[2]))
print(image)