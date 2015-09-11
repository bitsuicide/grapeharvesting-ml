import math

def computeMAPE(predictionStep, realStep):
    numStep = len(predictionStep)
    totalMAPE = 0
    for i in range(numStep):
        totalMAPE += computePartialMAPE(predictionStep[i], realStep[i])

    totalMAPE /= numStep
    return totalMAPE

def computePartialMAPE(prediction, real):
    diff = 0
    realData = 0
    for i in range(len(real)):
        diff += (int(prediction[i]) - int(real[i])) ** 2
        realData += int(real[i]) ** 2
        print "Diff: " + str(diff) + " RealData " + str(realData)
        print str(i)
    diff = math.sqrt(diff)
    realData = math.sqrt(realData)
    return float(diff / realData)

if __name__ == "__main__":
    prediction = raw_input("Insert prediction steps: ")
    real = raw_input("Insert real steps: ")
    predictionStep = prediction.split(" ")
    realStep = real.split(" ")
    print "MAPE: " + str(computeMAPE(predictionStep, realStep))