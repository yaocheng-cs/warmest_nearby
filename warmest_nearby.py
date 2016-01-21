'''
Created on Feb 25, 2013

@author: yaocheng
'''

import cherrypy
from geo_weather import get_warmest_nearby

ERROR_RADIUS = 0.5 # in km
NEARBY_RADIUS = 48.28032 # in km (30 miles)
NUM_DAYS = 7
NUM_CANDIDATE = 30
NUM_RESULT = 10

index_html = open('/Users/yaocheng/Documents/aptana_workspace/WeatherNearby/index.html', 'r').read()
#index_html = open('/var/www/html/index.html', 'r').read()

dummy = [[(1362009600, 'February 27, 2013', 'Wednesday', 'Auburndale', 75, 53, 64),
          (1362009600, 'February 27, 2013', 'Wednesday', 'Riverview', 74, 50, 62),
          (1362009600, 'February 27, 2013', 'Wednesday', 'Woodland', 75, 40, 57),
          (1362009600, 'February 27, 2013', 'Wednesday', 'Newton', 57, 35, 46),
          (1362009600, 'February 27, 2013', 'Wednesday', 'Cedarwood', 57, 34, 45)],
         
         [(1362096000, 'February 28, 2013', 'Thursday', 'Woodland', 78, 48, 63),
          (1362096000, 'February 28, 2013', 'Thursday', 'Auburndale', 74, 47, 60),
          (1362096000, 'February 28, 2013', 'Thursday', 'Riverview', 73, 45, 59),
          (1362096000, 'February 28, 2013', 'Thursday', 'Cedarwood', 49, 33, 41),
          (1362096000, 'February 28, 2013', 'Thursday', 'Newton Lower Falls', 47, 31, 39)],
         
         [(1362182400, 'March 01, 2013', 'Friday', 'Woodland', 82, 50, 66),
          (1362182400, 'March 01, 2013', 'Friday', 'Auburndale', 65, 42, 53),
          (1362182400, 'March 01, 2013', 'Friday', 'Riverview', 64, 42, 53),
          (1362182400, 'March 01, 2013', 'Friday', 'Cedarwood', 47, 30, 38),
          (1362182400, 'March 01, 2013', 'Friday', 'Newton', 47, 29, 38)]]


def get_result_html(result, term):
    html = '<h3>Warmest places around "%(term)s"</h3>\n' % {'term': term} 
    html += '<table border="1">\n'
    ranked = zip(*result)
    tr = '<tr>\n'
    tr += '<th></th>\n'
    for day in result:
        cal = day[0][1]
        wkd = day[0][2]
        tr += '<th>%(wkd)s<br/>%(cal)s</th>\n' % {'wkd': wkd, 'cal': cal}
    tr += '</tr>\n'
    html += tr
    for i in range(len(ranked)):
        tr = '<tr>\n'
        rankers = ranked[i]
        if i == 0:
            tr += '<th>Warmest</th>\n'
        elif i == len(ranked) - 1:
            tr += '<th>Coldest</th>\n'
        else:
            tr += '<th></th>\n'
        for ranker in rankers:
            place = ranker[3]
            high = ranker[4]
            low = ranker[5]
            tr += '<td align="center">%(place)s<br/>High: <b><i>%(high)s</i></b> Low: <b><i>%(low)s</b></i></td>\n' % {'place': place, 'high': high, 'low': low}
        tr += '</tr>\n'
        html += tr
    html += '</table>'
    return html
        

class WarmestNearby(object):
    
    @cherrypy.expose
    def index(self):
        #return 'OnePage class index!'
        return index_html
    
    @cherrypy.expose
    def search(self, city=None, state=None, code=None, radius=None):
        # if nothing is filled in the form, name_code and radius will be None, not empty string
        if not city and not code:
            return 'Please specify a place to search'
        if code:
            try:
                int(code)
                if code[0] == '-':
                    return 'Please input a integer without negative sign as postal code'
            except ValueError:
                return 'Please input a integer as postal code'
            term = code
        else:
            term = city
            if state:
                term += ' ' + state
        if radius:
            try:
                radius = 1.609344 * float(radius)
            except ValueError:
                return 'Please input a number as search radius'
        else:
            radius = NEARBY_RADIUS
        '''
        result = dummy
        '''
        result = get_warmest_nearby(term, \
                                    ERROR_RADIUS, \
                                    radius, \
                                    NUM_DAYS, \
                                    NUM_CANDIDATE, \
                                    NUM_RESULT)
        
        if isinstance(result, str):
            return result # result contains the error message
        elif result == []:
            return 'No nearby weather information retrieved'
        return get_result_html(result, term)
        
        
class Root(object):
    pass


root = Root()
root.warmestnearby = WarmestNearby()

#cherrypy.server.socket_host = '129.64.46.103'
cherrypy.quickstart(root)