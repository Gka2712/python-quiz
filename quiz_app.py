from flask import Flask,render_template,request,jsonify,redirect
import json
import os
import requests

app=Flask(__name__)
DATA_FILE='data.json'
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE,'r') as f:
        return json.load(f)
def save_data(data):
    with open(DATA_FILE,'w') as f:
        json.dump(data,f,indent=4)

def get_new_id():
    data=load_data()
    if not data:
        return 1
    else:
        return max(item['id'] for item in data) + 1
@app.route('/')
def main():
    response=requests.get('http://127.0.0.1:5000/items')
    if response.status_code==200:
        return render_template('main.html',quizzes=response.json())
    else:
        return "Error",response.status_code    
@app.route('/quiz/<int:quiz_id>')
def quiz_main(quiz_id):
    responses=requests.get('http://127.0.0.1:5000/items')
    if responses.status_code==200:
        data=responses.json()
        quiz_data=next((item for item in data if item['id']==quiz_id),None)
        quizlen=len(quiz_data)
        return render_template('quiz_main.html',quiz_data=quiz_data,quizlen=quizlen)
    else:
        print("Error:",responses.status_code)
@app.route('/quiz/<int:quiz_id>/question/<int:question_id>')
def quiz_question(quiz_id,question_id):
    responses=requests.get('http://127.0.0.1:5000/items')
    if responses.status_code==200:
        data=responses.json()
        quiz_data=next((item for item in data if item['id']==quiz_id),None)
        quizlen=len(quiz_data["quiz"])
        return render_template('question.html',quiz_data=quiz_data,quiz_id=quiz_id,question_id=question_id,quizlen=quizlen)
    else:
        print("Error:",responses.status_code)
@app.route('/sadmin')
def admin_main():
    return render_template('admin_main.html')
@app.route('/sadmin/makequiz')
def makequiz():
    return render_template('makequiz.html')
@app.route('/sadmin/storequiz',methods=['POST'])
def storequiz():
    name=request.form['qname']
    quiz_data={"name":name,"quiz":[]}
    response=requests.post('http://127.0.0.1:5000/items',json=quiz_data,headers={'Content-Type':'application/json'})
    if response.status_code==201:
        print("Quiz added successfully!")
        quiz_id=get_new_id()
        return render_template('storequiz.html',quiz=response.json(),quiz_id=quiz_id)
    else:
        print("Error",response.status_code)
        return "Error",response.status_code
    
@app.route('/sadmin/quizlist')
def quizlist():
    response=requests.get('http://127.0.0.1:5000/items')
    if response.status_code==200:
        return render_template('quizlist.html',quizzes=response.json())
    else:
        return "Error",response.status_code
@app.route('/sadmin/editquiz/<int:quiz_id>')
def editquiz(quiz_id):
    responses=requests.get('http://127.0.0.1:5000/items')
    if responses.status_code==200:
        data=responses.json()
        quiz_data=next((item for item in data if item['id']==quiz_id),None)
        return render_template('editquiz.html',quiz_data=quiz_data)
    else:
        print("Error:",responses.status_code)
@app.route('/sadmin/editdetailquiz/<int:quiz_id>')
def editquizdetail(quiz_id):
    return render_template('editdetailquiz.html',quiz_id=quiz_id)
@app.route('/sadmin/storequizdetail/<int:quiz_id>',methods=['POST'])
def storequizdetail(quiz_id):
    quiz=request.form['quiz']
    ans1=request.form['ans1']
    ans2=request.form['ans2']
    ans3=request.form['ans3']
    ans4=request.form['ans4']
    cans=request.form['cans']
    new_quiz={"quiz":quiz,"ans1":ans1,"ans2":ans2,"ans3":ans3,"ans4":ans4,"cans":cans}
    response=requests.post(f'http://127.0.0.1:5000/items/{quiz_id}/quiz',json=new_quiz)
    if response.status_code==201:
        print("Quiz added successfully!")
        quiz_id=get_new_id()-1
        return render_template('detailquizmessage.html',quiz_id=quiz_id)
    else:
        print("Error",response.status_code)
        return "Error",response.status_code
@app.route('/items',methods=['GET'])
def get_item():
    data=load_data()
    return jsonify(data)
@app.route('/items',methods=['POST'])
def post_item():
    new_item=request.json
    new_item['id']=get_new_id()
    data=load_data()
    data.append(new_item)
    save_data(data)
    return jsonify(new_item),201
@app.route('/items',methods=['PUT'])
def put_item(item_id):
    updated_item=request.json
    data=load_data()
    for item in data:
        if item['id']==item_id:
            item.update(updated_item)
            save_data(data)
            return jsonify(item)
        return jsonify({'error':'item not found'},404)
@app.route('/items/<int:item_id>',methods=['DELETE'])
def delete_item(item_id):
    data=load_data()
    data=[item for item in data if item['id']!=item_id]
    save_data(data)
    return '',204
@app.route('/items/<int:item_id>/quiz',methods=['POST'])
def add_quizdetail(item_id):
    new_quiz=request.json
    data=load_data()
    for item in data:
        if item["id"]==item_id:
            if not isinstance(item["quiz"],list):
                return jsonify({"Error":"Quiz should be a list"}),400
            item["quiz"].append(new_quiz)
            save_data(data)
            return jsonify(item),201
        return jsonify({"Error":"Item not found"}),404

if __name__=='__main__':
    app.run(debug=True)