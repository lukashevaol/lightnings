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
        r = requests.get(('http://localhost:5000/posts/update/%s' % tag))
        if (r.status_code == 200):
            return r.text
        else:
            return False


def main():
    print(posts_job_with_tags("lightning", "lightnings", "молния", "молнии", "гроза", "thunderstorm"))
    # lightnings_job()

    # schedule.every().day.at('10:00').do(lightnings_job())
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)


if __name__ == '__main__':
    main()
