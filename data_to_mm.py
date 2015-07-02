DATASET_DIR = "dataset"
FUSION_DATASET = "fusion_dataset.txt"
NUM_BLOCKS = 7

def generateAllStates(start, end):
    stateList = []
    stateList.append(000)
    for i in range(start, end):
        stateList.append(i)
    return stateList

def readStatesFromData(dataset):
    setElem = set()
    setElem.add(000)
    transaction = list()
    while True:
        line = dataset.readline()
        if line == "":
            break 
        splitLine = line.split(",")
        startState = 000
        endState = int("{}{}{}".format(splitLine[5], splitLine[6], splitLine[7]))
        setElem.add(endState)
        print endState
        if splitLine[2] != "#":
            startState = int("{}{}{}".format(splitLine[2], splitLine[3], splitLine[4])) 
            setElem.add(startState)
            #print startState
        transaction.append((startState, endState))
    return list(setElem), transaction

if __name__ == "__main__":
    stateList = generateAllStates(111, (NUM_BLOCKS + 1) * 111)
    fileDataset = open("{0}/{1}".format(DATASET_DIR, FUSION_DATASET), "r")
    listaStati, listaTransazioni = readStatesFromData(fileDataset)
    #print "Stati autogenerati: " + str(stateList) + " Count: " + str(len(stateList))
    #print "Stati dal dataset: " + str(listaStati) + " Count: " + str(len(listaStati))
    #print "Lista transazioni dal dataset: " + str(listaTransazioni) + " Count: " + str(len(listaTransazioni))
    fileDataset.close()


