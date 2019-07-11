from flask import Flask, make_response, render_template, request, abort
import requests
from PIL import Image, ImageDraw
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def hello():
    test_label = "Test image"
    test_url = "/jpeg-cutout?ra=352.6064&dec=0.1568&zoom=13&layer=dr8&width=500&height=500"
    return render_template('index.html', test_label=test_label, test_url=test_url)

@app.route('/jpeg-cutout')
def test():
        
    url = 'http://legacysurvey.org/viewer/jpeg-cutout'
    
    # Professional debugging
    mystr = '-'*60
    def fancy_print(thing):
        print("{mystr}\n{}\n{mystr}".format(thing, mystr=mystr))
    def long_print():
        print(mystr)

    if not ('dec' in request.args and 'ra' in request.args):
        abort(500) # Return http 500 error
    
    ra = request.args['ra']
    dec = request.args['dec']
    
    default_pixscale = 0.262
    if 'pixscale' in request.args:
        pixscale = request.args['pixscale']
    else:
        pixscale = default_pixscale

    # Would be easy to add new url args here
    for i, (key, value) in enumerate(request.args.items()):
        prefix = '?' if i == 0 else '&'
        url += "{}{}={}".format(prefix, key, value)
            
    r = requests.get(url)

    img = Image.open(BytesIO(r.content))

    draw = ImageDraw.Draw(img)
    fill = (0, 255, 0)
    width = 3
    draw.line((img.size[0]/2, 0, img.size[0]/2, img.size[1]), fill=fill, width=width)
    draw.line((0, img.size[1]/2, img.size[0], img.size[1]/2), fill=fill, width=width)

    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)

    response = make_response(img_io.getvalue())
    response.headers['Content-Type'] = 'image/jpeg'
    return response

def draw_ellipses(pil_image, ra, dec, pixscale):
    pass

if __name__ == "__main__":
    app.run(debug=True)
