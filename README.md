# Github-Stargazers-Scraper
Uses the Github GraphQL API to get the usernames of people who starred certain repos. Since the rate limit of the API can be quite restrictive (currently 5000 requests/hour at 100 users each), the script is autonomous and designed for very long runtimes.

## Usage
- If you don't have one already, generate a personal access token [here](https://github.com/settings/tokens). The token needs to have repo and user access.
- Open the script and replace the token variable with your own.
- In the same directory as the script, create a simple text file containing the repositories you want to scrape, one per line. The expected format is "username/repository" (for example, this would be "FluffyPanda69/Github-Stargazers-Scraper"). An example file is already provided.
- Run

## How it works
As the script goes through each repository, it will write its stargazers in an individual file. There are multiple checks in place to ensure that once a file is written, it contains the right data in the correct format. If the script is stopped and then restarted, all repos with a coresponding file in place will be considered done and ignored.

When the rate limit is about to be reached, the script will simply sleep until it is allowed to make requests again.

If an unexpected error is encountered, the script will attempt to continue while its remaining rate allows it. This might lead to lockups in extreme cases (API is down or network connection is lost). If the error isn't fatal, it will be mentioned at the top of the file that was being worked on.

### Disclaimer
I've let this run continuously on the provided list for over a day and encountered no fatal errors. However edge cases will likely break it. Checking for such things would likely halve the proper request rate and I don't want that, so if you're going to use this check on it from time to time. Alternatively, setup a supervisor to restart it if it closes.