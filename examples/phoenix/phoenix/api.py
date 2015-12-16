from __future__ import absolute_import
import falcon
import hammock
from phoenix import resources

API = falcon.API()
hammock.Hammock(API, resources)
