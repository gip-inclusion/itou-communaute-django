import os

from github import Github


if __name__ == "__main__":

    GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN", None)
    GITHUB_REPO = os.getenv("GITHUB_REPO", None)

    g = Github(GITHUB_ACCESS_TOKEN)
    repo = g.get_repo(GITHUB_REPO)
    pull_requests = repo.get_pulls(state="closed", sort="merged_at", direction="desc")
    releases = repo.get_releases()
    last_release = releases[0]

    items = []

    for pr in pull_requests:
        if pr.merged_at > last_release.published_at:
            print(f"- {pr.title} (#{pr.number})")

        elif pr.merged_at < last_release.published_at:
            break
