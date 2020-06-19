import argparse
import asyncio
import json
import logging
import os
import aiohttp
from datetime import date, timedelta, datetime
import requests
import time
import webbrowser
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from itertools import groupby
from operator import itemgetter
import constants, installer

def render_web_page(rows_header, rows_data, org, d_date):
    template_dir = Path(__file__).resolve().parent.parent.joinpath('templates')
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("template.html")
    output = template.render(organization_name=org['name'], rows_header=rows_header, rows_data=rows_data,
                             requested_date=d_date)
    file_path = template_dir.joinpath('tracker.html')
    with open(file_path, 'w') as ffile:
        ffile.write(output)
    webbrowser.open_new_tab('file:///' + str(file_path))


def generate_tables(projects, members, activities):
    unique_user_ids, unique_project_ids = [], []
    for each in activities:
        if each['user_id'] not in unique_user_ids:
            unique_user_ids.append(each['user_id'])
        if each['project_id'] not in unique_project_ids:
            unique_project_ids.append(each['project_id'])

    grouper = itemgetter("project_id", "user_id")
    worked_time_data = []
    for key, grp in groupby(sorted(activities, key=grouper), grouper):
        temp_dict = {"project_id": key[0], "user_id": key[1],
                     "tracked": time.strftime("%H:%M", time.gmtime(sum(item["tracked"] for item in grp)))}
        worked_time_data.append(temp_dict)

    rows_header_data = [""]
    for uid in unique_user_ids:
        for each in members:
            if uid == each['id']:
                rows_header_data.append(each['name'])
                break

    rows_time_data = []
    for pid in unique_project_ids:
        each_row = []
        for org in projects:
            if org['id'] == pid:
                each_row.append(org['name'])
                break
        for uid in unique_user_ids:
            for wtd in worked_time_data:
                if wtd['user_id'] == uid and wtd['project_id'] == pid:
                    each_row.append(wtd['tracked'])
                    break
            else:
                each_row.append("")
        rows_time_data.append(each_row)
    return rows_header_data, rows_time_data

async def get_projects(sess, org, projects, org_url):
    url = org_url + str(org['id']) + projects
    async with sess.get(url) as response:
        data = await response.json()
    if not data['projects']:
        raise Exception("No projects in org.")
    return data['projects']


async def get_members(sess, org, members_url, org_url):

    url = org_url + str(org['id']) + members_url
    async with sess.get(url) as response:
        data = await response.json()
    if not data['users']:
        raise Exception("No members in org.")
    return data['users']


async def get_activities(sess, org, activity_url, d_date):
    beg_time = datetime.combine(d_date, datetime.min.time())
    end_time = beg_time + timedelta(hours=23, minutes=59)

    beg_time = beg_time.isoformat() + "Z"
    end_time = end_time.isoformat() + "Z"

    params = {'organizations': org['id'], 'start_time': beg_time, 'stop_time': end_time}
    async with sess.get(activity_url, params=params) as response:
        data = await response.json()
    if not data['activities']:
        raise Exception("No activities in organization.")
    return data['activities']



async def get_server_data(app_token, auth_token, projects, org_url, org, members_url, d_date, activity_url):
    headers = {'App-Token': app_token, 'Auth-Token': auth_token}
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=150), raise_for_status=True,
                                     headers=headers) as sess:

        tasks = [asyncio.create_task(get_projects(sess, org, projects, org_url)),
                 asyncio.create_task(get_members(sess, org, members_url, org_url)),
                 asyncio.create_task(get_activities(sess, org, activity_url, d_date))]
        try:
            results = await asyncio.gather(*tasks, return_exceptions=False)
            rows_header_data, rows_time_data = generate_tables(*[each for each in results])
            render_web_page(rows_header_data, rows_time_data, org, d_date)
        except Exception as e:
            for each in tasks:
                if not each.done():
                    each.cancel()
            raise e


def main():
    installer.installer()
    email = input("\n\n\n\n\nEnter the email for which you want the requested data. Press enter for default value \n") or 'yunusdev5@gmail.com'
    password = input("Enter the password of the account for which you want the requested data. Press enter for default value \n") or 'Stupid123'
    app_token = input("Enter the app-token for which you want the requested data. Press enter for default value \n") or 'n2DwvM7Yzq6lqhQ-Xthdys7LEBNj40ZidSUPOpnnLD8'
    d_date = input("Enter the date for which you want the requested data. Default value is yesterday date\n") or datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
    home_url = constants.home_url
    activity_url = constants.activity_url
    org_url = constants.org_url
    user_url = constants.user_url
    projects_url = constants.projects_url
    projects = constants.projects
    organizations = constants.organizations
    members_url = constants.members_url
    d_date = datetime.strptime(d_date, '%Y-%m-%d').date()
    sess = requests.Session()
    post_data = {'email': email, 'password': password}
    headers = {'App-Token': app_token}
    res = sess.post(home_url, data=post_data, headers=headers, timeout=50)
    res.raise_for_status()
    data = res.json()

    auth_token = data['user']['auth_token']
    user_id = data['user']['id']

    headers = {'App-Token': app_token, 'Auth-Token': auth_token}
    res = sess.get(user_url + str(user_id) + organizations, headers=headers, timeout=50)
    res.raise_for_status()
    data = res.json()

    organization = data['organizations'][0]
    if not data['organizations']:
        raise Exception("No organization found for user.")

    try:
        asyncio.run(get_server_data(app_token, auth_token, projects, org_url,
                                    organization, members_url, d_date, activity_url))
    except Exception as e:
        logging.error(e)


if __name__ == "__main__":
    main()

