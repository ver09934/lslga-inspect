from flask import Flask, make_response, render_template

app = Flask(__name__)

@app.route('/')
def hello():
    test_label = "Test image:"
    return render_template('index.html', test_label=test_label)

@app.route('/test.jpg')
def test():

    import requests
    from PIL import Image, ImageDraw
    from io import StringIO
    from io import BytesIO

    url = 'http://legacysurvey.org/viewer/jpeg-cutout?ra=149.6670&dec=28.8776&zoom=13&layer=decals-dr7'
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
