import requests


def update_lightnings():
    requests.get('http://localhost:5000/lightnings/update')
    print("did lightnings update")


def update_posts():
    r = requests.get('http://localhost:5000/posts/update')
    if (r.status_code == 200):
        return r.text
    else:
        return False


def update_posts_by_tags(*tags):
    for tag in tags:
        print('Searching for {} tag started'.format(tag))
        res = requests.get(('http://localhost:5000/posts/update/%s' % tag))
        print(res.status_code)


def main():
    update_lightnings()
    update_posts_by_tags("thunder", "lightning")


if __name__ == '__main__':
    main()
