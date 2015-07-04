import data_to_mm
from igraph import *
from scipy.spatial import distance
import sys

DATASET_DIR = "dataset"
FUSION_DATASET = "fusion_dataset.txt"

def initGraph(stateList, transitionList, finalStateList, weather=True):
    """ Initi modified markov chain """
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
    return graph

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
    while state["final"] != True or step > len(inputWeatherList):
        newState = nextState(state, inputWeatherList[step], weather)
        step += 1
        statePath.append(newState)
        state = newState
    return statePath

if __name__ == "__main__":
    # Read from dataset
    fileDataset = open("{0}/{1}".format(DATASET_DIR, FUSION_DATASET), "r")
    stateList, transitionList, finalStateList = data_to_mm.readStatesFromData(fileDataset, grape = "Merlot")
    fileDataset.close()

    # Init graph
    graph = initGraph(stateList, transitionList, finalStateList, True)
    layout = graph.layout("kk")
    bestVertex = findState("000")
    print "Nodo di partenza: " + str(bestVertex["state"])
    path = findPath(bestVertex, [[83043.0,1826.0,620768.0,15.0,231.0], [0.0,78.0,1359.0,16.0,13.0], [0.0,115.0,2341.0,12.0,14.0], [0.0,102.0,829.0,15.0,7.0], [67.0,70.0,3786.0,12.0,35.0], [0.0,99.0,4269.0,13.0,28.0]], True)
    print "Step elaborati: " + str(len(path)) + " Path: " + str(path)
    #print graph.vs["weather"]
    #plot(graph, layout = layout)
    
