from Imports import jsonhandler,turnshandler
import numpy as np

class factionClass():
  def __init__(self, factionId, factions):
    class turns:
      def __init__(self,factionId):
        turns = turnshandler.getTurns()
        for turn in turns["turns"]:
          if turn["id"] == factionId:
              self.raw = turn
              self.deployments = turn["deployments"]
              self.regions = turn["regions"]
              break
    
    class resources:
        def __init__(self, resources):
            gold = resources["gold"]
            iron = resources["iron"]
            stone = resources["stone"]
            wood = resources["wood"]
            manpower = resources["manpower"]

            self.gold = gold
            self.iron = iron
            self.stone = stone
            self.wood = wood
            self.manpower = manpower
            self.raw = faction["resources"]

    class permissions:
        def __init__(self, roles):
            self.raw = faction["permissions"]
            for role_data in roles:
                role_id = role_data["roleId"]
                role_permissions = role_data["rolePermissions"]
                setattr(self, f"role_{role_id}", self.RoleIdClass(role_permissions, roles))

        class RoleIdClass:
            def __init__(self, role_permissions, roles):
                self.army = role_permissions["army"]
                self.region = role_permissions["region"]
                self.faction = role_permissions["faction"]
                self.trade = role_permissions["trade"]
                self.roles = roles

            def __getattr__(self, attr):
                if attr.startswith("role_"):
                    role_id_str = attr.split("_")[1]
                    try:
                        role_id = int(role_id_str)
                        role_data = next((role for role in self.roles if role["roleId"] == role_id), None)
                        if role_data:
                            return self.__class__(role_data["rolePermissions"], self.roles)
                        else:
                            raise AttributeError(f"Role with ID {role_id} not found")
                    except ValueError:
                         # Handle the case where the role ID is not a valid integer
                        raise AttributeError("Invalid role ID")
        
    class deployments:
      def __init__(self, deployments):
          self.raw = faction["deployments"]
          self.armies = self.Armies(deployments)
  
      class ArmyIdClass:
        def __init__(self, army_data):
          self.raw = army_data
          self.id = army_data["id"]
          self.name = army_data["name"]
          self.region = army_data["region"]
          self.tierOne = army_data["tierOne"]
          self.tierTwo = army_data["tierTwo"]
          self.faction = faction["name"]
  
      class Armies:
          def __init__(self, armies):
              """
              To access army data, use the dynamic attribute 'army_<id>'
              where <id> is the army's unique identifier.
              """
              self.raw = faction["deployments"]
              for army_data in armies:
                  army_id = army_data["id"]
                  setattr(self, f"army_{army_id}", self.ArmyIdClass(army_data))
  
          def __getattr__(self, attr):
              """
              To access an army by ID, use the attribute 'deployment_<id>'.
              """
              if attr.startswith("deployment_"):
                  army_id_str = attr.split("_")[1]
                  try:
                      army_id = int(army_id_str)
                      return getattr(self, f"army_{army_id}")
                  except ValueError:
                      raise AttributeError("Invalid army ID")
  
          class ArmyIdClass:
            def __init__(self, army_data):
              """
              To access this army's attributes, directly use the attributes
              'id', 'name', 'region', 'teirOne', 'teirTwo', and 'faction'.
              """
              self.raw = army_data
              self.id = army_data["id"]
              self.name = army_data["name"]
              self.region = army_data["region"]
              self.tierOne = army_data["tierOne"]
              self.tierTwo = army_data["tierTwo"]
              self.faction = faction["name"]
    
    def factionRegions(id):
      regions = jsonhandler.getregionjson()

      factionsRegions = []
      for region in regions:
        if region["regionOwner"] == id: factionsRegions.append(region["regionId"])
      return factionsRegions
    faction = None

    for indexFaction in factions:
        if indexFaction["guild"] == factionId:
          faction = indexFaction
    
    if type(faction) == type(None):
       raise ValueError("faction was not found in classhandler.factionclass ident")
            
    self.permissions = permissions(faction["permissions"])
    self.resources = resources(faction["resources"])
    self.deployments = deployments(faction["deployments"])
    self.name = faction["name"]
    self.guild = faction["guild"]
    self.capital = faction["capital"]
    self.regions = factionRegions(faction["guild"])
    self.turns = turns(faction["name"])
    self.alert = faction["alert"]

class regionClass():
  def __init__(self,regions,regionId):
    for indexRegion in regions:
      if indexRegion["regionId"] == regionId:
        region = indexRegion
        break
      
    self.id = region["regionId"]
    self.centre = region["regionCentre"]
    self.owner = region["regionOwner"]
    self.water = region["isWaterRegion"]
    self.land = region["isLandRegion"]
    try:
      self.armies = region["armies"]
      print("Warning: 'region[\"armies\"]' has been deprecated for 'faction[\"deployments\"]'. It is no longer stored in regions.json.")
    except KeyError: pass
    self.neighbours = region["neighbours"]
    self.building = region["building"]
    self.biome = region["Biome"]
    self.resources = region["Resource"]
    