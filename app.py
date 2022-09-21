from flask import Flask, render_template, request
from nltk.sentiment.vader import SentimentIntensityAnalyzer

app = Flask(__name__)


def sentiment_analyse(t):
    score = SentimentIntensityAnalyzer().polarity_scores(t)
    if score['neg'] > score['pos']:
        return "Negative"
    elif score['neg'] < score['pos']:
        return "Positive"
    else:
        return "Neutral"


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contactUs')
def contactus():
    return render_template('contactUs.html')


@app.route('/teamInfo')
def team_info():
    return render_template('teamInfo.html')


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        sen = request.form['sen']
        output = "The Sentence is " + sentiment_analyse(sen)
        return render_template('output.html', output=output)
    else:
        return render_template('post.html')


if __name__ == "__main__":
    app.run(debug=True)
