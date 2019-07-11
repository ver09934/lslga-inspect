from flask import Flask, make_response, render_template, send_file
app = Flask(__name__)

@app.route('/')
def hello():
    simple_label = "Matplotlib generated image."
    test_label = "Testing image return"
    return render_template('index.html', simple_label=simple_label, test_label=test_label)

# Using base from https://gist.github.com/wilsaj/862153

@app.route('/simple.png')
def simple():
    
    import datetime
    from io import BytesIO
    import random

    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter

    fig = Figure()
    ax = fig.add_subplot(111)
    x = []
    y = []

    now = datetime.datetime.now()
    delta = datetime.timedelta(days=1)

    for i in range(10):
        x.append(now)
        now += delta
        y.append(random.randint(0, 1000))

    ax.plot_date(x, y, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    canvas = FigureCanvas(fig)

    png_output = BytesIO()
    canvas.print_png(png_output)
    response = make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response

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

    return send_file(img_io, mimetype='image/jpeg')

    ''' '''
    response = make_response(img_io.getvalue())
    response.headers['Content-Type'] = 'image/jpeg'
    return response
    ''' '''

    '''
    from flask import Response
    return Response(img_io, mimetype='img/jpeg')
    '''

if __name__ == "__main__":
    app.run(debug=True)
