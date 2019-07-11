from flask import Flask, make_response, render_template, request
import requests
from PIL import Image, ImageDraw
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def hello():
    test_label = "Test image:"
    return render_template('index.html', test_label=test_label)

@app.route('/jpeg-cutout')
def test():

    # url = 'http://legacysurvey.org/viewer/jpeg-cutout?ra=149.6670&dec=28.8776&zoom=13&layer=decals-dr7'
    url = 'http://legacysurvey.org/viewer/jpeg-cutout?ra=149.6670&dec=28.8776&zoom=13&layer=decals-dr7'
        
    base_image_url = 'http://legacysurvey.org/viewer/jpeg-cutout'
    
    # Professional debugging
    mystr = '-'*60
    def fancy_print(thing):
        print("{mystr}\n{}\n{mystr}".format(thing, mystr=mystr))
    def long_print():
        print(mystr)

    fancy_print(request.args)

    url_args = request.args

    for key, value in url_args.items():
        print("{}: {}".format(key, value))

    long_print()
    
    # --------------------------------------------------------------
        
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

if __name__ == "__main__":
    app.run(debug=True)
