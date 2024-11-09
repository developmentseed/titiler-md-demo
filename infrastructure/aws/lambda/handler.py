"""AWS Lambda handler."""

import logging

from app.main import app
from mangum import Mangum

logging.getLogger("mangum.lifespan").setLevel(logging.ERROR)
logging.getLogger("mangum.http").setLevel(logging.ERROR)

handler = Mangum(app, lifespan="off")
