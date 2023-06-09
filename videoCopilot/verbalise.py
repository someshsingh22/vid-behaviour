from typing import List, Any, Tuple
import random
import pandas as pd

class AdMemUserVerbalisation:
    def __init__(self, user_id, study_id,path) -> None:
        self.user_id=user_id
        self.path= path
        self.study_id=study_id
        self.df= pd.read_csv(self.path+f"users_study{study_id}.csv")
        self.row= self.df.loc[self.df['user_id'] == self.user_id]
        
    def verb_persona(self) -> str:
        '''
        pass locale, age, and gender.
        '''
        age= '20'
        gender= self.row['Gender'].values[0]
        locale='India'
        return f"{age} year old {gender} from {locale}"
    
    def verb_seen_advertisements(self, watched: bool, n: int) -> str:
        '''
        watched = True/False means the viewer selected/unselected the brand, n is the max number of brands to return.
        '''
        if watched:
            out= self.row['brands_seen'].values[0]
        else:
            out= set(self.row['brands_seen_options'].values[0])-set(self.row['brands_seen'].values[0])
            out= random.sample(out, n)
        return f"{out}"
    
    def verb_used_products(self, used: bool, n: int) -> str:
        '''
        watched = True/False means the viewer selected/unselected the brand, n is the max number of brands to return.
        '''
        if used:
            out= self.row['brands_used'].values[0]
        else:
            out= set(self.row['brands_used_options'].values[0])-set(self.row['brands_used'].values[0])
            out= random.sample(out, n)
        return f"{out}"
    
    def verb_ad_blocker_yt_sub(self) -> str:
        '''
        The viewer uses an ad blocker and YouTube Premium subscription OR
        The viewer uses an ad blocker but is'nt a YouTube Premium subscriber OR
        The viewer doesn't use an ad blocker but is a YouTube Premium subscriber OR
        The viewer doesn't use an ad blocker and isn't a YouTube Premium subscriber
        '''
        adblocker= 'uses an' if self.row['ad_block'].values[0] else 'doesn\'t use an'
        youtube_sub= 'is' if self.row['yt_sub'].values[0] else 'isn\'t'
        return f"The viewer {adblocker} ad blocker and {youtube_sub} a YouTube Premium subscriber"
    
    def verb_time_on_yt_mobile_web(self) -> str:
        '''
        The viewer spends most of their time on YouTube on mobile OR
        The viewer spends most of their time on YouTube on web OR
        The viewer spends more time on web than mobile on YouTube OR
        The viewer spends more time on mobile than web on YouTube
        '''
        youtube_mobile= self.row['yt_mobile'].values[0] 
        return f"The viewer spends {youtube_mobile} on YouTube"
    
    def verb_primary_info_source(self, apprise:bool, n:int) -> str:
        '''
        apprise = True/False means the viewer selected/unselected the method, n is the max number of methods to return.
        '''
        apprise= self.row['apprise'].values[0]
        return f"{apprise}"
        
    def verbalise(self) -> List[Tuple[str, float]]:
        return [
            (f"The viewer is a {self.verb_persona()}.", 1),
            (f"They have seen advertisements for {self.verb_seen_advertisements(watched=True, n=5)} but not {self.verb_seen_advertisements(watched=False, n=5)}.", 1),
            (f"They remember using products like {self.verb_used_products(used=True, n=5)} but not {self.verb_used_products(used=False, n=5)}.", 1),
            (f"The viewer {self.verb_ad_blocker_yt_sub()}.", 1),
            (f"They spend {self.verb_time_on_yt_mobile_web()}.", 1),
            (f"They primarily apprise themselves of the latest products and brands through {self.verb_primary_info_source()}", 1),
        ]
    
    def __call__(self) -> str:
        entries = self.verbalise()
        return " ".join([entry[0] for entry in entries if random.random() < entry[1]])
        
    
    
class AdMemVideoVerbalisation:
    def __init__(self, video_id) -> None:
        pass
    
    def verbalise(self) -> List[Tuple[str, float]]:
        return [
            (f"They watch a {self.video_length} second advertisement for {self.brand}.", 1),
            (f"The video is shot in {self.get_orientation()}.", 1),
            
            
        ]

    def __call__(self) -> List[str]:
        return ""
    
class AdSceneVerbalisation:
    def __init__(self, video_id, scene_id) -> None:
        pass
    
    def __call__(self) -> List[str]:
        return ""
    
class AdMemResponseVerbalisation:
    def __init__(self, user_id, study_id, video_id) -> None:
        pass
    
    def __call__(self) -> List[str]:
        return ""