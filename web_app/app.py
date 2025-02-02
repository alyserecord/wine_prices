# Demonstrates Bootstrap version 3.3 Starter Template
# available here: https://getbootstrap.com/docs/3.3/getting-started/#examples

from flask import Flask, render_template,request, send_from_directory,jsonify
import pandas as pd
import numpy as np
import os
app = Flask(__name__)
import sys
sys.path.insert(0, '../src')
from recommender import CosineSimilarity

df = pd.read_csv('data/sorted_df.csv')

# home page
@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html', table = df)

@app.route("/search_results", methods=['GET','POST'])
def search_results():
    if request.method=='POST':
        selected_origin = request.form.get('origin')
        selected_varietal = request.form.get('varietal')
        print(selected_varietal)
        selected_price = request.form.get('price')
        # df = pd.read_csv('../data/64x64/sorted_df.csv')
        if selected_varietal == 'Select a varietal (optional)':
            selected = df[(df['origin']==selected_origin) & (df['price_bins']==selected_price)]
        else:
            selected = df[(df['origin']==selected_origin) & (df['varietal']==selected_varietal) & (df['price_bins']==selected_price)]
        try:
            subset = selected.sample(21)
        except:
            subset = selected
        if subset.shape[0] > 0:
            subset['name'] = subset['name'].astype(str) + '.jpg'
            subset = subset['name'].tolist()
            if len(subset)% 3 != 0 and len(subset)>3:
                subset = subset[:-(len(subset)%3)]
        else:
            subset = []
    return render_template("search_results.html",image_list = subset)


MEDIA_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'images')
MEDIA_FOLDER = '../images/'
@app.route('/images/<path:filename>')
def download_file(filename):
    return send_from_directory(MEDIA_FOLDER, filename)

def get_wines(selected_wine,num_rec):
    # commenting the following block out because it regenerated
    # the cosine simarilty matrix each time and was memory intensive
    nmf_topics = pd.read_csv('../data/64x64/nmf_topics.csv')    
    cs = CosineSimilarity(df,nmf_topics)
    cs.prep_sorted_data()
    cs.scale_nmf_clusters()
    cs.merge_files()
    # cs.generate_matrix()
    return cs.get_recommendation(selected_wine,20)  

    # similarity_matrix = np.load('../web_app/data/similarity_matrix.npy')
    # wine_index = df.name[df.name == selected_wine].index[0]
    # similar_indices = similarity_matrix[wine_index].argsort()[-2:-num_rec-2:-1]
    # items = []
    # for i in similar_indices:
    #     items.append(df.name[i])
    # return items


@app.route('/recomendations', methods=['GET','POST'])
def recommendations():

    selected_wine = request.args.get('type')
    selected_wine_att = []
    selected_wine_att.append(df[df['name']==selected_wine[:-4]]['varietal'].values[0])
    selected_wine_att.append(df[df['name']==selected_wine[:-4]]['origin'].values[0])
    selected_wine_att.append(format(df[df['name']==selected_wine[:-4]]['price'].values[0],'.2f'))
    selected_wine_att.append(df[df['name']==selected_wine[:-4]]['kmeans_label'].values[0]+1)
    selected_wine_att.append(df[df['name']==selected_wine[:-4]]['description'].values[0])
    wines = get_wines(selected_wine[:-4],21)
    # print(wines)
    items = []
    for wine in wines:
        lst = []
        lst.append('{}.jpg'.format(wine))
        lst.append(wine)
        lst.append(format(df[df['name']==wine]['price'].values[0],'.2f'))
        lst.append(df[df['name']==wine]['varietal'].values[0])
        lst.append(df[df['name']==wine]['origin'].values[0])
        lst.append(df[df['name']==wine]['kmeans_label'].values[0]+1)        
        lst.append(df[df['name']==wine]['description'].values[0])
        items.append(lst)
    return render_template('recommendations.html',img_name = selected_wine, selected_wine_att = selected_wine_att, recs = items)

@app.route('/get_varietal')
def get_varietal():
    origin = request.args.get('origin')
    price = request.args.get('price')
    sub_df = df[(df['origin']==origin) & (df['price_bins']==price)]
    varietal = sub_df['varietal'].unique()
    varietal = sorted(varietal)
    data = [{'id':i} for i in varietal]
    return jsonify(data)

@app.route('/get_prices')
def get_prices():
    origin = request.args.get('origin')
    sub_df = df[(df['origin']==origin)]
    prices = sub_df['price_bins'].unique()
    alphabet = "<251"
    prices = sorted(prices, key=lambda word: [alphabet.index(c) for c in word[0]])
    data = [{'id':i} for i in prices]
    return jsonify(data)

@app.route('/about', methods=['GET'])
def about():
    about = "Wine Recommender was built by Alyse Record, a wine lover and data scientist. The data was scraped from Wine.com \
        and contains features such as wine label, description, price, varietal and origin. Several unsupervised machine \
        learning models were applied to extract features from the wine labels and descriptions for use in the recommender. \
        The recommender uses cosine similiarity to find the wine that are most like the user's selection based on price,\
        origin, label, description and varietal."
    
    
    return render_template('about.html',para = about)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8105, threaded=True, debug=False)
