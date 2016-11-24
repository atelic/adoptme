#! /usr/bin/env python
import sys

import requests

from adopt import db, Project, User

GH_API_BASE = 'https://api.github.com/'


def insert_repos(repos):
    for repo in repos:
        user = User.query.filter_by(username=repo['owner']).first()
        if not user:
            user = User(
                repo['owner'],
                'password',
                repo['owner']
            )
        db.session.add(user)
        db.session.commit()
        p = Project(
            repo['name'],
            repo['url'],
            repo['description'],
            caretaker_id=user.id
        )
        db.session.add(p)
        db.session.commit()


def main(dry=True):
    repos = []

    r = requests.get(GH_API_BASE + 'search/repositories?q=stars:>1&s=stars&type=Repositories')
    items = r.json()['items']

    for item in items:
        if item['private']:
            continue
        r = {
            'name': item['name'],
            'full_name': item['full_name'],
            'url': item['html_url'],
            'private': item['private'],
            'description': item['description'],
            'owner': item['owner']['login'],
            'languages': requests.get(GH_API_BASE + 'repos/{}/languages'.format(item['full_name'])).json().keys()
        }
        repos.append(r)

    if not dry:
        insert_repos(repos)


if __name__ == '__main__':
    dry = '--dry' in sys.argv or '-d' in sys.argv
    main(dry=dry)
