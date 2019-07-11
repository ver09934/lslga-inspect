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

    args = request.args

    # Throw HTTP 500 error if ra/dec are nonexistent/empty
    if not ('ra' in args and 'dec' in args):
        abort(500)
    if args['ra'] == '' or args['dec'] == '':
        abort(500)

    ra = args['ra']
    dec = args['dec']
    
    default_pixscale = 0.262
    if 'pixscale' in args:
        if args['pixscale'] == '':
            pixscale = default_pixscale
        else:
            pixscale = args['pixscale']
    else:
        pixscale = default_pixscale

    # Would be easy to add new url args here
    for i, (key, value) in enumerate(args.items()):
        prefix = '?' if i == 0 else '&'
        url += "{}{}={}".format(prefix, key, value)
            
    r = requests.get(url)

    img = Image.open(BytesIO(r.content))

    draw_ellipses(img, ra, dec, pixscale)

    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)

    response = make_response(img_io.getvalue())
    response.headers['Content-Type'] = 'image/jpeg'
    return response

def draw_ellipses(img, ra, dec, pixscale):
    draw = ImageDraw.Draw(img)
    fill = (0, 255, 0)
    width = 3
    draw.line((img.size[0]/2, 0, img.size[0]/2, img.size[1]), fill=fill, width=width)
    draw.line((0, img.size[1]/2, img.size[0], img.size[1]/2), fill=fill, width=width)

if __name__ == "__main__":
    app.run(debug=True)
