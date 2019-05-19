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

    def caption_check(self, post, *captions):
        '''
        Checks if post has captions
        '''
        for caption in captions:
            if not (caption in post["node"]["accessibility_caption"]):
                return False
        return True

    def get_next_posts(self, end_cursor, days=1):
        '''
        Loads next posts
        :param days: time limit (load posts added not earlier than x days ago)
        :return:
        '''
        next_posts = []
        print("Loading more posts...")

        extra_data = {"after": end_cursor, "first": 30}
        extra_data["name"] = "tag_name"
        extra_data["name_value"] = self.tag
        variables = '{{"{name}":"{name_value}","first":{first},"after":"{after}"}}'.format(**extra_data)

        query_hash = 'f92f56d47dc7a55b606908374b43a314'

        settings = {
            "params": {
                "query_hash": query_hash,
                "variables": variables
            },
            "headers": {
                "X-Instagram-GIS": hashlib.md5(variables.encode("utf-8")).hexdigest(),
                "X-Requested-With": "XMLHttpRequest",
                "Referer": 'https://instagram.com/explore/tags/{}/'.format(self.tag),
            }
        }

        res = self.session.get("https://www.instagram.com/graphql/query/", **settings)
        json_data = json.loads(res.text)
        next_posts_json = json_data["data"]["hashtag"]["edge_hashtag_to_media"]["edges"]

        count_next_posts = 0
        count_good_next_posts = 0
        days_ago = datetime.now() - timedelta(days=days)
        timestamp = mktime(days_ago.timetuple())

        print('Only latest posts will be added, not earlier than {} days ago'.format(days))
        for post in next_posts_json:
            time = post["node"]["taken_at_timestamp"]
            if time > timestamp:
                count_next_posts += 1
                if (not post["node"]["is_video"]) and self.caption_check(post, "sky", "outdoor"):
                    count_good_next_posts += 1
                    next_posts.append((post["node"]["shortcode"], post["node"]["display_url"]))

        print('Searched in {} more posts by tag {}, selected {} more posts'.format(count_next_posts, self.tag,
                                                                                   count_good_next_posts))
        return next_posts

    def get_posts(self):
        '''
        Selects posts from explore/tag instagram page
        Returns their shortcode and display url
        '''
        data = []

        response = self.session.get(self.url)
        match = re.search(
            r'<script[^>]*>window._sharedData[ ]*=[ ]*((?!</script>).*);</script>',
            response.text,
        )
        shared_data = json.loads(match.group(1))
        posts = shared_data["entry_data"]["TagPage"][0]["graphql"]["hashtag"]["edge_hashtag_to_media"]["edges"]

        count_posts = 0
        count_good_posts = 0

        for post in posts:
            count_posts += 1
            if (not post["node"]["is_video"]) and self.caption_check(post, "sky", "outdoor"):
                count_good_posts += 1
                data.append((post["node"]["shortcode"], post["node"]["display_url"]))
        print('Searched in {} posts by tag {}, selected {} posts'.format(count_posts, self.tag, count_good_posts))

        if shared_data["entry_data"]["TagPage"][0]["graphql"]["hashtag"]["edge_hashtag_to_media"]["page_info"][
            "has_next_page"]:
            end_cursor = \
                shared_data["entry_data"]["TagPage"][0]["graphql"]["hashtag"]["edge_hashtag_to_media"]["page_info"][
                    "end_cursor"]
        else:
            end_cursor = None

        if end_cursor:
            next_posts = self.get_next_posts(end_cursor)
            for post in next_posts:
                data.append(post)
        return data

    def get_location_ids(self):
        '''
        Checks if selected posts have location
        If they do, adds them to dict with key (shortcode, display url)
        '''
        location_ids = {}
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
        print('Only {} posts has location'.format(count))
        return location_ids

    def get_location_coors(self):
        '''
        Gets coordinate location by location id
        Returns dict with display urls and coordinates by shortcode key
        '''
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
        '''
        Checks if there is a lightning with the location in db for each selected post
        Returns appropriate posts
        '''
        data = []
        count = 0
        for shortcode, (src, x, y) in self.get_location_coors().items():
            response = self.session.get('http://localhost:5000/lightnings/get?lat=%s&lng=%s' % (x, y))
            if response.text == "1":
                data.append((shortcode, src, x, y))
                count += 1
        print('Trying to add to db {} appropriate posts'.format(count))
        return data
