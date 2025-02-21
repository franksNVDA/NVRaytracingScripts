import pandas as pd
import re
import os
import pathlib
SVNPath = "D:/MmWork/UE5.1.1_DLSS4/Engine"
GitPath = "D:/NV/UE5.1.1_DLSS4/Engine"

#SVNPath = "D:/NV/UE5.1.1_DLSS4/Engine"
#GitPath = "D:/MmWork/UE5.1.1_DLSS4/Engine"

DifferFilesPath = ""


MergeEnginePath = "D:/SVNMergeFiles/Engine"

CompareFolders = [#"Config",
                  #"Plugins/Experimental",
                  #"Plugins/FX/Niagara/Source/Niagara/Private",
                  #"Plugins/MovieScene",
                  #"Plugins/Runtime/GeometryCache",
                  #"Plugins/Runtime/ProceduralMeshComponent",
                  #"Source/Editor/UnrealEd/Private",
                  #"Source/Runtime/AutomationMessages",
                  "Source/Runtime/Core",
                  "Source/Runtime/D3D12RHI",
                  "Source/Runtime/Engine",
                  #"Source/Runtime/Experimental",
                  #"Source/Runtime/Landscape",
                  #"Source/Runtime/Launch",
                  "Source/Runtime/RenderCore",
                  "Source/Runtime/Renderer",
                  "Source/Runtime/RHI",
                  #"Source/Runtime/VulkanRHI",
                  "Source/Runtime/Windows",
                  "Source/ThirdParty/NVIDIA",
                  #"Plugins/Runtime/Nvidia",
                  "Shaders"
                  ]
ExcludeFolders = ["Shaders/Shared/ThirdParty",
                  "Source/ThirdParty/NVIDIA/nvapi"] # avoid UTF-8 open failure
# avoid UTF-8 open failure
ExcludeFiles = ["ACES.ush",
                "DLSSUpscaler.cpp"]

FileSuffixs = [".h", ".cpp", ".ush", ".usf"]

# stream output vars 
ChangedFilesName = "GitSVNChangedFiles.txt"
NVModifiedFilesPath = "NVModifiedFiles.txt"
MergeExclusiveFilesPath = "MergeExclusiveFiles.txt"


# vars
nvModifiedFiles = {}

currentOutFile = {}
nvChangedFiles = []
clientChangedFiles = []
currentChangedFiles = []

nvChangedOnlyFiles = []
bothChangedFiles = []
nvAddedFiles = []



class FilePathPair(object):
    def __init__(self, fileName, filePath):
        self.FileName = fileName
        self.FilePath = filePath

class FilePath(object):
    def __init__(self, fileName, nvPath, clientPath):
        self.FileName = fileName
        self.FileNVPath = nvPath
        self.FileClientPath = clientPath


def Check(directoryPath):
 
    # Checking if the directory exists or not
    if os.path.exists(directoryPath):
         # Checking if the directory is empty or not
        if len(os.listdir(directoryPath)) == 0:
            print("No files found in ", directoryPath)
            return False
        else:
            return True
    else:
        print(directoryPath, " does not exist !")
        return False

def IsFile(path):
    if os.path.isfile(path):
        suffix = pathlib.Path(path).suffix
        if suffix in FileSuffixs:
            return True
    return False

def IsFolder(path):
    if os.path.isdir(path):
        return True
    else:
        return False

def CreatePath(PathA, PathB):
    return PathA + "/" + PathB

def IsSameFile(fileDataA, fileDataB):
    reFileDataA = ""
    reFileDataB = ""
    for line in fileDataA:
        reFileDataA += re.sub(r'[\d\.\ \n\t]', '', line)
    
    for line in fileDataB:
        reFileDataB += re.sub(r'[\d\.\ \n\t]', '', line)

    if reFileDataA != reFileDataB:
        return False
    else:
        return True

def DiffFile(fileA, fileB):
    fileDataA = {}
    fileDataB = {}
    with open(fileA, 'r', encoding='utf-8') as fA:
        fileDataA = fA.readlines()

    with open(fileB, 'r', encoding='utf-8') as fB:
        fileDataB = fB.readlines()
    if IsSameFile(fileDataA, fileDataB):
        return
    else:
        currentOutFile.write(fileA + '\n')
        currentChangedFiles.append(FilePathPair(pathlib.Path(fileA).name, fileA))
        print(fileB)
    
def CompareFolderInternal(PathA, PathB, bCollectNVAddedFiles, OutputPath):
    if IsFile(PathA) and IsFile(PathB) and pathlib.Path(PathB).name not in ExcludeFiles:
        DiffFile(PathA, PathB)
        return
    if IsFolder(PathA) and IsFolder(PathB) and PathB not in ExcludeFolders:
        dirsA = os.listdir(PathA)
        dirsB = os.listdir(PathB)
        for dir in dirsA:
            CompareFolderInternal(CreatePath(PathA, dir), CreatePath(PathB, dir), bCollectNVAddedFiles, CreatePath(OutputPath, dir))
        return
    if bCollectNVAddedFiles:
        if IsFile(PathA) and not IsFile(PathB):
            nvAddedFiles.append(FilePath(pathlib.Path(PathA).name, PathA, OutputPath))
            return
        if IsFolder(PathA) and not IsFolder(PathB) and PathB not in ExcludeFolders:
            dirsA = os.listdir(PathA)
            for dir in dirsA:
                CompareFolderInternal(CreatePath(PathA, dir), CreatePath(PathB, dir), bCollectNVAddedFiles, CreatePath(OutputPath, dir))
            return

def CompareFolder(EnginePathA, EnginePathB, bCollectNVAddedFiles, OutputEnginePath):
    for folder in CompareFolders:
        folderPathA = CreatePath(EnginePathA, folder)
        folderPathB = CreatePath(EnginePathB, folder)
        folderOutput = CreatePath(OutputEnginePath, folder)
        folderList = os.listdir(folderPathA)
        for i in folderList:
            CompareFolderInternal(CreatePath(folderPathA, i), CreatePath(folderPathB, i), bCollectNVAddedFiles, CreatePath(folderOutput, i))

def CompareSVNWithGit():
    global nvModifiedFiles
    global currentOutFile
    global nvChangedFiles
    global currentChangedFiles
    currentOutFile = nvModifiedFiles
    currentChangedFiles = nvChangedFiles
    CompareFolder(GitPath, SVNPath, True, MergeEnginePath)

def CreateFilePath(nvFilePath, nvEnginePath, clientEnginePath):
    return clientEnginePath + nvFilePath.replace(nvEnginePath, "")

def Init():
    global ChangedFiles
    ChangedFiles = open(ChangedFilesName, 'w', encoding='utf-8')
    global nvModifiedFiles
    nvModifiedFiles = open(NVModifiedFilesPath, 'w', encoding='utf-8')
    global ExcludeFolders
    for i in range(len(ExcludeFolders)):
        ExcludeFolders[i] = CreatePath(SVNPath, ExcludeFolders[i])

def Finish():
    global nvModifiedFiles
    nvModifiedFiles.flush()
    nvModifiedFiles.close()

def MergeInternal(nvPath):
    nvFileData = {}
    clientFileData = {}
    with open(nvPath, 'r', encoding='utf-8') as nvFile:
        nvFileData = nvFile.readlines()

    mergeFilePath = CreateFilePath(nvPath, GitPath, MergeEnginePath)
    
    osPath = pathlib.Path(mergeFilePath).parent
    if not os.path.exists(osPath):
        os.makedirs(osPath)

    mergeFile = open(mergeFilePath, 'w+', encoding='utf-8')
    mergeFile.writelines(nvFileData)
    mergeFile.flush()
    mergeFile.close()

def Merge():
    exlusiveFilesData = []
    with open(MergeExclusiveFilesPath, 'r', encoding='utf-8') as exlusiveFiles:
        data = exlusiveFiles.readlines()
        for j in data:
            exlusiveFilesData.append(re.sub(r'[\ \n\t]', '', j))   
    
    for i in nvChangedFiles:
        if i.FileName in exlusiveFilesData:
            continue
        if IsFile(i.FilePath):
            MergeInternal(i.FilePath)

    for i in nvAddedFiles:
        if i.FileName in exlusiveFilesData:
            continue
        if IsFile(i.FileNVPath):
            MergeInternal(i.FileNVPath)

# def CopyGitToSVN():
#     for file in nvModifiedFiles:
#         filePath = file.FileClientPath
#         destPath = CreateFilePath(file.FileNVPath, GitPath, SVNPath)
#         print("Copy", filePath, "to", destPath)
#         os.system("copy " + filePath + " " + destPath)



def Main():
    Init()
    CompareSVNWithGit()
    Merge()
    Finish()
Main()