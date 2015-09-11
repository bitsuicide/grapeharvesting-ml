import data_to_mm
import MAPE
from igraph import *
from scipy.spatial import distance
import sys
import dataset_miner

DATASET_DIR = "dataset"
FUSION_DATASET = "fusion_dataset.txt"
TEST_OUTPUT = "test.txt"

graph = None

def initGraph(stateList, transitionList, finalStateList, weather=True):
    global graph
    """ Init modified markov chain """
    graph = Graph(directed=True)
    nodeCount = len(stateList)
    graph.add_vertices(nodeCount)
    transitionMatrixProb = [[0 for x in range(nodeCount)] for x in range(nodeCount)] 
    
    # Init nodes
    for i in range(nodeCount):
        graph.vs[i]["state"] = stateList[i]
        if weather == True:
            graph.vs[i]["weather"] = {}
            graph.vs[i]["avgWeather"] = []
        if stateList[i] in finalStateList:
            graph.vs[i]["final"] = True
        else:
            graph.vs[i]["final"] = False
    
    stateValue = graph.vs["state"]
    # Init edges
    edgeSet = set()
    for trans in transitionList:
        startState = stateValue.index(trans[0])
        endState = stateValue.index(trans[1])
        transitionMatrixProb[startState][endState] += 1
        edgeSet.add((startState, endState))
        if weather == True:
                weatherDict = graph.vs[endState]["weather"]
                if trans[2] not in weatherDict:
                    weatherDict[trans[2]] = 1
                else:
                    weatherDict[trans[2]] = weatherDict[trans[2]] + 1
                graph.vs[endState]["weather"] = weatherDict
    graph.add_edges(list(edgeSet))

    if weather == True:
        # Init avg weather of nodes
        for i in range(nodeCount):
            countTransition = 0
            sumVector = [0, 0, 0, 0, 0]
            countVector = len(sumVector)
            for key, value in graph.vs[i]["weather"].iteritems():
                if key != ():
                    countTransition += value
                    for j in range(countVector):
                        sumVector[j] += key[j] * value

            if countTransition > 0:
                for h in range(countVector):
                    sumVector[h] /= countTransition
                graph.vs[i]["avgWeather"] = sumVector
            print countTransition, graph.vs[i]["avgWeather"]

    # Init weight of edges
    for edge in graph.es:
        edge["weigth"] = transitionMatrixProb[edge.source][edge.target] / float(graph.degree(edge.source, type="out"))

def euclidianDistance(v1, v2):
    """ Compute euclidian distance between w1 and w2 """
    return distance.euclidean(v1, v2)

def weatherWeigth(countProbability, weatherDistance, sourceOutDegree, smoothing=True):
    """ Compute weight with simple countProbability and weatherDistance """
    smoothing = 0
    if smoothing:
        smoothing = 1 / sourceOutDegree
    weight = (countProbability + smoothing) / (weatherDistance + smoothing)
    return weight

def fromStringToVector(stateValue):
    """ Transform from String to Vector """
    vector = []
    for i in stateValue:
        vector.append(int(i))
    return vector

def findState(inputStateValue):
    """ Choose most similar state from input state """
    vertexSeq = graph.vs.select(state=inputStateValue)
    if len(vertexSeq) == 0:
        vertexSeq = graph.vs
        inputState = fromStringToVector(inputStateValue)
        bestState = sys.maxint
        bestVertex = None
        for v in vertexSeq:
            vertexState = fromStringToVector(str(v["state"]))
            distance = euclidianDistance(inputState, vertexState)
            minimum = min(bestState, distance)
            if bestState != minimum:
                bestState = minimum
                bestVertex = v
        return bestVertex    
    return vertexSeq[0]

def nextState(sourceVertex, inputWeather, weather=True):
    """ Compute nextState that have maximum probability """
    adjVertexId = graph.neighbors(sourceVertex, mode="out") 
    print "Adiacenti: " + str(adjVertexId)
    bestVertex = None
    maxWeight = -1
    for i in adjVertexId:
        vertex = graph.vs[i]
        edge = graph.es.select(_source=sourceVertex.index, _target=i)[0]
        inputWeatherVector = fromStringToVector(inputWeather)
        if weather:
            distance = euclidianDistance(inputWeatherVector, vertex["avgWeather"])
            weight = weatherWeigth(edge["weigth"], distance, int(graph.degree(sourceVertex, type="out")))
        else:
            weight = edge["weigth"]
        if maxWeight < weight:
            bestVertex = vertex
            maxWeight = weight
    return bestVertex

def findPath(sourceVertex, inputWeatherList, weather=True):
    state = sourceVertex 
    step = 0
    statePath = [state]
    while step < len(inputWeatherList) - 1:
        newState = nextState(state, inputWeatherList[step], weather)
        if newState == None: #end of path
            break
        step += 1
        statePath.append(newState)
        state = newState
    return statePath

def startMarkov(grape, year, output, weather):
    # Read from dataset
    fileDataset = open("{0}/{1}".format(DATASET_DIR, FUSION_DATASET), "r")
    #training
    stateList, transitionList, finalStateList = data_to_mm.readStatesFromData(fileDataset, grape = grape, years = [year])
    fileDataset.close()
    #test
    fileDataset = open("{0}/{1}".format(DATASET_DIR, FUSION_DATASET), "r")
    testStateList, testTransitionList, testFinalStateList = data_to_mm.readStateFromSingleYear(fileDataset, grape = grape, year = year)
    fileDataset.close()

    realStateList = []
    realState = None
    climaList = []
    clima = None
    j = 0
    for t in testTransitionList:
        startState = str(t[0])
        if startState == "0": # new trans
            if j != 0:
                realStateList.append(realState)
                climaList.append(clima)
            realState = [startState]
            clima = [t[2]]
        else:
            realState.append(startState)
            clima.append(t[2])
        j += 1
    realStateList.append(realState)
    climaList.append(clima)

    print realStateList
    if realStateList == [None]:
        return 

    j = 0
    for rs in realStateList: # computation of all transactions
        print "Trans #" + str(j)
        print "Real State: " + str(rs)

        # Init graph
        initGraph(stateList, transitionList, finalStateList, weather)
        layout = graph.layout("kk")
        bestVertex = findState(rs[0])
        #print "Nodo di partenza: " + str(bestVertex["state"])
        print climaList[j]
        path = findPath(bestVertex, climaList[j] , weather)
        #print "Step elaborati: " + str(len(path)) + " Path: " + str(path)
        i = 0
        predictionState = []
        for step in path:
            i += 1
            predictionState.append(str(step["state"]))

        print "Prediction State " + str(predictionState)
        mape = MAPE.computeMAPE(predictionState[1:], rs[1:])
        print mape
        if output != None:
            #line = grape + "," + year + "," + str(j) + "," + str(rs) + "," + str(predictionState) + "," + str(mape) + "\n"
            line = grape + "," + year + "," + str(j) + "," + str(mape) + "\n"
            testOutput.write(line)
        j += 1
    plot(graph, layout = layout, vertex_label = graph.vs["state"], vertex_size = 35)

if __name__ == "__main__":
    """
    testOutput = open("{0}/{1}".format(DATASET_DIR, TEST_OUTPUT), "w")
    for grape in dataset_miner.GRAPE:
        for year in dataset_miner.YEAR:
            startMarkov(grape, year, testOutput, False)
    testOutput.close()
    """
    startMarkov("Trebbiano", "2003", None, False)

    
