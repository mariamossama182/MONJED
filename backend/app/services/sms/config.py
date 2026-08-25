"""
MONJED SMS Configuration

Africa's Talking credentials.
"""

import os

from dotenv import load_dotenv


load_dotenv()



AFRICAS_TALKING_USERNAME = os.getenv(
    "AFRICAS_TALKING_USERNAME"
)


AFRICAS_TALKING_API_KEY = os.getenv(
    "AFRICAS_TALKING_API_KEY"
)


AFRICAS_TALKING_SENDER_ID = os.getenv(
    "AFRICAS_TALKING_SENDER_ID",
    "MONJED",
)