"""
Retrieves a list of locales missing in Pontoon for a single project by comparing with GitHub repo.

Output as CSV file with column Missing Locales.

"""
import argparse
import json
from urllib.parse import quote as urlquote
from urllib.request import urlopen

IGNORE = ["templates", "configs"]

def retrieve_pontoon_locales(project):
    query = f'{{project(slug:"{project}"){{name,localizations{{locale{{code}}}}}}}}'
    url = f"https://pontoon.mozilla.org/graphql?query={urlquote(query)}"
    response = urlopen(url)
    json_data = json.load(response)

    locale_list = []
    for locale in json_data['data']['project']['localizations']:
        locale_list.append(locale['locale']['code'])
    return locale_list

def retrieve_github_locales(owner, repo, path):
    query = f'/repos/{owner}/{repo}/contents/{path}'
    url = f"https://api.github.com{urlquote(query)}"
    response = urlopen(url)
    json_data = json.load(response)
    
    locale_list = []
    for content in json_data:
        #Ignore files, non-locale folders via ignore list or anything that starts with "." (e.g. .github)
        if content['type'] == "dir" and content['name'] not in IGNORE and content['name'][0] != ".":
            locale_list.append(content['name'])
    return locale_list

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pontoon",
        required=True,
        dest="pontoon_project",
        help="Pontoon project name",
    )
    parser.add_argument(
        "--repo",
        required=True,
        dest="github_repo",
        help="GitHub repository name",
    )
    parser.add_argument(
        "--owner",
        required=False,
        default="mozilla-l10n",
        dest="github_owner",
        help="GitHub repository owner name",
    )
    parser.add_argument(
        "--path",
        required=False,
        default="",
        dest="github_path",
        help="GitHub path that contains locale folders",
    )

    args = parser.parse_args()

    missing_locales = ["Missing Locales"]
    pontoon_locales = retrieve_pontoon_locales(args.pontoon_project)
    github_locales = retrieve_github_locales(args.github_owner, args.github_repo, args.github_path)

    for locale in github_locales:
        if locale not in pontoon_locales:
            missing_locales.append(locale)
    
    with open("output.csv", "w") as f:
        f.write("\n".join(missing_locales))
        print("Missing locales saved to output.csv")

if __name__ == "__main__":
    main()