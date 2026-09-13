# Module 2
## Responsible Scraping and robots.txt

Before collecting any data, I reviewed The GradCafe's robots.txt file to verify that the pages used for this assignment permit crawler access.

The robots.txt file allows the general `*` user agent to access the site while specifically disallowing several restricted paths, including `/signin`, `/register`, `/forgot-password`, `/reset-password`, `/confirm-password`, `/verify-email`, and `/profile`.

This scraper will access only publicly available GradCafe pages permitted by robots.txt. It will not attempt to access restricted or login-protected pages or bypass CAPTCHAs, rate limits, Cloudflare verification, or other access restrictions. The scraper will also use reasonable delays between page requests and will stop if the website blocks, rate-limits, or otherwise rejects requests.

Evidence of the robots.txt review is included in `screenshot.jpg`.
