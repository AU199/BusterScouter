import statbotics
import requests
import pandas as pd

class ScoutingHelper:
    
    def __init__(self,TBAKey:str):
        self.stats = statbotics.Statbotics()
        self.BASEURL = "https://www.thebluealliance.com/api/v3"
        self.header = {
            "X-TBA-Auth-Key":TBAKey
        }
    def checkResponses(self):
        subURL = self.BASEURL + "/status"
        response = self.req(subURL,self.header).status_code
        
        if response != 200:
            Warning(f"Status Code {response} is not 200, check configs in order to debug issue")
        else:
            print(f"{response} all good")
    
    def getTeamsAtEvent(self,eventCode:str) -> pd.DataFrame:
        """Function Provides all team numbers as strings in the format 'frc#teamnumber#'

        Args:
            eventCode (str): The event code of the event you want to prompt ex.'2025cmptx'

        Returns:
            pd.Dataframe: returns a pandas dataframe of team number
        """
        subURL = self.BASEURL + f"/event/{eventCode}/teams/keys"    
        teamList = self.req(subURL,self.header).json()
        return pd.DataFrame(teamList)

    def getTeamEPAsAtEvent(self,eventCode:str, fields:list = ['all']) -> pd.DataFrame:
        teamList = self.getTeamsAtEvent(eventCode)[0]
        returnList = []
        
        for team in teamList:
            statistics = self.stats.get_team(int(team.removeprefix('frc')))
            teamField = []
            print(statistics)
            if fields != ['all']:
                teamField.append(statistics[field] for field in fields)
                returnList.append(tuple(zip(team,tuple(teamField))))
                continue
                
        
        
    def req(self,url,headers):
        return requests.get(url,headers)

if __name__ == "__main__":
    TBAAUTHKEY = open("baller.txt").readline().removesuffix("\n")

    scouter = ScoutingHelper(TBAAUTHKEY)

    print(scouter.getTeamEPAsAtEvent("2026ohmv"))