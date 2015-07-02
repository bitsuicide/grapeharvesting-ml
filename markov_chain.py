import data_to_mm
from igraph import *

DATASET_DIR = "dataset"
FUSION_DATASET = "fusion_dataset.txt"

def initGraph(stateList, transitionList, finalStateList, weather=True):
    graph = Graph(directed=True)
    nodeCount = len(stateList)
    edgeCount = len(transitionList)
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
    edgeList = []
    for trans in transitionList:
        startState = stateValue.index(trans[0])
        endState = stateValue.index(trans[1])
        transitionMatrixProb[startState][endState] += 1
        edgeList.append((startState, endState))
        if weather == True:
                weatherDict = graph.vs[endState]["weather"]
                if trans[2] not in weatherDict:
                    weatherDict[trans[2]] = 1
                else:
                    weatherDict[trans[2]] = weatherDict[trans[2]] + 1
                graph.vs[endState]["weather"] = weatherDict
    graph.add_edges(edgeList)

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
    for i in range(edgeCount):
        graph.es[i]["weigth"] = transitionMatrixProb[graph.es[i].source][graph.es[i].target] / float(graph.degree(graph.es[i].source, type="out"))
    return graph

if __name__ == "__main__":
    # Read from dataset
    fileDataset = open("{0}/{1}".format(DATASET_DIR, FUSION_DATASET), "r")
    stateList, transitionList, finalStateList = data_to_mm.readStatesFromData(fileDataset, grape = "Merlot")
    fileDataset.close()

    # Init graph
    graph = initGraph(stateList, transitionList, finalStateList, True)
    layout = graph.layout("kk")
    #print graph.vs["weather"]
    #plot(graph, layout = layout)
    
