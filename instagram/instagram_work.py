import requests
import re
import json
import hashlib
from datetime import datetime, timedelta
from time import mktime


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
        count_posts = 0
        count_ap_posts = 0
        count = 0
        count_ap = 0
        for post in posts:
            count_posts += 1
            if (not post["node"]["is_video"]) and (("sky" and "outdoor") in post["node"]["accessibility_caption"]):
                count_ap_posts += 1
                data.append((post["node"]["shortcode"], post["node"]["display_url"]))
        print('Searched in {} posts by tag {}, added {} posts'.format(count_posts, self.tag, count_ap_posts))

        if shared_data["entry_data"]["TagPage"][0]["graphql"]["hashtag"]["edge_hashtag_to_media"]["page_info"][
            "has_next_page"]:
            end_cursor = \
                shared_data["entry_data"]["TagPage"][0]["graphql"]["hashtag"]["edge_hashtag_to_media"]["page_info"][
                    "end_cursor"]
        else:
            end_cursor = None

        if end_cursor:

            print("Loading more posts...")

            extra_data = {"after": end_cursor, "first": 30}
            extra_data["name"] = "tag_name"
            extra_data["name_value"] = self.tag
            variables_string = '{{"{name}":"{name_value}","first":{first},"after":"{after}"}}'
            variables = variables_string.format(**extra_data)
            gis = variables

            query_hash = 'f92f56d47dc7a55b606908374b43a314'

            settings = {
                "params": {
                    "query_hash": query_hash,
                    "variables": variables
                },
                "headers": {
                    "X-Instagram-GIS": hashlib.md5(gis.encode("utf-8")).hexdigest(),
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": 'https://instagram.com/explore/tags/{}/'.format(self.tag),
                }
            }

            res = self.session.get("https://www.instagram.com/graphql/query/", **settings)
            json_data = json.loads(res.text)
            next_posts = json_data["data"]["hashtag"]["edge_hashtag_to_media"]["edges"]
            count = 0
            count_ap = 0
            d = 3
            days_ago = datetime.now() - timedelta(days=d)
            timestamp = mktime(days_ago.timetuple())

            print('Only latest posts will be added, not earlier than {} days ago'.format(d))

            for post in next_posts:
                time = post["node"]["taken_at_timestamp"]
                if time > timestamp:
                    count += 1
                    if (not post["node"]["is_video"]) and (
                            ("sky" and "outdoor") in post["node"]["accessibility_caption"]):
                        count_ap += 1
                        data.append((post["node"]["shortcode"], post["node"]["display_url"]))

            print('Searched in {} more posts by tag {}, added {} posts'.format(count, self.tag, count_ap))
        print('Searched in {} posts total, added {} posts'.format(count + count_posts, count_ap + count_ap_posts))
        return data

    def get_location_ids(self):
        location_ids = {}
        # print(self.get_posts())
        count = 0
        for shortcode, src in self.get_posts():
            response = self.session.get('https://www.instagram.com/p/%s/' % shortcode)
            match = re.search(
                r'<script[^>]*>window._sharedData[ ]*=[ ]*((?!</script>).*);</script>',
                response.text,
            )
            data = json.loads(match.group(1))
            if data["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["location"] is not None:
                count += 1
                location_id = data["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["location"]["id"]
                location_ids[shortcode, src] = location_id
        print('Only {} posts had location'.format(count))
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
        count = 0
        for shortcode, (src, x, y) in self.get_location_coors().items():
            response = self.session.get('http://localhost:5000/lightnings/get?lat=%s&lng=%s' % (x, y))
            if response.text == "1":
                data.append((shortcode, src, x, y))
                count += 1
        print('Trying to add to db {} appropriate posts'.format(count))
        return data
