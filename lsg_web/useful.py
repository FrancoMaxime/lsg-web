def set_actif(request):
    actif = 0
    if 'actif' in request.form:
        if request.form['actif'] == 'on':
            actif = 1
        elif request.form['actif'] == "off":
            actif = 0
        elif request.form['actif'] == "1" or request.form['actif'] == 1:
            actif = 1
        else:
            actif = 0
    return actif