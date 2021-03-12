import sys
import time
from datetime import datetime
from os import path

import requests


def run_query(q):
    request = requests.post('https://api.github.com/graphql', json={'query': q}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, q))


token = ""

headers = {"Authorization": "Bearer " + token}

if len(token) < 20:
    print("Missing access token or token is incorrect !")
    sys.exit(1)

try:
    with open("repos.txt", 'r') as topfile:
        repos = topfile.readlines()
        repos = [x.strip() for x in repos]
except Exception as e:
    print("Error reading repos file (\"repos.txt\")!")
    sys.exit(1)

reposet = [i for n, i in enumerate(repos) if i not in repos[:n]]

print("Found " + str(len(reposet)) + " distinct repos to check")

processed = 0

for repository in reposet:

    processed += 1

    if (len(repository) < 4) or ('/' not in repository):
        print("Repository name " + repository + " is not valid!\n")
        continue

    owner = repository.split('/')[0]
    repo = repository.split('/')[1]
    filename = "users_" + owner + "_" + repo + ".txt"

    if path.exists(filename):
        print("Already processed repository " + owner + "/" + repo + "!\n")
        continue

    query = """
    {{ 
        repository(owner: "{0}", name: "{1}") {{
            stargazers(first: 100 {2}) {{
                pageInfo {{
                endCursor
                hasNextPage
                }}
            nodes{{
                login
            }}
            }}
        }}
        rateLimit {{
        limit
        cost
        remaining
        resetAt
        }}
    }}
    """

    userlist = []
    hasNextPage = True
    endCursor = ""
    count = 0
    errors = []

    starttime = datetime.now()
    print("Started requests for " + owner + "/" + repo)
    print(starttime.strftime("%H:%M:%S"))

    while hasNextPage:
        this_query = query.format(owner, repo, endCursor)
        try:
            result = run_query(this_query)
        except Exception as e:
            print("\nGot an unexpected response :\n" + str(e))
            errors.append(str(e))
            continue

        if result["data"]["repository"] is None:
            hasNextPage = False
            continue

        hasNextPage = result["data"]["repository"]["stargazers"]["pageInfo"]["hasNextPage"]
        endCursor = result["data"]["repository"]["stargazers"]["pageInfo"]["endCursor"]
        endCursor = ', after: "' + endCursor + '"'
        data = result["data"]["repository"]["stargazers"]["nodes"]

        if count == 0:
            limit = result["data"]["rateLimit"]["limit"]
            print("Hourly rate point limit = " + str(limit) + "\n")

        cost = result["data"]["rateLimit"]["cost"]
        remaining = result["data"]["rateLimit"]["remaining"]
        resetAt = result["data"]["rateLimit"]["resetAt"]

        if data is not None:
            for name in data:
                if name is not None:
                    if name["login"] is not None:
                        userlist.append(name["login"])

        count += 100

        timetoreset = datetime.strptime(resetAt, '%Y-%m-%dT%H:%M:%SZ') - datetime.utcnow()

        # print(str(count))

        if count % 1000 == 0:
            print(str(count) + " users processed.")
            print("We have " + str(remaining) + " query points remaining this hour.")
            print("Current hour resets in " + str(timetoreset) + "\n")

        if remaining < 100:
            print("\n[" + datetime.now().strftime("%H:%M:%S") + "] Nearing rate limit, sleeping until rate reset...\n")
            time.sleep(timetoreset.total_seconds() + 10)
            print("\n[" + datetime.now().strftime("%H:%M:%S") + "] Woke up, trying to continue...\n")

    if len(userlist) > 1:
        endtime = datetime.now()
        print("Finished requests for " + owner + "/" + repo + "\n")
        print(endtime.strftime("%H:%M:%S"))
        timedif = endtime - starttime
        print("\nGot " + str(len(userlist)) + " users in " + str(timedif))
        print("\nSorting and writing userlist...\n")

        userlist.sort(key=str.lower)

        with open(filename, 'w+') as the_file:
            if len(errors) > 0:
                the_file.write("Errors:\n")
                for error in errors:
                    the_file.write(error + "\n")
                the_file.write("\n")
            for user in userlist:
                the_file.write(user + "\n")
        print("Done writing " + filename + " \n")
    else:
        print("Could not get any stargazers for " + owner + "/" + repo + "!")
        print("Maybe the repo does not exist or is private?\n")

    print("Processed " + str(processed) + " repos out of " + str(len(reposet)))

print("Done gathering stargazers for all given repos!")
