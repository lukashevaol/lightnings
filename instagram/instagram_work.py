import requests
import re
import json


class InstaScraper:
    def __init__(self, tag):
        self.session = requests.Session()
        self.tag = tag
        self.url = 'https://www.instagram.com/explore/tags/' + tag

    def get_posts(self):

        response = self.session.get(self.url)
        match = re.search(
            r'<script[^>]*>window._sharedData[ ]*=[ ]*((?!</script>).*);</script>',
            response.text,
        )
        shared_data = json.loads(match.group(1))
        posts = shared_data["entry_data"]["TagPage"][0]["graphql"]["hashtag"]["edge_hashtag_to_media"]["edges"]
        data = []
        for post in posts:
            if (not post["node"]["is_video"]) and (("sky" and "outdoor") in post["node"]["accessibility_caption"]):
                data.append((post["node"]["shortcode"], post["node"]["display_url"]))
        return data

    def get_location_ids(self):
        location_ids = {}
        for shortcode, src in self.get_posts():
            response = self.session.get('https://www.instagram.com/p/%s/' % shortcode)
            match = re.search(
                r'<script[^>]*>window._sharedData[ ]*=[ ]*((?!</script>).*);</script>',
                response.text,
            )
            data = json.loads(match.group(1))
            if data["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["location"] is not None:
                location_id = data["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["location"]["id"]
                location_ids[shortcode, src] = location_id
        return location_ids

    def get_location_coors(self):
        coors_dict = {}
        for (shortcode, src), location_id in self.get_location_ids().items():
            response = self.session.get('https://www.instagram.com/explore/locations/%s/' % location_id)
            match = re.search(
                r'<script[^>]*>window._sharedData[ ]*=[ ]*((?!</script>).*);</script>',
                response.text,
            )
            data = json.loads(match.group(1))
            lat = data["entry_data"]["LocationsPage"][0]["graphql"]["location"]["lat"]
            lng = data["entry_data"]["LocationsPage"][0]["graphql"]["location"]["lng"]
            coors_dict[shortcode] = src, lat, lng
        return coors_dict

    def appropriate_posts(self):
        data = []
        for shortcode, (src, x, y) in self.get_location_coors().items():
            response = self.session.get('http://localhost:5000/lightnings/get?lat=%s&lng=%s' % (x, y))
            if response.text == "1":
                data.append((shortcode, src, x, y))
        return data
