from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('ejercicio1.html')

@app.route('/ejercicio')
def exercise_check():
    return render_template('ejercicio1.html')

if __name__ == '__main__':
    app.run(debug=True)
