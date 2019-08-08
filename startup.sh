#!/bin/bash

export FLASK_APP=lslga_inspect
cd /home/admin/lslga-inspect
flask run --host=0.0.0.0 --port=80
