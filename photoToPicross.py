from PIL import Image
import os
import math
import numpy as np

imgFolder = "./testImages/"
resultsFolder = "./resultPuzzles/"

posSizes = [(5,5), (10,10), (15,15), (20,20), (25,25)]

targetHeight = 20

def closestPuzzleSize(currentSize, possibleSizes):
    differences = []
    for posSize in possibleSizes:
        xDiff = abs(currentSize[0] - posSize[0])
        yDiff = abs(currentSize[1] - posSize[1])
        diff = math.sqrt(xDiff*xDiff + yDiff*yDiff)
        differences.append(diff)

    minDiff = min(differences)
    return possibleSizes[differences.index(minDiff)]

def pixelate(img):
    imgSmall = img.reduce(4)

    imgMaxSize = max(img.width, img.height)
    pixelImg = imgSmall.resize(img.size, Image.NEAREST)

    return pixelImg

def imageToPicross(imagePath, targetHeight):
    testImg = Image.open(imagePath)

    ratioWidthToHeight = testImg.width / testImg.height
    puzzleSizeImg = testImg.resize((int(targetHeight * ratioWidthToHeight), targetHeight), Image.NEAREST)

    threshold = np.mean(puzzleSizeImg)
    func = lambda x: 255 if x > threshold else 0

    imgGrey = puzzleSizeImg.convert(mode="L")  # Convert to greyscale
    puzzleImg = imgGrey.point(func, mode="1")  # Convert to black & white

    puzzleRows = (~np.asarray(puzzleImg) * 1).tolist()
    puzzleCols = [[row[j] for row in puzzleRows] for j in range(puzzleImg.width)]

    return (puzzleRows, puzzleCols)

    # # Save monochrome puzzle image for testing
    # puzzleImgName = resultsFolder + "Picross " + testImgName
    # print(puzzleImgName + "\n" + str(puzzleRows) + "\n" + str(puzzleCols))
    # if not os.path.exists(puzzleImgName):
    #   puzzleImg.save(puzzleImgName)

# if not os.path.exists(resultsFolder):
#     os.makedirs(resultsFolder)
