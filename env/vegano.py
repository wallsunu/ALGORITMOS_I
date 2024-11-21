from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('plan.html')

@app.route('/vegano')
def vegan_check():
    return render_template('plan.html')

if __name__ == '__main__':
    app.run(debug=True)



