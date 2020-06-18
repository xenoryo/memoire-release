
import sys, os
import glob
from PIL import Image
import json
import sys
import yaml
from bs4 import BeautifulSoup




def writeAppConfigFile(dst, exercises):
    dict = {}
    dict["course"] = ingiCourseName
    dict["basicChapterConfig"] = getBasicConfig(dst + "/chapterConfig_" + ingiCourseName + ".yaml")
    dict["freeChapterConfig"] = []
    dict["exercises"] = exercises
    dict["passingThreshold"] = "50.0"
    file = open(dst + "/_static/js/appConfig.json", 'w')
    json.dump(dict, file)

def checkIfChapterAlreadySelected(chapter, selected):
    if chapter not in selected:
        selected[chapter] = 1
        return selected, False
    return selected, True

def writeChapterConfigFile(dst):
    chapters = []
    selected = {}
    finalDict = {}
    indexHTML = dst + "/index.html"
    file = open(indexHTML, 'r')
    parsedHTML = BeautifulSoup(file, 'html.parser')
    counter = 0
    for element in parsedHTML.find_all('a', href=True):
        ressource = element["href"]
        if "http://" not in ressource and "#" not in ressource and "html" in ressource:

            ressource = ressource.split(".html")[0]
            selected, alreadyAdded = checkIfChapterAlreadySelected(ressource, selected)
            if alreadyAdded == False:
                dict = {}
                if counter != 0:
                    dict["condition"] = [counter - 1]

                dict["id"] = counter
                finalDict[ressource] = dict
                counter += 1
                chapters.append(dict)

    file = open(dst + "/chapterConfig_" + ingiCourseName + ".yaml", 'w')
    yaml.dump(finalDict, file)
    return counter

def addPrefix(exercises, prefix):
    newExercises = []
    for exercise in exercises :
        newExercises.append(prefix + exercise)
    return newExercises

def writeExercisesConfigFile(src, dst):
    dict = {}
    subChapterParent = {}
    exercises = []
    vanillaExercises = []
    # checks every .rst file in src and maps what chapters are in which folder
    for r,d,f in os.walk(src):
        for file in f:
            if ".rst" in file:
                # folder = position of the chapter relatively to the root 
                folder = r.split("/")[-1]                               
                if folder != src.split("/")[-1] :
                    chapterName = folder + "/" + file.split(".rst")[0]
                else :
                    chapterName = file.split(".rst")[0]
                
                path = os.path.join(r, file)
                subChapters = getSubChapter(path)
                for subChapter in subChapters :
                    subChapterParent[subChapter] = chapterName

    for r, d, f in os.walk(src):
        for file in f:
            if ".rst" in file:

                folder = r.split("/")[-1]
                if folder != src.split("/")[-1] :
                    chapterName = folder + "/" + file.split(".rst")[0]
                else :
                    chapterName = file.split(".rst")[0]

                path = os.path.join(r, file)
                if chapterName in subChapterParent:

                    exerciseList = getInginiousExercisesFromRSTFiles(path)
                    dict = addExerciseListToChapter(dict, subChapterParent[chapterName], exerciseList)
                else :
                    exerciseList = getInginiousExercisesFromRSTFiles(path)
                    dict = addExerciseListToChapter(dict, chapterName, exerciseList)
                vanillaExercises = vanillaExercises + exerciseList
                exercises = exercises + addPrefix(exerciseList, "/lti/" + ingiCourseName + "/")
    
    file = open(dst + "/exerciseConfig_" + ingiCourseName + ".yaml", 'w')
    yaml.dump(dict, file)

    s = listToString(exercises)
    source = open("setupPWA/templateSWINGInious.txt", "r")
    dst = open(dst + "/ingi-service-worker.js", "w+")
    lines = source.readlines()

    for l in lines:
        if (l[:-1] == "$1"):
            dst.write(s)
        else:
            dst.write(l)

    dst.close()
    source.close()
    return vanillaExercises

def addExerciseListToChapter(dict, chapterName, exerciseList):
    if chapterName in dict :
        dict[chapterName] = dict[chapterName] + exerciseList
    else:
        dict[chapterName] = exerciseList
    return dict

def getSubChapter(path):
    subChapters = []
    f = open(path, "r")
    lines = f.readlines()
    for x in lines:
        if "include::" in x:
            y = x.split("include:: ")[1]
            if ".rst" in y :
                z = y.split(".rst")[0]
                ressource = z.split("/")[-1]
                subChapters.append("".join(ressource.split()))
    return subChapters

def getInginiousExercisesFromRSTFiles(path):
    exercises = []
    f = open(path, "r")
    lines = f.readlines()
    for x in lines:
        if "inginious::" in x:
            ressource = x.split("inginious:: ")[1]
            exercises.append("".join(ressource.split()))
    return exercises


def setup(app):
    # executes getFilesList when sphinx reaches the "build-finished" event
    app.add_js_file('js/CourseManager.js')
    app.add_js_file('js/Inginious.js')
    app.add_js_file('js/LocationManager.js')
    app.add_js_file('js/Syllabus.js')
    app.add_js_file('js/Utils.js')
    app.add_js_file('js/base.js')

    app.connect('build-finished', buildConfigAndPWA)

def buildConfigAndPWA(app, exception):
    exercisesList = writeExercisesConfigFile(app.srcdir, app.outdir)
    numberOfChapters = writeChapterConfigFile(app.outdir)
    writeAppConfigFile(app.outdir, exercisesList)
    writeServiceWorker(app.outdir)
    writeManifest(app.srcdir, app.outdir)
    numberOfChapters = numberOfChapters + 1
    if(numberOfChapters > 200):
        print("There are " + str(numberOfChapters) + " chapters in this syllabus, it is possibly unwise to use the learning path feature depending on the learning path you plan set")
    else:
        if(numberofChapters > 500):
            print("There are " + str(numberOfChapters) + " chapters in this syllabus, as a result the learning path feature will be disabled")


def listToString(list):
    s = "\'" + list[0] + "\'"
    for i in range(1, len(list)):
        s += ",\n"
        s += "\'" + list[i] + "\'"
    s += "\n"
    return s


def getOutputFolder(path):
    folders = path.split("/")
    return folders[-1]


def getTruePath(dst, path):
    folders = path.split("/")
    truePath = "/"
    for i in range(len(folders)):
        if folders[i] == dst:
            for j in range(i + 1, len(folders)):
                truePath += folders[j] + "/"
            break
    return truePath


def getListOfFilesToCache(dst):
    files = []
    # r=root, d=directories, f = files
    outDir = getOutputFolder(dst)
    for r, d, f in os.walk(dst):

        truePath = getTruePath(outDir, r)
        for file in f:

            if ".doctree" not in file and ".buildinfo" not in file and ".pickle" not in file:
                path = pathToSyllabus + os.path.join(truePath, file)
                files.append(path)

    return files


def writeServiceWorker(dst):
    filesToCache = getListOfFilesToCache(dst)
    s = listToString(filesToCache)
    source = open("setupPWA/templateSW.txt", "r")
    dst = open(dst + "/sw.js", "w+")
    lines = source.readlines()

    for l in lines:
        if (l[:-1] == "$1"):
            dst.write(s)
        else:
            dst.write(l)

    dst.close()
    source.close()



#JSON
def writeManifest(sourceDir, outputDir):
    source = open("setupPWA/theme/pwa/static/json/config.yaml","r")
    config = yaml.load(source, Loader=yaml.FullLoader)
    data = {}
    for field, value  in config.items():
        data[field] = value
    if(len(data) < 6):
        print("wrong manifest config")
    data['start_url'] = pathToSyllabus + "/" + master_doc + ".html"
    data['icons'] = []
	
    files = [f for f in glob.glob(sourceDir + "/setupPWA/theme/pwa/static/json/img/icons/*.png", recursive=True)]
    for f in files:
        p = f.split("/")
        src = "_static/json/img/icons/" + p[-1]
        type = "image/png"
        im = Image.open(f)
        width, height = im.size
        sizes = str(width) + "x" + str(height)
        data['icons'].append({
            'src': src,
            'type': type,
            'sizes': sizes})
    with open(outputDir + '/manifest.json', 'w') as outfile:
        json.dump(data, outfile)
	
#App config

def getPassedExercises(dict):
    tasks_grades = dict["task_grades"]
    exercisesNames = list(tasks_grades.keys())
    passed = {}
    for name in exercisesNames:
        if (tasks_grades[name] > 50.0):
            passed[name] = 1
    return passed


def isChapterPassed(passedExercises, chapterExercises):
    for exercise in chapterExercises:
        if exercise not in passedExercises:
            break
    else:
        return True
    return False


def getPassedChapters(passedExercises, exercisesDict):
    chaptersNames = list(exercisesDict.keys())
    passed = []
    for name in chaptersNames:
        if (not exercisesDict[name]):
            passed.append(name)
        else:
            bool = isChapterPassed(passedExercises, exercisesDict[name])
            if (bool == True):
                passed.append(name)
    return passed


def isChapterAllowed(allowedAndPassedId, chaptersDict, name):
    if ("condition" not in chaptersDict[name]):
        return True
    else:
        conditions = chaptersDict[name]["condition"]
        for condition in conditions:
            if condition not in allowedAndPassedId:
                break
        else:
            return True
        return False


def getNotAllowedChapters(allowedAndPassedId, left, passedChapters, chaptersDict):
    newChaptersDict = {}
    newLeft = []
    if (not left):
        return left
    else:
        chaptersNames = list(chaptersDict.keys())
        changes = 0
        for name in chaptersNames:

            isAllowed = isChapterAllowed(allowedAndPassedId, chaptersDict, name)
            if (isAllowed == True):
                changes += 1
                if (name in passedChapters):
                    id = chaptersDict[name]["id"]
                    allowedAndPassedId.append(id)
            else:
                newLeft.append(name)
                newChaptersDict[name] = chaptersDict[name]
        if (changes == 0):
            return left
        else:
            return getNotAllowedChapters(allowedAndPassedId, newLeft, passedChapters, newChaptersDict)


def getBasicConfig(chapterConfig):
    chapters = open(chapterConfig, "r")

    chaptersLoad = yaml.load(chapters, Loader=yaml.FullLoader)
    chaptersDict = {}
    for chapterName, chapterInformation in chaptersLoad.items():
        chaptersDict[chapterName] = chapterInformation
    return getNotAllowedChapters([], [" "], [], chaptersDict)