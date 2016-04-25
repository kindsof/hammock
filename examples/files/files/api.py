import falcon
import hammock
import resources


application = falcon.API()
hammock.Hammock(application, resources)

# from werkzeug.contrib.profiler import ProfilerMiddleware
# application = ProfilerMiddleware(application, profile_dir='profile')
