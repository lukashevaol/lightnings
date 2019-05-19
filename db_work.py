import requests
import json
from db_manager import session_scope
from models import Coordinate, Post
from instagram.instagram_scraper import InstaScraper
import sys

sys.path.append('../')


def add_lightnings():
    '''
    Adds lightnings data from lightnings.ru to db
    '''
    r = requests.get('http://www.lightnings.ru/vr44_24.php?LA=53&LO=38')
    data = json.loads(r.text.replace("rs", "\"rs\""))
    coors = data['rs']

    with session_scope() as s:
        for coor in coors:
            coordinate = Coordinate()
            coordinate.first_point_lat = coor['p1t']
            coordinate.first_point_lng = coor['p1n']
            coordinate.second_point_lat = coor['p2t']
            coordinate.second_point_lng = coor['p2n']
            coordinate.third_point_lat = coor['p3t']
            coordinate.third_point_lng = coor['p3n']
            coordinate.fourth_point_lat = coor['p4t']
            coordinate.fourth_point_lng = coor['p4n']
            coordinate.cnt = coor['cnt']
            coordinate.start_date = coor['DS']
            coordinate.end_date = coor['DE']
            s.add(coordinate)
    return "Updated lightnings db"


def get_lightnings(lat, lng):
    '''
    Checks if there are lightnings with these coordinates in db
    '''
    with session_scope() as s:
        lightning_coors = s.query(Coordinate).filter(Coordinate.first_point_lat >= lat).filter(
            Coordinate.second_point_lat <= lat). \
            filter(Coordinate.first_point_lng >= lng).filter(Coordinate.third_point_lng < lng).all()
        if len(lightning_coors) > 0:
            return "1"
        else:
            return "0"


def add_posts(tag='lightnings'):
    '''
    Adds posts to db
    '''
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
