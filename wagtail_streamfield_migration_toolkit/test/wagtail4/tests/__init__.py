import os
from wagtail import VERSION as WAGTAIL_VERSION


def load_tests(loader, standard_tests, pattern):
    if WAGTAIL_VERSION > (4, 0, 0):
        this_dir = os.path.dirname(__file__)
        package_tests = loader.discover(start_dir=this_dir, pattern=pattern)
        standard_tests.addTests(package_tests)
        return standard_tests
    else:
        return None
