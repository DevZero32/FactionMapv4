import requests
from PIL import Image, ImageDraw, ImageOps
from io import BytesIO
import os
from Imports import jsonhandler, classhandler, armyhandler
import imghdr
from functools import lru_cache
import numpy as np
import asyncio

imageLock = asyncio.Lock()

# === ALGROS ===

def calculateOffset(image, center):
    # Get the size of the image
    img_width, img_height = image.size

    # Calculate the offset to paste from the center
    offset = (center[0] - img_width // 2, center[1] - img_height // 2)

    return offset

def getCenterAndBoundingBoxSize(image):
    # Convert the image to a NumPy array
    imgArray = np.array(image)

    # Find the coordinates of black pixels using NumPy's boolean indexing
    blackPixelsCoords = np.argwhere(np.all(imgArray[:, :, :3] == [0, 0, 0], axis=-1) & (imgArray[:, :, 3] == 255))

    # Calculate the bounding box coordinates
    if blackPixelsCoords.size > 0:
        minY, minX = np.min(blackPixelsCoords, axis=0)
        maxY, maxX = np.max(blackPixelsCoords, axis=0)

        # Calculate the size of the bounding box
        boundingBoxSize = (maxX - minX + 1, maxY - minY + 1)

        # Calculate the center of the bounding box
        center = ((minX + maxX) // 2, (minY + maxY) // 2)

        return center, boundingBoxSize
    else:
        return None, None

def calContinousLand(regionId: int) -> list:
    """
    Returns all connected regions with the same owner starting from the given regionId.
    """

    # Get the region data
    regions = jsonhandler.getregionjson()
    
    # Initialize stack for DFS and a list to store connected lands
    connectedLands = []
    stack = [regionId]
    
    # To avoid visiting the same region multiple times
    visited = set()
    
    # Get the region class for the starting region
    start_region = classhandler.regionClass(regions=regions, regionId=regionId)
    owner = start_region.owner

    # DFS Loop
    while stack:
        current_region_id = stack.pop()
        
        # Skip if already visited
        if current_region_id in visited:
            continue
        
        # Mark as visited
        visited.add(current_region_id)
        # Add to connected lands (only once since we're checking 'visited')
        connectedLands.append(current_region_id)
        # Get the current region class
        current_region = classhandler.regionClass(regions=regions, regionId=current_region_id)
        
        # Explore neighbors
        for neighbor_id in current_region.neighbours:
            neighbor = classhandler.regionClass(regions=regions, regionId=neighbor_id)
            # If the neighbor has the same owner and hasn't been visited, add to the stack
            if neighbor.owner == owner and neighbor_id not in visited:
                stack.append(neighbor_id)
    return connectedLands

# === IMAGE ===

async def save_image(imageUrl, guildId):
  response = requests.get(imageUrl)
  imgData = response.content

  imageFormat = str(imghdr.what(None, h=imgData))
  supportedFormats = ["png", "jpg", "jpeg", "bmp"]

  if imageFormat in supportedFormats:
    image = Image.open(BytesIO(imgData))
    image = image.convert("RGBA")
    image.save(f'Data/Logos/{guildId}.png')
  else:
    raise Warning(f"{imageFormat} is not supported as a format type.")


# Map assembly
async def redraw() -> None:
  async with imageLock:
    # === Temp file removal ===
    try:
        os.remove("Data/Map/Temp/borderLayer.png")
    except: pass
    try:
        os.remove("Data/Map/Temp/MapBuildings.png")
    except: pass
    try:
        os.remove("Data/Map/Temp/mapOverview.png")
    except: pass
    mapBorders = Image.open("Data/Map/MapBorders.png").convert("RGBA")

    for faction in jsonhandler.getfactionsjson():
      compositePaste(mapBorders,faction["guild"]).save("Data/Map/Temp/borderLayer.png")


    addBuildings()
    assembleMap.cache_clear()


async def updateFactionBorders(factionId):
  async with imageLock:
    try:
      # Load the existing map with borders or create a new one if not found
      mapImage = Image.open("Data/Map/Temp/borderLayer.png").convert("RGBA")
    except:
      mapImage = Image.open("Data/Map/MapBorders.png").convert("RGBA")
    
    # Get faction data
    faction = classhandler.factionClass(factionId=factionId, factions=jsonhandler.getfactionsjson())
    factionRegions = faction.regions

    # Collect lands (connected regions) of the faction
    lands = []
    for region in factionRegions:
      if region not in [r for area in lands for r in area["area"]]:
        # Calculate the continuous area
        area = calContinousLand(regionId=region)
        lands.append({"area": area})
    
    # Now, only update the affected areas
    for land in lands:
      area = land["area"]

      # Create a mask for the area and clear the old one
      areaMask = Image.new("RGBA", mapImage.size, (255, 255, 255, 0))  # Transparent mask
      for regionId in area:
        # Open the mask image corresponding to the region and paste it into the area mask
        regionMask = Image.open(f"Data/Map/Temp/Masks/{regionId}.png").convert("RGBA")
        areaMask.paste(regionMask, (0, 0), regionMask)
      
      # Clear the old area from the map by setting its alpha to 0
      clearMask = Image.new("RGBA", areaMask.size, (255, 255, 255, 0))  # Fully transparent
      mapImage.paste(clearMask, (0, 0), areaMask)

      compositePaste(mapImage,faction.guild).save("Data/Map/Temp/borderLayer.png")

    # Save the updated border layer
    mapImage.save("Data/Map/Temp/borderLayer.png")
    addBuildings()

    assembleMap.cache_clear()
    assembleMap()

def compositePaste(baseImage,factionId):
  try: 
    baseImage = Image.open(baseImage).convert("RGBA")
  except: pass
  # === Faction class ===
  
  lands = []
  faction = classhandler.factionClass(factionId=factionId,factions=jsonhandler.getfactionsjson())
  factionRegions = faction.regions

  for region in factionRegions:
    if region not in [r for area in lands for r in area["area"]]:

      area = calContinousLand(regionId=region)
      lands.append({"area":area})

      if area not in [a["area"] for a in lands]:
        lands.append({"area": area})
      
      #applying
      areaMask = Image.new("RGBA",baseImage.size,(255,255,255,0))
      for i in area:
        i = Image.open(f"Data/Map/Temp/Masks/{i}.png").convert("RGBA")
        areaMask.paste(i,(0,0),i)
      
      centre,boundingBox = getCenterAndBoundingBoxSize(areaMask)
      if boundingBox == None or centre == None:
        return

      logoImage = Image.new("RGBA",baseImage.size,(0,0,0,0))
      logo = Image.open(f"Data/Logos/{factionId}.png").convert("RGBA").resize(boundingBox)
      logo.putalpha(230)

      logoImage.paste(logo,calculateOffset(logo,centre),logo)
      areaMask = Image.composite(logoImage,areaMask,areaMask)

      baseImage.paste(areaMask,(0,0),areaMask)
  return baseImage

def addBuilding(regionId):
  try:
     buildingImage = Image.open("Data/Map/Temp/MapBuildings.png").convert("RGBA")
  except FileNotFoundError: 
    width, height = Image.open("Data/Map/MapOverview.png").convert("RGBA").size
    buildingImage = Image.new(mode="RGBA",size=(width,height))

  factions = jsonhandler.getfactionsjson()
  region = classhandler.regionClass(jsonhandler.getregionjson(),regionId)
  
  if region.building != "None":
    regionBuilding = Image.open(f"Data/Map/Buildings/{(region.building).lower()}.png").convert("RGBA")
    width,height = region.centre
    width -= 12
    height -= 12 
    buildingImage.paste(regionBuilding,(width,height))
    assembleMap.cache_clear()
    buildingImage.save("Data/Map/Temp/MapBuildings.png")

def addBuildings():
  width, height = Image.open("Data/Map/MapOverview.png").convert("RGBA").size

  buildingImage = Image.new(mode="RGBA",size=(width,height))
  regions = jsonhandler.getregionjson()
  for region in regions:
    region = classhandler.regionClass(regions,region["regionId"])

    if region.building != "None":
      regionBuilding = Image.open(f"Data/Map/Buildings/{(region.building).lower()}.png").convert("RGBA")
      width,height = region.centre
      width -= 12
      height -= 12 
      buildingImage.paste(regionBuilding,(width,height))

  buildingImage.save("Data/Map/Temp/MapBuildings.png") 
  return buildingImage

def addDeployments():
  regions = jsonhandler.getregionjson()
  factions = jsonhandler.getfactionsjson()
  # === Get all regions with a deployment
  deploymentRegions = []
  for faction in factions:
    for deployment in faction["deployments"]:
      if deployment["region"] != deploymentRegions:
        deploymentRegions.append(deployment["region"])
  # === Get Image ===
  try:
    deploymentImage = Image.open("Data/Map/Temp/DeploymentsLayer.png").convert("RGBA")
  except FileNotFoundError: 
    width, height = Image.open("Data/Map/MapOverview.png").convert("RGBA").size
    deploymentImage = Image.new(mode="RGBA",size=(width,height))
    
  # === Pasting images if no building ===

  manpowerIcon = Image.open("Data/Map/Buildings/manpower.png").convert("RGBA")

  for region in deploymentRegions:
    region = classhandler.regionClass(regions,region)
    if region.building == "None":
      width,height = region.centre
      width -= 12
      height -= 12
      deploymentImage.paste(manpowerIcon,(width,height))
  return deploymentImage

@lru_cache(maxsize=None)
async def assembleMap():
  # === Default ====
  def Default():
    try:
      borderImage = Image.open("Data/Map/Temp/borderLayer.png").convert("RGBA")
    except FileNotFoundError:
      borderImage = Image.open("Data/Map/MapBorders.png").convert("RGBA")
    try:
      buildingImage = Image.open("Data/Map/Temp/MapBuildings.png").convert("RGBA")
    except FileNotFoundError: 
      buildingImage = addBuildings()
    deploymentImage = addDeployments()
    titlesImage = Image.open("Data/Map/mapTitles.png").convert("RGBA")
    overviewImage = Image.open("Data/Map/MapOverview.png").convert("RGBA")    
      
    
    deploymentImage.paste(titlesImage,(0,0 ), titlesImage)
    buildingImage.paste(deploymentImage,(0,0 ), deploymentImage)
    borderImage.paste(buildingImage, (0, 0), buildingImage)
    overviewImage.paste(borderImage, (0, 0), borderImage)
    overviewImage.save("Data/Map/Temp/mapOverview.png")
  # === Political ===
  def Political():
    try:
      borderImage = Image.open("Data/Map/Temp/borderLayer.png").convert("RGBA")
    except FileNotFoundError:
      borderImage = Image.open("Data/Map/MapBorders.png").convert("RGBA")
    titlesImage = Image.open("Data/Map/mapTitles.png").convert("RGBA")
    overviewImage = Image.open("Data/Map/MapOverview.png").convert("RGBA")  
      
    borderImage.paste(titlesImage,(0,0),titlesImage)
    overviewImage.paste(borderImage,(0,0),borderImage)
    overviewImage.save("Data/Map/Temp/politicalOverview.png")
  # === Topograhy ===
  def Topograhy():
    borderImage = Image.open("Data/Map/MapBorders.png").convert("RGBA")
    titlesImage = Image.open("Data/Map/mapTitles.png").convert("RGBA")
    biomeImage = Image.open("Data/Map/BiomesMap.png").convert("RGBA")
      
    borderImage.paste(titlesImage,(0,0),titlesImage)
    biomeImage.paste(borderImage,(0,0),borderImage)
    biomeImage.save("Data/Map/Temp/topographyOverview.png")
  async with imageLock:
    Default()
    Political()
    Topograhy()
def generateMasks():
  
  def findCordinatesWithinBorder(image, regionCentre):
    """
      Flood fill from the region centre with red color and return a list of coordinates
      that have been filled with the same red color.

      Args:
        image (Image): The image on which to perform the flood fill.
        regionCentre (tuple): The center coordinates of the region.

      Returns:
        list: A list of coordinates that have been filled with red color.
      """
    radius = 250
    width, height = image.size

    # Define the bounding box around regionCentre
    min_x = max(0, regionCentre[0] - radius)
    min_y = max(0, regionCentre[1] - radius)
    max_x = min(width - 1, regionCentre[0] + radius)
    max_y = min(height - 1, regionCentre[1] + radius)

    # Perform flood fill with red color
    filled_image = image.copy()
    ImageDraw.floodfill(filled_image, regionCentre, (255, 0, 0, 255), thresh=0)

    # Find all coordinates with the same red color
    red_coordinates = []
    for y in range(min_y, max_y + 1):
      for x in range(min_x, max_x + 1):
        if filled_image.getpixel((x, y)) == (255, 0, 0, 255):
          red_coordinates.append((x, y))

    return red_coordinates

  regions = jsonhandler.getregionjson()
  for region in regions:
    if region["Biome"] == "Ocean": continue
    region = classhandler.regionClass(regions,region["regionId"])
    
    borderImage = Image.open("Data/Map/mapBorders.png").convert("RGBA")
    width, height = borderImage.size
    regionCordinates = findCordinatesWithinBorder(borderImage,region.centre)

    maskImage = Image.new("RGBA",(width,height),(255,255,255,0))
    for cordinate in regionCordinates:
      maskImage.putpixel(cordinate,(0,0,0))
    maskImage.save(f"Data/Map/Temp/Masks/{region.id}.png")