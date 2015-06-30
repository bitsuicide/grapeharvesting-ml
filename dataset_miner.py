# Create new dataset from pre-harvest and weather data

import datetime, sys, math

DATASET_DIR = "dataset"
WEATHER_DATASET = "meteo.csv"
PREHARVEST_DATASET = "DatasetPreHarvest.txt"
NEWDATASET = "fusion_dataset.txt"

# Pre-harvest constant
GRAPE_ID = 0
VIGNETO_ID = 1
ZUCCHERI_ID = 2
ACIDITA_ID = 3
PH_ID = 4
DATA_ID = 5
YEAR = ["2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014"]
GRAPE = ["CabernetSauvignon", "Merlot", "Sangiovese", "Syrah", "Trebbiano"]
BLANK_SYMBOL = "?"

# Weather constant
W_DATA_ID = 1
W_TMIN_ID = 2
W_TAVG_ID = 3
W_TMAX_ID = 4
W_RAIN_ID = 5
MIN_TEMP = 0
FIRSTDAY_WEATHER = "01/04"

NUM_BLOCKS = 5
SEPARATOR = ","
INDEX_NAME = ["sugar", "acidity", "ph", "fregoniIndex", "huglinIndex", "branasIndex", "thermalExcursion", "rain"] 

minMaxValueHD = None
minMaxValueWD = None

def initGrapeList():
    """ Initialize grape pre-harvest list """
    grapeDict = dict()
    for gp in GRAPE:
        grapeDict[gp] = dict()
        for y in YEAR:
            grapeDict[gp][y] = list()
    return grapeDict

def readWeather(dataset):
    """ Read from file weather dataset """
    global weatherData, minMaxValueWD
    dataset.readline()
    minValueRain = minValueTE = sys.float_info.max
    maxValueRain = maxValueTE = 0

    while True:
        line = dataset.readline()
        if line == "":
            break
        lineSplit = line.split(SEPARATOR)
        temp_min = lineSplit[W_TMIN_ID]
        temp_avg = lineSplit[W_TAVG_ID]
        temp_max = lineSplit[W_TMAX_ID]
        rain = lineSplit[W_RAIN_ID]
        date = lineSplit[W_DATA_ID].translate(None, "\"")
        weatherData[date] = (temp_min, temp_avg, temp_max, rain)
        minValueRain = min(minValueRain, float(rain))
        maxValueRain = max(maxValueRain, float(rain))
        fTempMax = float(temp_max)
        fTempMin = float(temp_min)
        temporalExcursion = fTempMax - fTempMin
        if fTempMax != fTempMin:
            minValueTE = min(minValueTE, temporalExcursion)
            maxValueTE = max(maxValueTE, temporalExcursion)

    minMaxValueWD = [[minValueRain, maxValueRain], [minValueTE, maxValueTE]]

def readPreHarvest(dataset):
    """ Read from file pre-harvest dataset """
    global harvestData, minMaxValueHD
    minValueSugar = minValueAcidity = minValuePH = sys.float_info.max
    maxValueSugar = maxValueAcidity = maxValuePH = 0
    dataset.readline()
    while True:
        line = dataset.readline()
        if line == "":
            break
        lineSplit = line.split(SEPARATOR)
        #print lineSplit
        if not BLANK_SYMBOL in lineSplit:
            year = lineSplit[DATA_ID].split("/")[-1].strip()
            sugar = lineSplit[ZUCCHERI_ID]
            acidity = lineSplit[ACIDITA_ID]
            ph = lineSplit[PH_ID]
            data = lineSplit[DATA_ID].strip()
            harvestData[lineSplit[GRAPE_ID]][year].append((data, sugar, acidity, ph))
            minValueSugar = min(minValueSugar, float(sugar))
            maxValueSugar = max(maxValueSugar, float(sugar))
            minValueAcidity = min(minValueAcidity, float(acidity))
            maxValueAcidity = max(maxValueAcidity, float(acidity))
            minValuePH = min(minValuePH, float(ph))
            maxValuePH = max(maxValuePH, float(ph))

    minMaxValueHD = [[minValueSugar, maxValueSugar], [minValueAcidity, maxValueAcidity], [minValuePH, maxValuePH]]

def dateRange(dateStart, dateEnd):
    for n in range(int ((dateEnd - dateStart).days)):
        yield dateStart + datetime.timedelta(n)

def computeWeatherData(dateStart, dateEnd):
    """ Compute weather index """
    tempDate = dateStart.split("/")
    startDate = datetime.date(int(tempDate[2]), int(tempDate[1]), int(tempDate[0]))
    tempDate = dateEnd.split("/")
    endDate = datetime.date(int(tempDate[2]), int(tempDate[1]), int(tempDate[0]))
    thermalExcursion = 0
    fregoniIndex = 0
    huglinIndex = 0
    branasIndex = 0
    h = 0
    rain = 0
    dayCount = 0

    for date in dateRange(startDate, endDate):
        dayCount += 1
        currentDate = date.strftime("%d/%m/%Y")
        try:
            wheaterLine = weatherData[currentDate]
            tempAvg = float(wheaterLine[W_TAVG_ID - 2])
            tempMin = float(wheaterLine[W_TMIN_ID - 2])
            tempMax = float(wheaterLine[W_TMAX_ID - 2])
            sumThermalExcursion += tempMax - tempMin
            if tempMin < MIN_TEMP:
                h += 1
            huglinIndex += tempAvg + (tempMax - 20)
            branasIndex += tempAvg
            rain += float(wheaterLine[W_RAIN_ID - 2])
        except KeyError:
            print "Day " + currentDate + " is not available"

    thermalExcursion = sumThermalExcursion / dayCount        
    fregoniIndex = sumThermalExcursion * h
    huglinIndex = huglinIndex * (1.02 / 2)
    branasIndex *= rain
    return (fregoniIndex, huglinIndex, branasIndex, thermalExcursion, rain)

def computeDataInterval():
    """ Compute interval for block """
    intervalList = []
    maxMinValue = minMaxValueHD + [[0, 200], [0, 200], [0, 200]] + minMaxValueWD
    print maxMinValue
    for index in range(len(maxMinValue)):
        minValue = maxMinValue[index][0]
        distance = (maxMinValue[index][1] - minValue) / NUM_BLOCKS
        maxRangeValue = []
        for block in range(0, NUM_BLOCKS):
            i = block + 1
            maxRangeValue.append((math.ceil((minValue + (i * distance)) * 100)) / 100)
        intervalList.append(maxRangeValue)
    return intervalList

if __name__ == "__main__":
    fileWeather = open("{0}/{1}".format(DATASET_DIR, WEATHER_DATASET), "r")
    filePreHarvest = open("{0}/{1}".format(DATASET_DIR, PREHARVEST_DATASET), "r")
    #fileNewDataset = open("{0}/{1}".format(DATASET_DIR, NEWDATASET), "w")

    harvestData = initGrapeList()
    readPreHarvest(filePreHarvest)
    weatherData = dict()
    readWeather(fileWeather)
    #print minMaxValueWD
    #print minMaxValueHD
    intervalList = computeDataInterval()
    print intervalList
    #print computeWeatherData("20/9/2010", "27/9/2010")
    #print str(harvestData)
    #print str(weatherData)

    fileWeather.close()
    filePreHarvest.close()
    #fileNewDataset.close()
