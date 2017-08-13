#!/usr/bin/env python
# Uses pip packages: b2, PyGithub

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from datetime import datetime
import json
import os
import sys

from b2.api import B2Api
realm_url = 'production'

from github import Github
repo = Github(os.environ['GITHUB_TOKEN']).get_repo('Lukas-W/pdfium')

api = B2Api()
api.authorize_account(realm_url, os.environ['B2_ACCOUNT_ID'], os.environ['B2_APP_KEY'])
bucket = api.get_bucket_by_name(os.environ['B2_BUCKET'])
files = bucket.list_file_names()['files'];

file_dictionary = {};

for file in files:
	file_name = file['fileName'];
	if file_name == 'index.json':
		continue

	sha, system, base_name = file_name.split('/');
	size = file['size'];
	timestamp = datetime.fromtimestamp(file['uploadTimestamp'] / 1000);


	if sha not in file_dictionary:
		file_dictionary[sha] = {'files': []}

	file_dictionary[sha]['files'].append({
		'name': base_name,
		'system': system,
		'size': size,
		'timestamp': timestamp.isoformat(),
		'download_url': bucket.get_download_url(file_name)
	})

build_list = []

for sha in file_dictionary:
	commit = repo.get_commit(sha).commit
	build_list.append({
		'sha': sha,
		'author_date': commit.author.date.isoformat(),
		'committer_date': commit.committer.date.isoformat(),
		'files': file_dictionary[sha]['files']
	})

build_list.sort(key = lambda build: build['author_date'], reverse=True)

json_string = json.dumps(build_list, indent=4)

if 'TRAVIS' in os.environ:
	u = json_string.encode('utf-8')
	bucket.upload_bytes(u, 'index.json', 'application/json')
	print("Uploaded index.json", file=sys.stderr)

print(json_string)
