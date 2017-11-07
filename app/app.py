from flask import Flask
from flask import render_template
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map

app = Flask(__name__)
GoogleMaps(app)

@app.route('/')
def mapdemo():
        # creating a map in the view
        locates = []
        with open('out.json', 'r') as f:
            for data in f.readlines():
                locates.append(eval(data))
        flaskmap = Map(
            identifier="test",
            lat=39.9129,
            lng=116.40,
            zoom=15,
            maptype='SATELLITE',
            markers=locates,
            style="width:100%;height:100%;"
        )
        return render_template('map.html',mymap=flaskmap)

if __name__=='__main__':
    app.run(debug=True)
