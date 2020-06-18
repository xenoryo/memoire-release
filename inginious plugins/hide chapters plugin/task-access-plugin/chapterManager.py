import yaml
def getPassedExercises(dict, passingThreshold):
    threshold = float(passingThreshold)
    tasks_grades = dict["task_grades"]
    exercisesNames = list(tasks_grades.keys())
    passed = {}
    for name in exercisesNames:
        if (tasks_grades[name] > threshold):
            passed[name] = 1
    return passed

def isChapterPassed(passedExercises, chapterExercises):
    for exercise in chapterExercises:
        if exercise not in passedExercises:
            break
    else :
        return True
    return False


def getPassedChapters(passedExercises, exercisesDict):
    chaptersNames = list(exercisesDict.keys())
    passed = []
    for name in chaptersNames:
        if(not exercisesDict[name]):
            passed.append(name)
        else:
            bool = isChapterPassed(passedExercises, exercisesDict[name])
            if (bool == True):
                passed.append(name)
    return passed

def isChapterAllowed(allowedAndPassedId, chaptersDict, name):
    if ("condition" not in chaptersDict[name]):
        return True
    else :
        conditions = chaptersDict[name]["condition"]
        for condition in conditions:
            if condition not in allowedAndPassedId:
                break
        else :
            return True
        return False
		
def getNotAllowedChapters(allowedAndPassedId, left, passedChapters, chaptersDict):
    newChaptersDict = {}
    newLeft = []
    if(not left):
        return left
    else:
        chaptersNames = list(chaptersDict.keys())
        changes = 0
        for name in chaptersNames:

            isAllowed = isChapterAllowed(allowedAndPassedId, chaptersDict, name)
            if(isAllowed == True):
                changes += 1
                if(name in passedChapters):
                    id = chaptersDict[name]["id"]
                    allowedAndPassedId.append(id)
            else:
                newLeft.append(name)
                newChaptersDict[name] = chaptersDict[name]
        if(changes == 0):
            return left
        else:
            return getNotAllowedChapters(allowedAndPassedId, newLeft, passedChapters, newChaptersDict)


def algo(dict, chapterConfig, exerciseConfig, passingThreshold):
    chap = open(chapterConfig, "r")
    ex = open(exerciseConfig, "r")

    chaptersLoad = yaml.load(chap, Loader=yaml.FullLoader)
    chaptersDict = {}
    for chapterName, chapterInformation  in chaptersLoad.items():
        chaptersDict[chapterName] = chapterInformation

    exercisesLoad = yaml.load(ex, Loader=yaml.FullLoader)
    exercisesDict = {}
    for chapterName, chapterExercises in exercisesLoad.items():
        exercisesDict[chapterName] = chapterExercises

    passedExercises = getPassedExercises(dict, passingThreshold)
    passedChapters = getPassedChapters(passedExercises,exercisesDict)
    return getNotAllowedChapters([],[" "], passedChapters, chaptersDict)
