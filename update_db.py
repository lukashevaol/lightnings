import requests
import json
from db_manager import session_scope
from models import Coordinate, Post
from instagram.instagram_work import InstaScraper
import sys

sys.path.append('../')


def add_lightnings():
    r = requests.get('http://www.lightnings.ru/vr44_24.php?LA=53&LO=38')
    data = json.loads(r.text.replace("rs", "\"rs\""))
    coors = data['rs']

    with session_scope() as s:
        for coor in coors:
            coordinate = Coordinate()
            coordinate.p1t = coor['p1t']
            coordinate.p1n = coor['p1n']
            coordinate.p2t = coor['p2t']
            coordinate.p2n = coor['p2n']
            coordinate.p3t = coor['p3t']
            coordinate.p3n = coor['p3n']
            coordinate.p4t = coor['p4t']
            coordinate.p4n = coor['p4n']
            coordinate.cnt = coor['cnt']
            coordinate.DS = coor['DS']
            coordinate.DE = coor['DE']
            s.add(coordinate)
    return "Updated lightnings db"


def get_lightnings(lat, lng):
    with session_scope() as s:
        lightning_coors = s.query(Coordinate).filter(Coordinate.p1t >= lat).filter(Coordinate.p2t <= lat). \
            filter(Coordinate.p1n >= lng).filter(Coordinate.p3n < lng).all()
        if len(lightning_coors) > 0:
            return "1"
        else:
            return "0"


def add_posts(tag='olyadelaetproektpodd'):
    scraper = InstaScraper(tag)
    with session_scope() as s:
        posts = scraper.appropriate_posts()
        if len(posts) > 0:
            print('Checking if some of them are already in db...')
            count = 0
            for el in posts:
                exists = (s.query
                          (s.query(Post.id).filter_by(shortcode=el[0]).exists())
                          ).scalar()
                if not exists:
                    post = Post()
                    post.shortcode = el[0]
                    post.photo = el[1]
                    post.lat = el[2]
                    post.lng = el[3]
                    s.add(post)
                    count += 1
            print('Added to db {} posts'.format(count))
            return "Updated posts table"
        else:
            return "Nothing to add in table"
