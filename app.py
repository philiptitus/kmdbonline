from flask import Flask, render_template,request, redirect,session
import pymysql
import os
from werkzeug.utils import secure_filename
from sms import send_sms



app = Flask(__name__)

app.secret_key = "Strovold19."


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDERS = os.path.join(APP_ROOT, "static\images")
app.config['UPLOAD_FOLDERS'] = UPLOAD_FOLDERS


@app.route("/")
def index():
    con = pymysql.connect(host="localhost", user="root", password="", database="mov")
    cursor = con.cursor()
    dramaCursor = con.cursor()
    actionsCursor = con.cursor()
    horrorsCursor = con.cursor()
    romancesCursor = con.cursor()
    
    sql = "SELECT * FROM products"
    dramaSql = "SELECT * FROM products WHERE product_cat = 'dramas' LIMIT 4"
    actionSql = "SELECT * FROM products WHERE product_cat = 'actions' LIMIT 4"
    horrorSql = "SELECT * FROM products WHERE product_cat = 'horrors' LIMIT 4"
    romanceSql = "SELECT * FROM products WHERE product_cat = 'romances' LIMIT 4"
    
    cursor.execute(sql)
    dramaCursor.execute(dramaSql)
    actionsCursor.execute(actionSql)
    horrorsCursor.execute(horrorSql)
    romancesCursor.execute(romanceSql)
    
    allproducts = cursor.fetchall()
    alldramas = dramaCursor.fetchall()
    allactions = actionsCursor.fetchall()
    allhorrors = horrorsCursor.fetchall()
    allromances = romancesCursor.fetchall()
    
    return render_template("home.html", products=allproducts, dramas=alldramas, actions=allactions, horrors=allhorrors, romances=allromances)


@app.route("/categories/<category>")
def categories(category):
    con = pymysql.connect(host="localhost", user="root", password="", database="mov")
    cursor = con.cursor()
    sql = "SELECT * FROM products WHERE product_cat = %s"
    cursor.execute(sql, (category,))
    allproducts = cursor.fetchall()
    return render_template("products.html", products=allproducts, cat_name=category)


@app.route("/product/<product_id>")
def product(product_id):
    con = pymysql.connect(host="localhost", user="root", password="", database="mov")
    cursor = con.cursor()
    sql = """
SELECT p.*, AVG(r.rating) AS average_rating
FROM products p
LEFT JOIN ratings r ON p.product_id = r.product_id
WHERE p.product_id = %s
GROUP BY p.product_id
"""

    cursor.execute(sql, (product_id,))
    allProducts = cursor.fetchone()
    return render_template("singleproduct.html", product=allProducts)


@app.route("/upload")
def upload():
    if request.args.get("msg") != "":
        msg = request.args.get("msg")
        return render_template("upload.html", msg=msg)
    else:
        return render_template("upload.html", msg="")


@app.route("/save-products", methods=['GET', 'POST'])
def saveProducts():
    con = pymysql.connect(host="localhost", user="root", password="", database="mov")
    cur = con.cursor()
    if request.method == 'POST':
        product_name = request.form['product_name']
        product_desc = request.form['product_desc']
        product_cost = request.form['product_cost']
        product_category = request.form['product_cat']
        product_image = request.files['product_image']
        myFileName = secure_filename(product_image.filename)
        if product_name == "" or product_desc == "" or product_cost == "" or product_category == "" or product_image== "":
            msg = "Please Fill In All Fields"
            return redirect(f"/upload?msg={msg}")
        else:
            sql= "INSERT INTO products(product_name,product_desc,product_cost,product_cat,product_img_path)VALUES (%s,%s,%s,%s,%s)"
            cur.execute(sql,(product_name,product_desc,product_cost,product_category,myFileName))
            con.commit()
            product_image.save(os.path.join(app.config['UPLOAD_FOLDERS'],myFileName))
            msg="Products Added Successfuly"
            return redirect(f"/upload?msg={msg}")

    else:
         msg="the method was not post"
         return redirect(f"/upload?msg={msg}")


@app.route("/register")
def register():
    if request.args.get("msg") != "":
        msg = request.args.get("msg")
        color = request.args.get("color")
        return render_template("register.html", msg=msg,color=color)
    else:
        return render_template("register.html", msg="",color="")

@app.route("/save-user", methods=['GET', 'POST'])
def saveUsers():
    con = pymysql.connect(host="localhost", user="root", password="", database="mov")
    cur = con.cursor()
    if request.method == 'POST':
        f_name = request.form['f_name']
        l_name = request.form['l_name']
        email = request.form['email']
        phone = request.form['phone']
        dob = request.form['dob']
        password = request.form['password']
        c_password = request.form['c_password']

        if f_name == "" or l_name == "" or email == "" or phone == "" or dob == "" or password == "":
            msg = "Please Fill In All Fields"
            color = "danger"
            return redirect(f"/register?msg={msg}&color={color}")
    
        elif len(password) <=8:
            msg = "password must have at least eight characters"
            color = "danger"
            return redirect(f"/register?msg={msg}&color={color}")

        elif password != c_password:
            msg = "passwords don't match"
            color = "danger"
            return redirect(f"/register?msg={msg}&color={color}")
    
        else:
            sql= "INSERT INTO users(f_name,l_name,email,phone,dob,password)VALUES (%s,%s,%s,%s,%s,%s)"
            cur.execute(sql,(f_name,l_name,email,phone,dob,password))
            con.commit()
            message = "You have successfuly registerd on sokogarden"
            send_sms(phone,message)
            msg = "Info Added Successfuly"
            color = "danger"
            return redirect(f"/upload?msg={msg}&color={color}")
            
    else:
        msg = "the method was not post"
        color="danger"
        return redirect(f"/upload?msg={msg}")



@app.route("/login")
def login():
    if request.args.get("msg") != "":
        msg = request.args.get("msg")
        color = request.args.get("color")
        return render_template("login.html", msg=msg,color=color)
    else:
        return render_template("login.html", msg="",color="")

@app.route("/do-login", methods=['GET', 'POST'])
def dologin():
    con = pymysql.connect(host="localhost", user="root", password="", database="mov")
    cur = con.cursor()
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]
        if email == "" or password == "":
           msg = "Please Fill In All Fields"
           color = "danger"
           return redirect(f"/login?msg={msg}&color={color}")
        elif len(password) <=8:
            msg = "password must have at least eight characters"
            color = "danger"
            return redirect(f"/register?msg={msg}&color={color}")
        else:
            sql = "SELECT user_id FROM users WHERE email = %s AND password = %s LIMIT 1"
            cur.execute(sql,(email,password))
            user = cur.fetchone()
            if cur.rowcount == 1:
                session['key'] = str  (user[0])
                return redirect("/profile")
            else:
                msg = "Email and Password are incorrect"
                color = "danger"
                return redirect(f"/login?msg={msg}&color={color}")
            
           

    else:
        msg = "the method was not post"
        color = "danger"
        return redirect(f"/login?msg={msg}&color={color}")       


@app.route("/logout")
def logout():
    session.pop('key',None)
    return redirect("/login")

@app.route("/profile")
def profile():
    if "key" in session:
        user_id = session['key']
        con = pymysql.connect(host="localhost", user="root", password="", database="mov")
        cur = con.cursor()
        sql = "SELECT f_name,l_name  FROM users WHERE user_id = %s"
        cur.execute(sql,(user_id))
        data = cur.fetchone()
        return render_template("profile.html",data=data)
    else:
        msg = "you must be logged in to access"
        color = "danger"
        return redirect(f"/login?msg={msg}&color={color}")








@app.route("/ratings/")
def ratings():
    if "key" in session:
        con = pymysql.connect(host="localhost", user="root", password="", database="mov")
        cur = con.cursor()
        sql = "SELECT product_id, product_name, product_cost FROM products WHERE product_id = %s"
        product_id = 1  # Replace with the actual product ID you want to retrieve
        cur.execute(sql, (product_id,))
        data = cur.fetchone()
        return render_template("ratings.html", data=data)
    else:
        
            msg = "You must be logged in to access this page"
            color = "danger"
            return redirect(f"/login?msg={msg}&color={color}")


@app.route("/save-ratings", methods=['GET', 'POST'])
def saveRatings():
    con = pymysql.connect(host="localhost", user="root", password="", database="mov")
    cur = con.cursor()

    if request.method == 'POST':
        product_id = request.form['product_id']
        rating = request.form['rating']

        if product_id == "" or rating == "":
            msg = "Please Fill In All Fields"
            color = "danger"
            return redirect(f"/ratings?msg={msg}")
        else:
            try:
                rating = float(rating)
                if rating < 1 or rating > 10:
                    msg = "Rating must be between 1 and 10"
                    color = "danger"
                    return redirect(f"/ratings?msg={msg}")

                sql = "INSERT INTO ratings(product_id, rating) VALUES (%s, %s)"
                cur.execute(sql, (product_id, rating))
                con.commit()
                msg = "Rating submitted successfully"
                color = "warning"
                return redirect(f"/ratings?msg={msg}")
            except ValueError:
                msg = "Invalid rating value"
                return redirect(f"/ratings?msg={msg}")
    else:
        msg = "Invalid request method"
        return redirect(f"/ratings?msg={msg}")








if __name__ == "__main__":
    app.run(debug=True)
    import pdb; pdb.set_trace()
