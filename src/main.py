from scraping_build import * 



def routine():
    get_all_build_from_date(get_yesterday_date())


if __name__ == "__main__":
    routine()