from flask import Flask, render_template, request
import pandas as pd
import time
import pafy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


app = Flask(__name__)


def get_comments(page_url):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(page_url)
    driver.maximize_window()
    time.sleep(15)
    prev_h = 0
    while True:
        height = driver.execute_script("""
                function getActualHeight() {
                    return Math.max(
                        Math.max(document.body.scrollHeight, document.documentElement.scrollHeight),
                        Math.max(document.body.offsetHeight, document.documentElement.offsetHeight),
                        Math.max(document.body.clientHeight, document.documentElement.clientHeight)
                    );
                }
                return getActualHeight();
            """)
        driver.execute_script(f"window.scrollTo({prev_h},{prev_h + 200})")
        time.sleep(1)
        prev_h += 200

        if prev_h >= height:
            break
        if height >= 10000:
            break
    content = driver.find_elements(By.CLASS_NAME, 'style-scope ytd-comment-renderer')

    comments = []
    for i in range(len(content)):
        comments.append((content[i].text.split('\n'))[2])
        if i == 100:
            break
    driver.close()
    return comments


data = pd.read_csv('static/numbered_dataset_words.csv', usecols=['sl.no', 'score', 'word'])
words = {}
scores = {}
for s, k, v in zip(data['sl.no'], data['word'], data['score']):
    words[s] = k
    scores[s] = v


def keymaker(filtered_sentence):
    keystore = []
    for i in filtered_sentence:
        if i in words.values():
            for key, value in words.items():
                if i == value:
                    keystore.append(key)
    return keystore


def polarity(filtered_sentence):
    polarities = []
    for i in keymaker(filtered_sentence):
        polarities.append(scores.get(i))
    total = 0
    for j in polarities:
        j = int(j)
        total = total + j
    return int(total)


def senti_analyse(net_polarity):
    if net_polarity >= 1:
        return "POSITIVE"
    elif net_polarity < 0:
        return "NEGATIVE"
    else:
        return "NEUTRAL"


def analyse(comments):
    polarity_list = []
    count = 0
    for i in comments:

        stop_words = set(stopwords.words('english'))
        w_tokens = word_tokenize(i)
        fil_sen = []
        for w in w_tokens:
            if w not in stop_words:
                fil_sen.append(w)
        count += 1
        if count == 100:
            break

        p = polarity(fil_sen)
        polarity_list.append(p)
        net_polarity = 0

        for j in polarity_list:
            net_polarity += j
        return senti_analyse(net_polarity)


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
        purl = request.form['sen']
        video = pafy.new(purl)
        value = video.videoid
        vrl = "https://www.youtube.com/embed/" + value
        comments = get_comments(purl)
        res = analyse(comments)
        if res is not None:
            output = str(len(comments))
            result = "This Video generally has {} reviews".format(res)
            return render_template('output.html', output=output, result=result, vrl=vrl)
        else:
            output = "0"
            result = "Error"
            return render_template('output.html', output=output, result=result, vrl=vrl)
    else:
        return render_template('post.html')


if __name__ == "__main__":
    app.run(debug=True)
