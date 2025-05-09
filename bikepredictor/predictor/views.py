import joblib
import numpy as np
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import matplotlib.pyplot as plt
import seaborn as sns
import os, base64
from django.conf import settings
from io import BytesIO


# Load the trained model
model = joblib.load('predictor/model/bike_buyer_model.pkl')

# Your selected feature order
selected_features = [
    'Age', 'Income', 'Children', 'Cars', 'Married', 'Male', 'Masters',
    'Region_North America', 'Region_Pacific',
    'Occupation_Manual', 'Occupation_Professional', 'Occupation_Skilled Manual',
    'Commute Distance_1-2 Miles', 'Commute Distance_2-5 Miles',
    'Commute Distance_10+ Miles', 'Commute Distance_5-10 Miles'
]

@login_required
def predict_view(request):
    if request.method == 'POST':
        # Raw input from user
        Age = int(request.POST['age'])
        Income = int(request.POST['income'])
        Children = int(request.POST['children'])
        Cars = int(request.POST['cars'])
        Married = 1 if request.POST['married'] == 'yes' else 0
        Male = 1 if request.POST['gender'] == 'male' else 0
        Masters = 1 if request.POST['education'] == 'masters' else 0

        # One-hot encode manually
        Region = request.POST['region']
        region_columns = ['Region_North America', 'Region_Pacific']
        region_encoded = [1 if Region == col.split('_')[1] else 0 for col in region_columns]

        Occupation = request.POST['occupation']
        occupation_columns = ['Occupation_Manual', 'Occupation_Professional', 'Occupation_Skilled Manual']
        occupation_encoded = [1 if Occupation == col.split('_')[1] else 0 for col in occupation_columns]

        Commute = request.POST['commute']
        commute_columns = {
            'Commute Distance_1-2 Miles': '1-2 Miles',
            'Commute Distance_2-5 Miles': '2-5 Miles',
            'Commute Distance_5-10 Miles': '5-10 Miles',
            'Commute Distance_10+ Miles': '10+ Miles'
        }
        commute_encoded = [1 if Commute == label else 0 for label in commute_columns.values()]

        #final input
        final_input = [Age, Income, Children, Cars, Married, Male, Masters] + region_encoded + occupation_encoded + commute_encoded
        X = pd.DataFrame([final_input], columns=selected_features)

        #Predict
        prediction = model.predict(X)[0]

        return render(request, 'predictor/input.html', {'prediction': prediction})

    return render(request, 'predictor/input.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            return render(request, 'predictor/register.html', {'error': 'Username already exists'})

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('home')  # change to your home page name
    return render(request, 'predictor/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'predictor/login.html', {'error': 'Invalid credentials'})

    return render(request, 'predictor/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def home_view(request):
    return render(request, 'predictor/home.html')

@login_required
def dashboard(request):
    # Load your CSV file
    csv_path = os.path.join(os.path.dirname(__file__), 'model', 'training_data.csv')
    df = pd.read_csv(csv_path)

    # Generate chart (edit this as needed)
    plt.figure(figsize=(6, 4))
    sns.histplot(df['Income'])  # Example: 'Income' column
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    chart = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    # Context for the template
    context = {
        'record_count': len(df),
        'summary': df.describe().to_html(classes="table table-striped"),
        'chart': chart,
    }

    return render(request, 'predictor/dashboard.html', context)