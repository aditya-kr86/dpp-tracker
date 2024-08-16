import requests
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, timezone
USERNAME = "pari-kumari"
Graph_id = "dpp-entry"
TOKEN = "hjkbsa154ecakjksclc65496sc1c"
pixela_endpoint = "https://pixe.la/v1/users"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

utc_plus_530 = timezone(timedelta(hours=5, minutes=30))
current_time = datetime.now(utc_plus_530)

class Todo(db.Model):
    slno = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone(timedelta(hours=5, minutes=30))).replace(hour=0, minute=0, second=0, microsecond=0))

    def __repr__(self) -> str:
        return f"{self.slno} - {self.desc} - {self.date_created}"


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == "POST":
        physics = request.form.get('physics_input') if request.form.get('physics') == 'other' else request.form.get('physics')
        chemistry = request.form.get('chemistry_input') if request.form.get('chemistry') == 'other' else request.form.get('chemistry')
        mathematics = request.form.get('mathematics_input') if request.form.get('mathematics') == 'other' else request.form.get('mathematics')
        dpp_count = int(physics) + int(chemistry) + int(mathematics)
        desc = f"PHY: {physics}, CHEM: {chemistry}, MATHS: {mathematics}"
        todo = Todo(desc=desc)

        #################################### Post DPP Count to Pixela ##########
        date = current_time.strftime("%Y%m%d")
        # date = "20240802"
        graph_value_endpoint = f"{pixela_endpoint}/{USERNAME}/graphs/{Graph_id}"
        graph_value_config = {
            "date": date,
            "quantity": str(dpp_count)  # Pixela expects quantity as a string
        }
        headers = {
            "X-USER-TOKEN": TOKEN
        }
        requests.post(url=graph_value_endpoint, json=graph_value_config, headers=headers)
        db.session.add(todo)
        db.session.commit()
    # Fetch all Todo items ordered by slno in descending order
    allTodo = Todo.query.order_by(Todo.slno.desc()).all()
    return render_template('index.html', allTodo=allTodo)




@app.route('/update/<int:slno>', methods=['GET','POST'])
def update(slno):
    todo = Todo.query.filter_by(slno=slno).first()
    if request.method == "POST":
        physics = request.form.get('physics_input') if request.form.get('physics') == 'other' else request.form.get('physics')
        chemistry = request.form.get('chemistry_input') if request.form.get('chemistry') == 'other' else request.form.get('chemistry')
        mathematics = request.form.get('mathematics_input') if request.form.get('mathematics') == 'other' else request.form.get('mathematics')
        dpp_count = int(physics) + int(chemistry) + int(mathematics)
        desc = f"PHY: {physics}, CHEM: {chemistry}, MATHS: {mathematics}"

        # Convert date_created to 'YYYYMMDD' format
        which_date = todo.date_created.strftime('%Y%m%d')

        ##------------------------STEP-4-Update graph---------------##
        graph_value_endpoint = f"{pixela_endpoint}/{USERNAME}/graphs/{Graph_id}/{which_date}"
        graph_value_config = {
            "quantity": str(dpp_count)
        }
        headers = {
            "X-USER-TOKEN": TOKEN
        }
        requests.put(url=graph_value_endpoint, json=graph_value_config, headers=headers)

        todo.desc = desc
        db.session.commit()
        return redirect("/")
    return render_template('update.html', todo=todo)


@app.route('/delete/<int:slno>')
def delete(slno):
    todo = Todo.query.filter_by(slno=slno).first()
    ##------------------------------STEP-5-DELETE---------------------------------------##
    # Convert date_created to 'YYYYMMDD' format
    date = todo.date_created.strftime('%Y%m%d')
    graph_value_endpoint = f"{pixela_endpoint}/{USERNAME}/graphs/{Graph_id}/{date}"
    headers = {
            "X-USER-TOKEN": TOKEN
        }
    requests.delete(url=graph_value_endpoint, headers=headers)
    
    # Delete the todo item from the database
    db.session.delete(todo)
    db.session.commit()
    
    return redirect("/")

if __name__=="__main__":
    app.run()
