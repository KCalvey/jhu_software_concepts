from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser


BASE_URL = "https://www.thegradcafe.com/"
ROBOTS_URL = urljoin(BASE_URL, "robots.txt")


def check_robots_txt(target_url):
    """
    Check whether robots.txt allows access to the target URL.
    """
    robot_parser = RobotFileParser()
    robot_parser.set_url(ROBOTS_URL)
    robot_parser.read()

    return robot_parser.can_fetch("*", target_url)


def build_results_url(page_number=1):
    """
    Build a GradCafe results URL for a specific page.
    """
    return urljoin(BASE_URL, f"survey/?page={page_number}")


def main():
    test_url = build_results_url(1)

    print(f"Testing URL: {test_url}")

    if check_robots_txt(test_url):
        print("robots.txt allows access to this URL.")
    else:
        print("robots.txt does not allow access to this URL.")


if __name__ == "__main__":
    main()
