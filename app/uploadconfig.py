ALLOWED_EXTENTIONS =  set(['png','jpg','jpeg','pdf'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENTIONS