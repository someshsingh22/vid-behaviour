import json
import random
from pathlib import Path
from typing import Any, List, Tuple
import ast

import pandas as pd

FEATURES_ROOT = Path("/home/someshs/vid-behaviour/data/study/")
SCENES_URL = "https://hemingwaydata.blob.core.windows.net/scenes/"

USER_TABLE_STUDY1 = pd.read_csv(FEATURES_ROOT / "user_data_study1.csv")
USER_TABLE_STUDY2 = pd.read_csv(FEATURES_ROOT / "user_data_study2.csv")

VIDEO_FEATS_TABLE = pd.read_csv(FEATURES_ROOT / "video_feats.csv")
COLOR_FEATS = json.load(open(FEATURES_ROOT / "color_feats.json"))
IMAGE_FEATS = json.load(open(FEATURES_ROOT / "image_feats.json"))
BLIP_CAPTION = pd.read_csv(FEATURES_ROOT / "blip_output.csv")
OCR = pd.read_csv(FEATURES_ROOT / "ocr.csv")
NUM_SCENES = pd.read_csv(FEATURES_ROOT / "num_scenes.csv")
SCENE_DURATION= pd.read_csv(FEATURES_ROOT / "scene_duration.csv")
SEP = "\n"

class AdMemUserVerbalisation:
    def __init__(self, user_id, study_id) -> None:
        self.user_id = user_id
        self.study_id = study_id

        if study_id == 1:
            self.df = USER_TABLE_STUDY1
        else:
            self.df = USER_TABLE_STUDY2

        self.row = self.df.loc[self.df["user_id"] == self.user_id]

    def verb_persona(self) -> str:
        """
        pass locale, age, and gender.
        HARD CODED FOR NOW
        {
            'locale': 'India',
            'age': '20',
        }
        gender: given in the user table
        """
        age = "20"
        gender = self.row["Gender"].values[0]
        locale = "India"
        return f"{age} year old {gender} from {locale}"

    def verb_seen_advertisements(self, watched: bool, n: int) -> str:
        """
        watched = True/False means the viewer selected/unselected the brand, n is the max number of brands to return.
        """
        if watched:
            out = self.row["brands_seen"].values[0]
            out = ast.literal_eval(out)
            out = ", ".join([entry for entry in out])

        else:
            seen = ast.literal_eval(self.row["brands_seen"].values[0])
            seen_options = ast.literal_eval(self.row["brands_seen_options"].values[0])
            out = set(seen_options) - set(seen)
            if len(out) > n:
                out = random.sample(out, n)
            out = ", ".join([entry for entry in out])
        return f"{out}"

    def verb_used_products(self, used: bool, n: int) -> str:
        """
        watched = True/False means the viewer selected/unselected the brand, n is the max number of brands to return.
        """
        if used:
            out = self.row["brands_used"].values[0]
            out = ast.literal_eval(out)
            out = ", ".join([entry for entry in out])

        else:
            used = ast.literal_eval(self.row["brands_used"].values[0])
            used_options = ast.literal_eval(self.row["brands_used_options"].values[0])
            out = set(used_options) - set(used)
            if len(out) > n:
                out = random.sample(out, n)

            out = ", ".join([entry for entry in out])
        return f"{out}"

    def verb_ad_blocker_yt_sub(self) -> str:
        """
        The viewer uses an ad blocker and YouTube Premium subscription OR
        The viewer uses an ad blocker but is'nt a YouTube Premium subscriber OR
        The viewer doesn't use an ad blocker but is a YouTube Premium subscriber OR
        The viewer doesn't use an ad blocker and isn't a YouTube Premium subscriber
        """
        adblocker = "uses an" if self.row["ad_block"].values[0] else "doesn't use an"
        youtube_sub = "is" if self.row["youtube_sub"].values[0] else "isn't"
        return f"The viewer {adblocker} ad blocker and {youtube_sub} a YouTube Premium subscriber"

    def verb_time_on_yt_mobile_web(self) -> str:
        """
        The viewer spends most of their time on YouTube on mobile OR
        The viewer spends most of their time on YouTube on web OR
        The viewer spends more time on web than mobile on YouTube OR
        The viewer spends more time on mobile than web on YouTube
        """
        youtube_mobile = self.row["youtube_mobile"].values[0]
        return f"The time spent by the viewer on Youtube is  {youtube_mobile}"

    def verb_primary_info_source(self, apprise: bool, n: int) -> str:
        """
        apprise = True/False means the viewer selected/unselected the method, n is the max number of methods to return.
        """
        apprise = self.row["apprise"].values[0]

        apprise = apprise.split(",")
        apprise = random.sample(apprise, n)
        apprise = ", ".join([entry for entry in apprise])
        return f"{apprise}"

    def verbalise(self) -> List[Tuple[str, float]]:
        return [
            (f"The viewer is a {self.verb_persona()}.", 1),
            (
                f"They have seen advertisements for {self.verb_seen_advertisements(watched=True,n=5)} but not from {self.verb_seen_advertisements(watched=False, n=5)}.",
                1,
            ),
            (
                f"They remember using products like {self.verb_used_products(used=True, n=5)} but not from {self.verb_used_products(used=False, n=5)}.",
                1,
            ),
            (f"{self.verb_ad_blocker_yt_sub()}.", 1),
            (f"{self.verb_time_on_yt_mobile_web()}.", 1),
            (
                f"They apprise themselves of the latest products and brands through {self.verb_primary_info_source(True,5)}",
                1,
            ),
        ]

    def __call__(self) -> str:
        entries = self.verbalise()
        return SEP.join([entry[0] for entry in entries if random.random() < entry[1]])


class AdMemVideoVerbalisation:
    def __init__(self, video_id) -> None:
        self.video_id = video_id
        self.df = VIDEO_FEATS_TABLE
        self.row = self.df.loc[self.df["video_id"] == self.video_id]
        self.video_length = int(self.row["length"].values[0])
        self.brand = self.row["brand"].values[0]
        self.title = '\"' + self.row["title"].values[0] + '\"'
        self.description = '\"' + self.row["desc"].values[0] + '\"'
        self.image_feats = IMAGE_FEATS
        self.velocity = self.row["velocity"].values[0]
        self.scenes_df = NUM_SCENES
        self.num_scenes = self.scenes_df.loc[
            self.scenes_df["Video id"] == self.video_id
        ]["num_scenes"].values[0]

    def get_orientation(self) -> str:
        """
        Returns the orientation of the video.
        """
        self.image_name = str(self.video_id) + "-" + "001" + ".jpg"
        self.url = SCENES_URL + self.image_name
        json_data = self.image_feats[self.url]["Visual Tags"]
        for item in json_data:
            if item["category"] == "orientation":
                orient_tag = item["tag"]
                break
        return orient_tag

    def num_people(self) -> Tuple[int, str]:
        """
        Returns the number of unique faces in the video and the celebrities in the video if any else blank.
        """
        return "", ""

    def verbalise(self) -> List[Tuple[str, float]]:
        video_pre = [
            (
                f"They watch a {self.video_length} second advertisement for {self.brand}.",
                1,
            ),
            (f"The title of the advertisement is {self.title}.", 1),
            (f"The description of the advertisement is {self.description}.", 1),
            (
                f"The ad is shot in {self.get_orientation()} orientation, at a {self.velocity} pace",
                1,
            ),
            (f"Following are the description of each scene", 1),
            (
                f"There are {self.num_people()[0]} unique faces in the advertisement {self.num_people()[1]}.",
                1,
            ),
        ]
        scenes = [
            AdSceneVerbalisation(str(self.video_id), str(scene_id))()
            for scene_id in range(1, self.num_scenes + 1)
        ]
        for scene in scenes:
            video_pre.append((scene, 1))
        return video_pre

    def __call__(self) -> List[str]:
        return SEP.join(
            [entry[0] for entry in self.verbalise() if random.random() < entry[1]]
        )


class AdSceneVerbalisation:
    """
    color_feats format
    {'Color Tags': {'background': {'colors': {'Off_White': {'coverage': 0.4926, 'rgb': {'blue': 222, 'green': 219, 'red': 221}}, 'Silver': {'coverage': 0.1803, 'rgb': {'blue': 211, 'green': 207, 'red': 210}}, 'White': {'coverage': 0.327, 'rgb': {'blue': 243, 'green': 241, 'red': 243}}}, 'tones': {'cool': 0, 'neutral': 1.0, 'warm': 0}}, 'foreground': {'colors': {'Black': {'coverage': 0.2535, 'rgb': {'blue': 40, 'green': 35, 'red': 38}}, 'Dark_Gray': {'coverage': 0.1868, 'rgb': {'blue': 70, 'green': 63, 'red': 66}}, 'Gray': {'coverage': 0.2196, 'rgb': {'blue': 156, 'green': 144, 'red': 150}}, 'Off_White': {'coverage': 0.0633, 'rgb': {'blue': 228, 'green': 225, 'red': 227}}, 'White': {'coverage': 0.2768, 'rgb': {'blue': 253, 'green': 252, 'red': 253}}}, 'tones': {'cool': 0, 'neutral': 1.0, 'warm': 0}}, 'overall': {'colors': {'Black': {'coverage': 0.0731, 'rgb': {'blue': 39, 'green': 35, 'red': 37}}, 'Gray': {'coverage': 0.0699, 'rgb': {'blue': 157, 'green': 145, 'red': 151}}, 'Off_White': {'coverage': 0.3903, 'rgb': {'blue': 222, 'green': 219, 'red': 221}}, 'Silver': {'coverage': 0.1414, 'rgb': {'blue': 211, 'green': 207, 'red': 210}}, 'White': {'coverage': 0.3253, 'rgb': {'blue': 245, 'green': 244, 'red': 245}}}, 'tones': {'cool': 0, 'neutral': 1.0, 'warm': 0}}}}
    image_feats format
    {'Natural Image Aesthetics': {'Overall Aesthetics': 'Low', 'Balancing Elements': 'Low', 'Color Harmony': 'High', 'Interesting Content': 'Low', 'Shallow Depth of Field': 'Low', 'Good Lighting': 'Low', 'Object Emphasis': 'High', 'Repetition': 'Low', 'Rule Of Thirds': 'Low', 'Symmetry': 'Low', 'Vivid Color': 'Low'}, 'Face Features': {'Face Count': 0, 'Face Features': [], 'Facing': 'No Faces', 'Eyes': 'Unknown'}, 'Clutter': 'Low', 'Human Parts': {'Head': 'invisible', 'Torso': 'invisible', 'Upper Arms': 'invisible', 'Lower Arms': 'invisible', 'Upper Legs': 'invisible', 'Lower Legs': 'invisible'}, 'Visual Tags': [{'category': 'orientation', 'confidence': 1.0, 'tag': 'landscape'}, {'category': 'people', 'confidence': 0.997, 'tag': 'woman'}, {'category': 'none', 'confidence': 0.983, 'tag': 'rinse'}, {'category': 'photography style', 'confidence': 0.88, 'tag': 'product photography'}, {'category': 'none', 'confidence': 0.821, 'tag': 'brushing'}, {'category': 'none', 'confidence': 0.789, 'tag': 'hygiene'}, {'category': 'none', 'confidence': 0.781, 'tag': 'shower'}, {'category': 'none', 'confidence': 0.78, 'tag': 'title'}, {'category': 'none', 'confidence': 0.772, 'tag': 'moisture'}, {'category': 'scene', 'confidence': 0.763, 'tag': 'rainwater'}, {'category': 'none', 'confidence': 0.751, 'tag': 'leak'}, {'category': 'none', 'confidence': 0.748, 'tag': 'filler'}, {'category': 'none', 'confidence': 0.74, 'tag': 'fringe'}, {'category': 'none', 'confidence': 0.739, 'tag': 'cleanliness'}, {'category': 'scene', 'confidence': 0.733, 'tag': 'ripple'}]}
    ocr_csv format
    image path,text
    scenes/2473-018.jpg,"['Could reduce emissions by', 'Compared to conventional fuels']"
    """

    def __init__(self, video_id, scene_id) -> None:
        self.video_id = video_id
        self.scene_id = scene_id.zfill(3)

        self.image_feats = IMAGE_FEATS
        self.color_feats = COLOR_FEATS
        self.blip_caption = BLIP_CAPTION
        self.ocr = OCR
        self.image_name = self.video_id + "-" + self.scene_id + ".jpg"
        self.url = SCENES_URL + self.image_name

    def get_blip_caption(self):
        caption = self.blip_caption[self.blip_caption["image"] == self.image_name][
            "caption"
        ].values[0]
        caption = caption.split(",")[0]
        caption = caption.strip("'['")
        return caption
    def get_start_time(self):
        return ""
    def get_end_time(self):
        return ""
    

    def get_photography_style(self):
        json_data = self.image_feats[self.url]["Visual Tags"]
        photography_style = ""
        for item in json_data:
            if item["category"] == "photography style":
                photography_style = item["tag"]
                break

        return photography_style.split(' ')[0]

    def get_clutter(self):
        clutter = self.image_feats[self.url]["Clutter"]
        if clutter == "Low" or clutter == "High":
            return f"The scene has {clutter} visual complexity."
        else :
            return ""
        
    def get_body_parts(self):
        x = self.image_feats[self.url]["Human Parts"]
        body_parts = []
        for i in x.keys():
            if x[i] == "visible":
                body_parts.append(i)
        body_parts = ",".join(body_parts)
        return body_parts

    def get_num_faces(self):
        self.num_faces = self.image_feats[self.url]["Face Features"]["Face Count"]
        if self.num_faces == 0:
            return "There are no prominent faces in the scene."
        elif self.num_faces == 1:
            return "There is one prominent face in the scene."
        else:
            return f"There are {self.num_faces} faces in the scene."

    def get_colors(self, max_colors=5, min_coverage=0.9):
        """
        Keep adding colors till the coverage is >= min_coverage or the number of colors is >= max_colors
        """
        background, foreground = (
            self.color_feats[self.url]["Color Tags"]["background"]["colors"],
            self.color_feats[self.url]["Color Tags"]["foreground"]["colors"],
        )
        # sort colors by coverage
        background = sorted(
            background.items(), key=lambda x: x[1]["coverage"], reverse=True
        )
        foreground = sorted(
            foreground.items(), key=lambda x: x[1]["coverage"], reverse=True
        )
        background_colors, foreground_colors = [], []
        background_coverage, foreground_coverage = 0, 0
        for color in background:
            background_colors.append(color[0])
            background_coverage += color[1]["coverage"]
            if (
                background_coverage >= min_coverage
                or len(background_colors) >= max_colors
            ):
                break
        for color in foreground:
            foreground_colors.append(color[0])
            foreground_coverage += color[1]["coverage"]
            if (
                foreground_coverage >= min_coverage
                or len(foreground_colors) >= max_colors
            ):
                break
        return ",".join(background_colors), ",".join(foreground_colors)

    def get_tones(self):
        """
        The tones are cool, neutral, warm with the values ranging from 0 to 1.
        If there is one tone with a value >= 0.5, then that tone is the dominant tone.
        """
        tones = self.color_feats[self.url]["Color Tags"]["overall"]["tones"]
        max_tone = max(tones, key=tones.get)
        if tones[max_tone] >= 0.5:
            return f"The dominant tone of the scene is {max_tone}."
        else:
            return ""

    def get_persons(self):
        """
        Return people category from visual tags but  override by face tags genders if confident
        """
        return ""

    def get_tags(self, C=0.7):
        """
        Return comma separtated tags over C confidence except photography style
        if category is not "none", "{category}: {tag}" else "{tag}"
        """
        tags = self.image_feats[self.url]["Visual Tags"]
        tags = [
            f"{tag['category']}: {tag['tag']}"
            if tag["category"] != "none"
            else tag["tag"]
            
            for tag in tags
            if tag["confidence"] >= C
            and not (tag["category"] in ["photography style", "orientation"])
        ]
        return ",".join(tags)

    def get_ocr(self):
        """
        Return full stop separated text in the scene
        """
        texts = self.ocr[self.ocr["image path"] == "scenes/" + self.image_name][
            "text"
        ].values[0]
        # convert to list string to list
        texts = texts.strip("[]").split(",")
        texts = [text.strip().strip("'") for text in texts]
        texts = "'" + "', '".join(texts) + "'"
        if len(texts) < 3:
            return "There is no text in the scene"
        else:
            return "The text shown in the scene is " + texts

    def get_asr(self):
        """
        "The narration in the scene is {comma separated ASR} in a {MALE/FEMALE} voice" if there is narration else return "There is no narration in the scene"
        """
        return ""

    def get_scene_ranking(self):
        """
        Divide into 3 parts based on the scene ranking
        First -> "This scene is {/2nd/3rd..} most viewed"
        Second -> ""
        Third -> "This scene is {/2nd/3rd..} least viewed"
        """
        return ""

    def verbalise(self) -> List[Tuple[str, float]]:
        return [
            (f"The scene shows {self.get_blip_caption()}.", 1),
            (f"The scene lasts from {self.get_start_time()} to {self.get_end_time()}.", 1),
            (
                f"The foreground colors of the scene are {self.get_colors()[0]} and the background colors are {self.get_colors()[1]}.",
                1,
            ),
            (self.get_tones(), 1),
            (
                f"The photography style of the scene is {self.get_photography_style()}.",
                1,
            ),
            (f"{self.get_clutter()}", 1),
            (f"The scene has {self.get_persons()} .", 1),
            (f"{self.get_body_parts()}.", 1),
            (f"{self.get_num_faces()}", 1),
            (f"This scene is categorized by the tags  {self.get_tags()}.", 1),
            (f"{self.get_ocr()}.", 1),
            (f"{self.get_asr()}", 1),
            (f"{self.get_scene_ranking()}", 1),
        ]

    def __call__(self) -> List[str]:
        entries = self.verbalise()

        return SEP.join([entry[0] for entry in entries if random.random() < entry[1]])


class AdMemResponseVerbalisation:
    def __init__(self, user_id, study_id, video_id) -> None:
        self.user_id = user_id
        self.study_id = study_id
        self.video_id = video_id
        self.df = pd.read_csv(f"/home/harini/response{study_id}.csv")

    def brand_recall_verbalise(self) -> str:
        recalled = self.df[
            (self.df["user_id"] == self.user_id)
            & (self.df["video_id"] == self.video_id)
        ]["recalled"].values[0]

        desc = self.df[
            (self.df["user_id"] == self.user_id)
            & (self.df["video_id"] == self.video_id)
        ]["scene_description"].values[0]
        if recalled == 1:
            response = (
                "The user was able to recall the ad." + f' The user recalled: "{desc}"'
            )

        else:
            response = "The user was not able to recall the ad."
        return response

    def scene_recall_verbalise(self) -> str:
        pass

    def __call__(self) -> List[str]:
        return self.verbalise()
