DATASET_DIR = "dataset"
FUSION_DATASET = "fusion_dataset.txt"
NUM_BLOCKS = 7

def generateAllStates(start, end):
    stateList = []
    stateList.append(000)
    for i in range(start, end):
        stateList.append(i)
    return stateList

def readStatesFromData(dataset, grape=None, years=None):
    setElem = set()
    setElem.add(000)
    transaction = list()
    finalState = set()
    lastEndState = None
    while True:
        line = dataset.readline()
        if line == "":
            break 
        splitLine = line.split(",")
        grapeValue = splitLine[0]
        yearsValue = splitLine[1]
        if (grape == None or grapeValue == grape) and (years == None or yearsValue not in years):
            startState = 000
            endState = int("{}{}{}".format(splitLine[5], splitLine[6], splitLine[7]))
            weather = (float(splitLine[8]), float(splitLine[9]), float(splitLine[10]), float(splitLine[11]), float(splitLine[12]))
            setElem.add(endState)
            #print endState
            if splitLine[2] != "#":
                startState = int("{}{}{}".format(splitLine[2], splitLine[3], splitLine[4])) 
                setElem.add(startState)
            elif lastEndState != None:
                finalState.add(lastEndState)
            transaction.append((startState, endState, weather))
            lastEndState = endState
    return list(setElem), transaction, list(finalState)

def readStateFromSingleYear(dataset, grape, year):
    setElem = set()
    setElem.add(000)
    transaction = list()
    finalState = set()
    lastEndState = None
    while True:
        line = dataset.readline()
        if line == "":
            break 
        splitLine = line.split(",")
        grapeValue = splitLine[0]
        yearsValue = splitLine[1]
        if (grape == None or grapeValue == grape) and yearsValue == year:
            startState = 000
            endState = int("{}{}{}".format(splitLine[5], splitLine[6], splitLine[7]))
            weather = (float(splitLine[8]), float(splitLine[9]), float(splitLine[10]), float(splitLine[11]), float(splitLine[12]))
            setElem.add(endState)
            #print endState
            if splitLine[2] != "#":
                startState = int("{}{}{}".format(splitLine[2], splitLine[3], splitLine[4])) 
                setElem.add(startState)
            elif lastEndState != None:
                finalState.add(lastEndState)
            transaction.append((startState, endState, weather))
            lastEndState = endState
    return list(setElem), transaction, list(finalState)

if __name__ == "__main__":
    stateList = generateAllStates(111, (NUM_BLOCKS + 1) * 111)
    fileDataset = open("{0}/{1}".format(DATASET_DIR, FUSION_DATASET), "r")
    listaStati, listaTransazioni = readStatesFromData(fileDataset)
    #print "Stati autogenerati: " + str(stateList) + " Count: " + str(len(stateList))
    #print "Stati dal dataset: " + str(listaStati) + " Count: " + str(len(listaStati))
    #print "Lista transazioni dal dataset: " + str(listaTransazioni) + " Count: " + str(len(listaTransazioni))
    fileDataset.close()
