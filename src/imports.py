##
## This code is part of the Jaudit utilty.
##
## (C) Copyright IBM 2023.
##
## This code is licensed under the Apache License, Version 2.0. You may
## obtain a copy of this license in the LICENSE.txt file in the root directory
## of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
##
## Any modifications or derivative works of this code must retain this
## copyright notice, and modified files need to carry a notice indicating
## that they have been altered from the originals.
##

import sys
import os

import re
import json
import csv

import string

import subprocess
import struct
import argparse
import traceback
import inspect

import zipfile as ZipFile
import gzip as gzip

from hashlib import sha256
from socket import gethostname
from io import IOBase, BytesIO, TextIOWrapper
