from flask import Flask,request,render_template,jsonify
import numpy as np
import joblib
import pandas as pd
import folium
from branca.element import Figure 

app=Flask(__name__)

model=None
rmodel=None


@app.route('/')
def home():
    
    return render_template('index.html')

@app.route("/main",methods=['POST'])
def main():
    global model
    global subtitle
    global df
    global rdf
    global rmodel

    button_value = request.form['button']
    if button_value == 'hyderabad':
        subtitle="Hyderabad"
        model=joblib.load('models/hyderabad-pred.joblib')
        df=pd.read_csv('models/FINAL_hyd.csv')
        rmodel=joblib.load('models/FINAL_hyderabad_rent.joblib')
        rdf=pd.read_csv('models/final_Hyderabad_rent.csv')
    elif button_value == 'chennai':
        subtitle="Chennai"
        model=joblib.load('models/chennai-pred.joblib')
        df=pd.read_csv('models/FINAL_che.csv')
        rmodel=joblib.load('models/FINAL_chennai_rent.joblib')
        rdf=pd.read_csv('models/final_Chennai_rent.csv')
    elif button_value == 'kolkata':
        subtitle="Kolkata"
        model=joblib.load('models/kolkata-pred.joblib')
        df=pd.read_csv('models/FINAL_kol.csv')
        rmodel=joblib.load('models/FINAL_kolkata_rent.joblib')
        rdf=pd.read_csv('models/final_Kolkata_rent.csv')
    elif button_value == 'bangalore':
        subtitle="Bangalore"
        model=joblib.load('models/bangalore-pred.joblib')
        df=pd.read_csv('models/FINAL_bang.csv')
        rmodel=joblib.load('models/FINAL_bangalore_rent.joblib')
        rdf=pd.read_csv('models/final_Bangalore_rent.csv')
    elif button_value == 'mumbai':
        subtitle="Mumbai"
        model=joblib.load('models/mumbai-pred.joblib')
        df=pd.read_csv('models/FINAL_mum.csv')
        rmodel=joblib.load('models/FINAL_mumbai_rent.joblib')
        rdf=pd.read_csv('models/final_Mumbai_rent.csv')
    elif button_value == 'delhi':
        subtitle="Delhi"
        model=joblib.load('models/delhi-pred.joblib')
        df=pd.read_csv('models/FINAL_del.csv')
        rmodel=joblib.load('models/FINAL_delhi_rent.joblib')
        rdf=pd.read_csv('models/final_Delhi_rent.csv')


    rdf=rdf[rdf['Latitude']!='Not found'].reset_index(drop=True)
    rdf['price'] = rdf['price'].str.replace(',', '')
    rdf['price']=rdf['price'].astype(float)

    jsonify(df.to_dict(orient='records'))
    jsonify(rdf.to_dict(orient='records'))
    print(rdf.head())


    return render_template('main.html',sub_title=subtitle,)

@app.route("/predict",methods=['POST'])
def predict():
    global subtitle
    


    if request.form.get('predict') == 'predict':
        print('c')

        # extract the input values from the form
        area = int(request.form['area'])
        bed = int(request.form['bed'])
        resale = int(request.form.get('resale'))

        vastu = int(request.form.get('vastu'))


        nearbylist=[]
        nearby = request.form.getlist('nearby')

        a=['gym', 'swim', 'land', 'jog', 'indo', 'mall', 'sport', '1atm', 'club', 'school', 'cafe', 'hosp', 'child']
        for i in range(0,13):
            if(a[i] in nearby):
                nearbylist.append('1')
            else:
                nearbylist.append("0")
        print(nearbylist)

        nearbystr = ''.join(nearbylist)
        nearbyint = int(nearbystr, 2)

        esslist=[]
        ess=request.form.getlist('ess')
        b=['pow','car','lift','sec','gas']
        for i in range(0,5):
            if(b[i] in ess):
                esslist.append('1')
            else:
                esslist.append("0")
        print(esslist)

        essstr = ''.join(esslist)
        essint = int(essstr, 2)

        location_str=(request.form['location'])
        from geopy.geocoders import Nominatim
        # Create a Nominatim geocoder object
        geolocator = Nominatim(user_agent="http")

        # Use geocoder to convert location string to latitude and longitude
        location = geolocator.geocode(location_str)

        if location is not None:
            latitude = location.latitude
            longitude = location.longitude
            latitude=float(latitude)
            longitude=float(longitude)

            ip=[area,latitude,longitude,bed,resale,vastu,nearbyint,essint]
            print(ip)
            global model
            pred=model.predict([ip]) 

            out=round(pred[0],4)
            pred_text="the PREDICTED price maybe:{} lakh".format(out)
        
        else:
            pred_text="Location not found"
        
        return render_template('main.html',prediction_text=pred_text,sub_title=subtitle)


    elif request.form.get('show') == 'show':
        print('a')
        global df
        global rdf

        f = float(request.form['from'])
        t = float(request.form['to'])
        d= request.form.get('rentorown')
        print(d)
        if(d=="1"):
            houses_in_range = rdf[(rdf['price'] >= f) & (rdf['price'] <= t)]
            locations = houses_in_range['locality'].tolist()
            locations=list(set(locations))
            # Check if there are any houses in the price range
            if houses_in_range.empty:
                print('d')
                return render_template('main.html', map_message='No houses in that range',sub_title=subtitle)
            else:
                # Create a map centered on the first house in the range
                map_center = [houses_in_range.iloc[0]['Latitude'], houses_in_range.iloc[0]['Longitude']]
                m = folium.Map(location=map_center, zoom_start=12)

                # loop through the filtered dataset and add markers to the map for each property
                for index, row in houses_in_range.iterrows():
                    # create a popup with the property information
                    popup = folium.Popup(
                        f"<b>Place:</b> {row['locality']}<br>"
                        f"<b>Price:</b> {row['price']} rupees/month<br>"
                        f"<b>No. of Bedrooms:</b> {row['bedroom']} <br>"
                        f"<b>No. of Bathrooms:</b> {row['bathroom']} <br>"
                        f"<b>Location:</b> {row['Latitude']}, {row['Longitude']}<br>"
                        f"<b>Seller Type:</b> {row['seller_type']}<br>"
                        f"<b>Layout Type:</b> {row['layout_type']}<br>",
                        max_width=300)
                    
                    tooltip=folium.Tooltip(
                        f"<b>Place:</b> {row['locality']}<br>"
                        f"<b>Area:</b> {row['area']} sqft<br>",
                    )
                    
                    # add a marker for the property
                    folium.Marker(
                        location=[row['Latitude'], row['Longitude']],
                        popup=popup,tooltip=tooltip,
                        icon=folium.Icon(color='blue', icon='home')).add_to(m)

                # Show the map
                fig2=Figure(width=540,height=350) #for he size of the map
                fig2.add_child(m)
                folium.TileLayer('Stamen Terrain').add_to(m)
                folium.TileLayer('Stamen Toner').add_to(m)
                folium.TileLayer('Stamen Water Color').add_to(m)
                folium.TileLayer('cartodbpositron').add_to(m)
                folium.TileLayer('cartodbdark_matter').add_to(m)
                folium.LayerControl().add_to(m)
        else:
            houses_in_range = df[(df['price'] >= f) & (df['price'] <= t)]
            locations = houses_in_range['Location'].tolist()
            locations=list(set(locations))
            # Check if there are any houses in the price range
            if houses_in_range.empty:
                print('d')
                return render_template('main.html', map_message='No houses in that range',sub_title=subtitle)
            else:
                # Create a map centered on the first house in the range
                map_center = [houses_in_range.iloc[0]['latitude'], houses_in_range.iloc[0]['longitude']]
                m = folium.Map(location=map_center, zoom_start=12)

                # loop through the filtered dataset and add markers to the map for each property
                for index, row in houses_in_range.iterrows():
                    # create a popup with the property information
                    popup = folium.Popup(
                        f"<b>Place:</b> {row['Location']}<br>"
                        f"<b>Area:</b> {row['Area']} sqft<br>"
                        f"<b>Price:</b> {row['price']} lakhs<br>"
                        f"<b>Location:</b> {row['latitude']}, {row['longitude']}<br>"
                        f"<b>No. of Bedrooms:</b> {row['No. of Bedrooms']}<br>"
                        f"<b>Resale:</b> {row['Resale']}<br>",
                        max_width=300)
                    
                    tooltip=folium.Tooltip(
                        f"<b>Place:</b> {row['Location']}<br>"
                        f"<b>Area:</b> {row['Area']} sqft<br>",
                    )
                    
                    # add a marker for the property
                    folium.Marker(
                        location=[row['latitude'], row['longitude']],
                        popup=popup,tooltip=tooltip,
                        icon=folium.Icon(color='blue', icon='home')).add_to(m)

                # Show the map
                fig2=Figure(width=540,height=350) #for he size of the map
                fig2.add_child(m)
                folium.TileLayer('Stamen Terrain').add_to(m)
                folium.TileLayer('Stamen Toner').add_to(m)
                folium.TileLayer('Stamen Water Color').add_to(m)
                folium.TileLayer('cartodbpositron').add_to(m)
                folium.TileLayer('cartodbdark_matter').add_to(m)
                folium.LayerControl().add_to(m)
        
        

        print('b')
        return render_template('main.html',my_map=m._repr_html_(),locations=locations,fromm=int(f),to=int(t),sub_title=subtitle)


    elif request.form.get('rpredict') == 'rpredict':

        # extract the input values from the form
        area = int(request.form['rarea'])
        bed = int(request.form['rbed'])
        bath = int(request.form['rbath'])
        sellertype = int(request.form.get('sellertype'))
        layouttype = int(request.form.get('layouttype'))
        propertytype = int(request.form.get('propertytype'))
        furnishtype = int(request.form.get('furnishtype'))
        location_str=(request.form['location'])
        from geopy.geocoders import Nominatim
        # Create a Nominatim geocoder object
        geolocator = Nominatim(user_agent="my_app")

        # Use geocoder to convert location string to latitude and longitude
        location = geolocator.geocode(location_str)

        if location is not None:
            latitude = location.latitude
            longitude = location.longitude
            latitude=float(latitude)
            longitude=float(longitude)

            ip=[sellertype, bed, layouttype, propertytype, area, furnishtype, bath, latitude, longitude]
            print(ip)
            global rmodel
            pred=rmodel.predict([ip]) 

            out=round(pred[0],4)
            rpred_text="the PREDICTED price maybe:{} rupees ".format(out)
        
        else:
            rpred_text="Location not found"
        
        return render_template('main.html',rprediction_text=rpred_text,sub_title=subtitle)





    


if __name__=="__main__":
    app.run(debug=True)
