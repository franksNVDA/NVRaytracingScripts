import unreal
#import pathlib
def IsNaniteMesh(staticMesh):
    if not staticMesh:
        return False
    
    return staticMesh.get_nanite_setting_enable() and staticMesh.has_valid_nanite_data()

Folders = ["/Game/MegaScans/3D_Plants/",
           "/Game/Scene/3D/Nature/Foliage/Tree/Medium/"]

NaniteResult = "E:/RTScript/NaniteGoThroughResult.txt"

NaniteMeshes = []


class NaniteMesh(object):
    def __init__(self, staticMesh):
        self.FileName = staticMesh.get_fname()
        self.NaniteTrianglesNum = staticMesh.get_num_nanite_triangles()
        self.ProxyMeshTrianglesNum = staticMesh.get_num_triangles(0)
        self.ProxyPercentTriangles = staticMesh.get_nanite_setting_fallback_percent_triangles() * 100
        self.ProxyRelativeError = staticMesh.get_nanite_setting_fallback_relative_error()

def IsValidNaniteMesh(staticMesh):
    if staticMesh and isinstance(staticMesh, unreal.StaticMesh) and IsNaniteMesh(staticMesh) and staticMesh.is_support_ray_tracing():
        return True

def ProcessAssets(path):
    assetPaths = unreal.EditorAssetLibrary.list_assets(path)
    #print(assetPaths)
    for assetPath in assetPaths:
        assetPath = assetPath.split(".")[0]
        staticMesh = unreal.EditorAssetLibrary.load_asset(assetPath)
        if IsValidNaniteMesh(staticMesh):
            NaniteMeshes.append(NaniteMesh(staticMesh))

def PrintAssets():
    ChangedFiles = open(NaniteResult, 'w', encoding='utf-8')
    for mesh in NaniteMeshes:
        #print(mesh.FileName)
        #print("NaniteTrianglesNum: ", mesh.NaniteTrianglesNum)
        #print("ProxyMeshTrianglesNum: ", mesh.ProxyMeshTrianglesNum)
        #print("ProxyPercentTriangles: ", mesh.ProxyPercentTriangles)
        #print("ProxyRelativeError: ", mesh.ProxyRelativeError)
        ChangedFiles.writelines(str(mesh.FileName) + " " + str(mesh.NaniteTrianglesNum) + " " + str(mesh.ProxyMeshTrianglesNum) + " " + str(mesh.ProxyPercentTriangles) + " " + str(mesh.ProxyRelativeError) + "\n")
    ChangedFiles.flush()
    ChangedFiles.close()


def Main():
    for folder in Folders:
        ProcessAssets(folder)

    PrintAssets()

Main()

