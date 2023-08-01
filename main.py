import flask,json,hashlib,uuid,time
app=flask.Flask("AccountSystem")
tokens={}
def loadConf():
    with open("users.json","r") as f:
        return json.load(f)
def writeConf(conf):
    with open("users.json","w+") as f:
        return json.dump(conf,f)
@app.route("/")
def main():
    return flask.render_template("mainpage.html")
@app.route("/signup")
def signup():
    return flask.render_template("signup.html")
@app.route("/login")
def login():
    return flask.render_template("login.html")
@app.route("/clientarea")
def clientarea():
    token=flask.request.cookies.get("token")
    if token not in tokens.keys():
        return flask.render_template("unloggedin.html")
    #get user info
    conf=loadConf()
    info=conf[tokens[token]]
    last_login=info["last_login"]
    if last_login == 0:
        last_login="无记录"
    else:
        last_login=time.ctime(last_login)
    return flask.render_template("clientarea.html",username=tokens[token],last_login=last_login)
@app.route("/api/signup",methods=["POST"])
def signup_api():
    args=flask.request.form
    name=args.get("email")
    pswd=args.get("password")
    if not name or not pswd:
        return flask.render_template("error.html",error="电子邮件和密码为必填项目。")
    #detect conflict
    conf=loadConf()
    if name in conf.keys():
        return flask.render_template("error.html",error="此电子邮件已注册过此站点。")
    #detect length
    if len(name) > 50 or len(pswd) > 128:
        return flask.render_template("error.html",error="长度不合法。")
    #vaildate
    if "@" not in name or name.endswith("@"):
        return flask.render_template("error.html",error="你最好填真实电子邮箱。")
    #create then
    conf.update({
        name:{
        "password":hashlib.sha512(pswd.encode("utf-8")).hexdigest(), #PRIVACY!,
        "last_login":0}
    })
    writeConf(conf)
    return flask.render_template("redirect_model.html",message="注册完成，请进行登入。")
@app.route("/api/login",methods=["POST"])
def login_api():
    args=flask.request.form
    name=args.get("email")
    pswd=args.get("password")
    if not name or not pswd:
        return flask.render_template("error.html",error="电子邮件和密码为必填项目。")
    #detect conflict
    conf=loadConf()
    if name not in conf.keys():
        return flask.render_template("error.html",error="找不到账号。")
    #vaildate
    if hashlib.sha512(pswd.encode("utf-8")).hexdigest() != conf[name]["password"]:
        return flask.render_template("error.html",error="密码错误。")
    #generate token
    tid=str(uuid.uuid4())
    tokens.update({tid:name})
    #write conf
    conf[name]["last_login"]=time.time()
    writeConf(conf)
    #generate response
    resp=flask.make_response(flask.redirect("/clientarea"))
    resp.set_cookie("token",tid,86400)
    return resp
@app.route("/logout")
def logout():
    token=flask.request.cookies.get("token")
    if token in tokens.keys():
        del tokens[token]
    return flask.redirect("/")
app.run(port=9988)