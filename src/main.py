from scraping_build import * 



def routine():
    get_all_build_from_date(get_yesterday_date())


if __name__ == "__main__":
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    parent_dir = os.path.dirname(script_dir)
    os.chdir(parent_dir)
    routine()