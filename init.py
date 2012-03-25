import tornado.ioloop
import tornado.web
import os.path
import json
import urllib2
import time


class Ecole(object):
    def __init__(self, ecole, infos):
        self.ecole = ecole
        self.distance_text = infos['distance']['text']
        self.distance = infos['distance']['value']
        self.status = infos['status']

def make_the_call(address, ecoles):
    url="http://maps.googleapis.com/maps/api/distancematrix/json?origins=%s&destinations=%s&sensor=false"%\
(address.replace(" ", "+"), "|".join(["%s+Champagne+Ardennes"%ecole for ecole in ecoles]))
    print url

    #return []
    result = urllib2.urlopen(url)
    response = result.read()
    json_load = json.loads(response)
    assert(len(ecoles) == len(json_load["rows"][0]["elements"]))
    temp = []
    for i in range(0, len(ecoles)):
        temp.append(Ecole(ecoles[i], json_load["rows"][0]["elements"][i]))

    return temp

def handle_treatment(region, address):
    f = open("marne.ecoles")
    lines = json.loads("".join(f.readlines()))
    f.close()
    sizeofecoles = len(lines)
    i=0
    j=0
    distances_ecoles = []
    ecoles = []
    while j < sizeofecoles:
        if i == 100:
            temp = make_the_call(address, ecoles)
            distances_ecoles.extend(temp)
            ecoles = []
            i = 0
            time.sleep(10)
        else:
            lines[i]
            i += 1
            ecole = lines[j].keys()[0]
            ecoles.append(ecole)
            j +=1

    if ecoles:
        temp = make_the_call(address, ecoles)
        distances_ecoles.extend(temp)


    return distances_ecoles


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        region = None
        address = None
        if 'region' in self.request.arguments:
            region = self.request.arguments['region'][0]
        if 'address' in self.request.arguments:
            address = self.request.arguments['address'][0]
        if not region or not address:
            self.render("info.template", regions=['marne', 'aisne', 'ardennes'])
        else:
            list_ecoles = handle_treatment(region, address)
            if list_ecoles is None:
                self.write("Impossible de lire le fichier ecole")
            else:
                self.render("ecoles.template", list_ecoles=list_ecoles)

application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()




