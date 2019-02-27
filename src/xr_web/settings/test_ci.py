from .test import *  # noqa
import os

WEBPACK_LOADER = {
    "DEFAULT": {
        "BUNDLE_DIR_NAME": "bundles/",
        "STATS_FILE": os.path.join(
            os.path.dirname(BASE_DIR),  # noqa
            "webpack",
            "webpack-stats-production.json",
        ),  # noqa
    }
}

SKIP_SELENIUM = False
