#! /usr/bin/env python
from adopt import db

db.reflect()
db.drop_all()
