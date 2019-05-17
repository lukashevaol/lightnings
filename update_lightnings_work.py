import schedule
import time
import requests


def lightnings_job():
    requests.get('http://localhost:5000/lightnings/update')
    print("did lightnings update")


def posts_job():
    r = requests.get('http://localhost:5000/posts/update')
    if (r.status_code == 200):
        return r.text
    else:
        return False


def posts_job_with_tags(*tags):
    for tag in tags:
        print('Searching for {} tag started'.format(tag))
        res = requests.get(('http://localhost:5000/posts/update/%s' % tag))
        print(res.status_code)


def main():
    lightnings_job()
    posts_job_with_tags("lightnings")


if __name__ == '__main__':
    main()
