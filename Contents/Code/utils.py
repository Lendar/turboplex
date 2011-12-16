SITE = "http://turbofilm.tv"

def get_url(path=""):
    if path.startswith(SITE):
        return path
    else:
        return SITE + path