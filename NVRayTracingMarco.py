import pandas as pd
import re
import os
import pathlib
NVEnginePath = "D:/UE4/Engine"
VanillaEnginePath = "D:/UEVanilla/Engine"
ClientEnginePath = "D:/LSA/Dev-Main/Engine"
MergeEnginePath = "D:/LSA_NVMerge/Engine"

CompareFolders = ["Source/Runtime/Renderer",
                  "Source/Runtime/RenderCore",
                  "Source/Runtime/Engine",
                  "Source/Runtime/D3D12RHI"
                  ]

FileSuffixs = [".h", ".cpp"]

# stream output vars 
ClientModifiedFilesPath = "ClientModifiedFiles.txt"
NVModifiedFilesPath = "NVModifiedFiles.txt"
BothModifiedFilesPath = "BothModifedFiles.txt"
MergeExclusiveFilesPath = "MergeExclusiveFiles.txt"

clientModifiedFiles = {}
nvModifiedFiles = {}
bothModifiedFiles = {}
currentOutFile = {}

# vars
nvChangedFiles = []
clientChangedFiles = []
currentChangedFiles = []

nvChangedOnlyFiles = []
bothChangedFiles = []

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
        print(fileA, "is not equal to", fileB)
    
def CompareFolderInternal(PathA, PathB):
    if IsFile(PathA) and IsFile(PathB):
        DiffFile(PathA, PathB)
        return
    if IsFolder(PathA) and IsFolder(PathB):
        dirsA = os.listdir(PathA)
        dirsB = os.listdir(PathB)
        for dir in dirsA:
            CompareFolderInternal(CreatePath(PathA, dir), CreatePath(PathB, dir))
        return

def CompareFolder(EnginePathA, EnginePathB):
    for folder in CompareFolders:
        folderPathA = CreatePath(EnginePathA, folder)
        folderPathB = CreatePath(EnginePathB, folder)
        folderList = os.listdir(folderPathA)
        for i in folderList:
            CompareFolderInternal(CreatePath(folderPathA, i), CreatePath(folderPathB, i))

def CompareClientWithVanilla():
    global clientModifiedFiles
    global currentOutFile
    global clientChangedFiles
    global currentChangedFiles
    currentOutFile = clientModifiedFiles
    currentChangedFiles = clientChangedFiles
    CompareFolder(ClientEnginePath, VanillaEnginePath)

def CompareNVWithVanilla():
    global nvModifiedFiles
    global currentOutFile
    global nvChangedFiles
    global currentChangedFiles
    currentOutFile = nvModifiedFiles
    currentChangedFiles = nvChangedFiles
    CompareFolder(NVEnginePath, VanillaEnginePath)

def CreateFilePath(nvFilePath, nvEnginePath, clientEnginePath):
    return clientEnginePath + nvFilePath.replace(nvEnginePath, "")

def FilterChangedFiles():
    for i in nvChangedFiles:
        bFound = False
        for j in clientChangedFiles:
            if i.FileName == j.FileName:
               bothChangedFiles.append(FilePath(i.FileName, i.FilePath, j.FilePath))
               bothModifiedFiles.write(i.FileName + "\n")
               bFound = True
               break
        if bFound == False:
            nvChangedOnlyFiles.append(FilePath(i.FileName, i.FilePath, CreateFilePath(i.FilePath, NVEnginePath, ClientEnginePath)))

def Init():
    global clientModifiedFiles
    clientModifiedFiles = open(ClientModifiedFilesPath, 'w', encoding='utf-8')
    global nvModifiedFiles
    nvModifiedFiles = open(NVModifiedFilesPath, 'w', encoding='utf-8')
    global bothModifiedFiles
    bothModifiedFiles = open(BothModifiedFilesPath, 'w', encoding='utf-8')

def Finish():
    global clientModifiedFiles
    clientModifiedFiles.flush()
    clientModifiedFiles.close()
    global nvModifiedFiles
    nvModifiedFiles.flush()
    nvModifiedFiles.close()
    global bothModifiedFiles
    bothModifiedFiles.flush()
    bothModifiedFiles.close()

def MergeInternal(nvPath, clientPath, isBothChanged):
    nvFileData = {}
    clientFileData = {}
    with open(nvPath, 'r', encoding='utf-8') as nvFile:
        nvFileData = nvFile.readlines()

    with open(clientPath, 'r', encoding='utf-8') as clientPath:
        clientFileData = clientPath.readlines()

    NVBothChangeComments = ["// [NV_CLIENT_BOTH_CHANGED] This file is changed both by NV and Client, should be resolved carefully!!!\n"]
    NVMarcoBegin = ["#ifndef NV_RAYTRACING\n",
                    "#define NV_RAYTRACING 0\n",
                    "#endif\n",
                    "#if NV_RAYTRACING\n"]
    NVMarcoMiddle = ["#else //#if NV_RAYTRACING\n"]
    NVMarcoEnd = ["#endif //#if NV_RAYTRACING\n"]

    mergeFilePath = CreateFilePath(nvPath, NVEnginePath, MergeEnginePath)
    
    osPath = pathlib.Path(mergeFilePath).parent
    if not os.path.exists(osPath):
        os.makedirs(osPath)

    mergeFile = open(mergeFilePath, 'w+', encoding='utf-8')
    if isBothChanged:
        mergeFile.writelines(NVBothChangeComments)
    mergeFile.writelines(NVMarcoBegin)
    mergeFile.writelines(nvFileData)
    mergeFile.writelines(NVMarcoMiddle)
    mergeFile.writelines(clientFileData)
    mergeFile.writelines(NVMarcoEnd)
    mergeFile.flush()
    mergeFile.close()


def Merge():
    exlusiveFilesData = []
    with open(MergeExclusiveFilesPath, 'r', encoding='utf-8') as exlusiveFiles:
        data = exlusiveFiles.readlines()
        for j in data:
            exlusiveFilesData.append(re.sub(r'[\ \n\t]', '', j))   
    
    for i in nvChangedOnlyFiles:
        if i.FileName in exlusiveFilesData:
            continue
        if IsFile(i.FileNVPath) and IsFile(i.FileClientPath):
            MergeInternal(i.FileNVPath, i.FileClientPath, False)
    
    for i in bothChangedFiles:
        if i.FileName in exlusiveFilesData:
            continue
        if IsFile(i.FileNVPath) and IsFile(i.FileClientPath):
            MergeInternal(i.FileNVPath, i.FileClientPath, True)

def Main():
    Init()
    CompareClientWithVanilla()
    CompareNVWithVanilla()
    FilterChangedFiles()
    Merge()
    Finish()
Main()