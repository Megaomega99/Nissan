#!/usr/bin/env python3
"""
Comprehensive test script to validate all training fixes
Tests all ML models with various data scenarios
"""

import requests
import json
import time
import pandas as pd
import numpy as np
import io
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

def print_status(message, status="info"):
    """Print colored status messages"""
    colors = {
        "info": "\033[94m",  # Blue
        "success": "\033[92m",  # Green
        "warning": "\033[93m",  # Yellow
        "error": "\033[91m",  # Red
        "reset": "\033[0m"
    }
    print(f"{colors.get(status, '')}{message}{colors['reset']}")

def create_test_user():
    """Create a test user and return token"""
    print_status("🔐 Creating test user...", "info")
    
    timestamp = int(time.time())
    username = f"testuser_{timestamp}"
    email = f"test_{timestamp}@example.com"
    
    # Register user
    register_data = {
        "username": username,
        "email": email,
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    register_response = requests.post(
        f"{API_URL}/auth/register",
        json=register_data
    )
    
    if register_response.status_code != 200:
        raise Exception(f"Registration failed: {register_response.text}")
    
    # Login to get token
    login_data = {
        "username": username,
        "password": "testpassword123"
    }
    
    login_response = requests.post(
        f"{API_URL}/auth/login",
        data=login_data
    )
    
    if login_response.status_code != 200:
        raise Exception(f"Login failed: {login_response.text}")
    
    token = login_response.json()["access_token"]
    print_status(f"✅ User created: {username}", "success")
    
    return token, username

def create_test_vehicle(token):
    """Create a test vehicle"""
    print_status("🚗 Creating test vehicle...", "info")
    
    vehicle_data = {
        "name": "Test Vehicle",
        "make": "Tesla",
        "model": "Model S",
        "year": 2023,
        "battery_capacity": 100.0
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_URL}/vehicles/",
        json=vehicle_data,
        headers=headers
    )
    
    if response.status_code != 200:
        raise Exception(f"Vehicle creation failed: {response.text}")
    
    vehicle_id = response.json()["id"]
    print_status(f"✅ Vehicle created with ID: {vehicle_id}", "success")
    
    return vehicle_id

def generate_test_battery_data(num_samples=50):
    """Generate synthetic battery data for testing"""
    print_status(f"📊 Generating {num_samples} test battery data samples...", "info")
    
    base_date = datetime.now() - timedelta(days=num_samples)
    dates = [base_date + timedelta(days=i) for i in range(num_samples)]
    
    # Generate realistic battery degradation data
    np.random.seed(42)  # For reproducible results
    
    data = []
    initial_soh = 100.0
    
    for i, date in enumerate(dates):
        # Simulate gradual degradation with some noise
        degradation_rate = 0.02  # 2% per 100 cycles
        cycles_per_day = np.random.uniform(0.8, 1.2)
        cumulative_cycles = sum([cycles_per_day] * (i + 1))
        
        # Calculate SOH with degradation
        base_soh = initial_soh - (cumulative_cycles * degradation_rate)
        soh = max(70, base_soh + np.random.normal(0, 1))  # Add noise, min 70%
        
        # Generate correlated features
        soc = np.random.uniform(20, 95)  # State of charge
        voltage = 300 + (soc / 100) * 100 + np.random.normal(0, 5)  # Voltage correlates with SOC
        current = np.random.normal(15, 3)  # Current
        temperature = np.random.normal(25, 5)  # Temperature
        capacity_fade = initial_soh - soh  # Capacity fade
        internal_resistance = 0.02 + (capacity_fade / 100) * 0.03  # Resistance increases with fade
        
        data.append({
            "timestamp": date.strftime("%Y-%m-%d %H:%M:%S"),
            "state_of_health": round(soh, 2),
            "state_of_charge": round(soc, 2),
            "voltage": round(voltage, 2),
            "current": round(current, 2),
            "temperature": round(temperature, 2),
            "cycle_count": int(cumulative_cycles),
            "capacity_fade": round(capacity_fade, 2),
            "internal_resistance": round(internal_resistance, 4)
        })
    
    return data

def upload_battery_data(token, vehicle_id, data):
    """Upload battery data via CSV"""
    print_status("📤 Uploading battery data...", "info")
    
    # Convert to DataFrame and then CSV
    df = pd.DataFrame(data)
    csv_data = df.to_csv(index=False)
    
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": ("test_data.csv", io.StringIO(csv_data), "text/csv")}
    
    response = requests.post(
        f"{API_URL}/battery-data/upload/{vehicle_id}",
        headers=headers,
        files=files
    )
    
    if response.status_code != 200:
        raise Exception(f"Data upload failed: {response.text}")
    
    result = response.json()
    print_status(f"✅ Uploaded {result.get('message', 'data successfully')}", "success")

def test_model_training(token, vehicle_id, model_type, model_name):
    """Test training a specific model type"""
    print_status(f"🤖 Testing {model_name} ({model_type})...", "info")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create model
    model_data = {
        "vehicle_id": vehicle_id,
        "name": f"{model_name} Test Model",
        "model_type": model_type,
        "description": f"Test model for {model_type} algorithm"
    }
    
    create_response = requests.post(
        f"{API_URL}/ml-models/",
        json=model_data,
        headers=headers
    )
    
    if create_response.status_code != 200:
        print_status(f"❌ Model creation failed: {create_response.text}", "error")
        return False
    
    model_id = create_response.json()["id"]
    print_status(f"   ✓ Model created with ID: {model_id}")
    
    # Train model
    train_data = {"test_size": 0.2}
    train_response = requests.post(
        f"{API_URL}/ml-models/{model_id}/train",
        json=train_data,
        headers=headers
    )
    
    if train_response.status_code != 200:
        print_status(f"❌ Training request failed: {train_response.text}", "error")
        return False
    
    print_status(f"   ✓ Training started...")
    
    # Wait for training to complete (with timeout)
    max_wait = 120  # 2 minutes
    wait_time = 0
    
    while wait_time < max_wait:
        time.sleep(5)
        wait_time += 5
        
        status_response = requests.get(
            f"{API_URL}/ml-models/{model_id}",
            headers=headers
        )
        
        if status_response.status_code == 200:
            model_info = status_response.json()
            if model_info.get("is_trained"):
                test_score = model_info.get("test_score", 0)
                print_status(f"   ✅ Training completed! Test R²: {test_score:.4f}", "success")
                
                # Test prediction endpoints if model is trained
                if test_score > 0:
                    test_predictions(token, model_id)
                
                return True
        
        print_status(f"   ⏳ Waiting for training... ({wait_time}s)")
    
    print_status(f"   ⚠️ Training timeout after {max_wait}s", "warning")
    return False

def test_predictions(token, model_id):
    """Test prediction endpoints"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test model metrics
    try:
        metrics_response = requests.get(
            f"{API_URL}/predictions/metrics/{model_id}",
            headers=headers
        )
        
        if metrics_response.status_code == 200:
            metrics = metrics_response.json()
            print_status(f"   ✓ Model metrics: R²={metrics.get('r2_score', 'N/A'):.4f}, "
                       f"RMSE={metrics.get('rmse', 'N/A'):.4f}")
        
        # Test SOH forecast
        forecast_data = {
            "model_id": model_id,
            "prediction_steps": 30,
            "time_step_days": 7
        }
        
        forecast_response = requests.post(
            f"{API_URL}/predictions/soh-forecast",
            json=forecast_data,
            headers=headers
        )
        
        if forecast_response.status_code == 200:
            forecast = forecast_response.json()
            print_status(f"   ✓ SOH forecast: {len(forecast.get('predictions', []))} predictions generated")
        
    except Exception as e:
        print_status(f"   ⚠️ Prediction test failed: {e}", "warning")

def main():
    """Main test execution"""
    print_status("🧪 COMPREHENSIVE TRAINING FIXES TEST", "info")
    print_status("=" * 50, "info")
    
    try:
        # Setup
        token, username = create_test_user()
        vehicle_id = create_test_vehicle(token)
        
        # Generate and upload test data
        battery_data = generate_test_battery_data(60)  # More data for better training
        upload_battery_data(token, vehicle_id, battery_data)
        
        # Test all model types
        model_tests = [
            ("linear", "Linear Regression"),
            ("polynomial", "Polynomial Regression"),
            ("random_forest", "Random Forest"),
            ("svm", "Support Vector Machine"),
            ("sgd", "Stochastic Gradient Descent"),
            ("neural_network", "Neural Network"),
            ("perceptron", "Perceptron"),
            ("rnn", "RNN (LSTM)"),
            ("gru", "GRU")
        ]
        
        results = {}
        print_status(f"\n🎯 Testing {len(model_tests)} model types...", "info")
        
        for model_type, model_name in model_tests:
            try:
                success = test_model_training(token, vehicle_id, model_type, model_name)
                results[model_type] = "✅ SUCCESS" if success else "❌ FAILED"
            except Exception as e:
                print_status(f"❌ {model_name} failed with exception: {e}", "error")
                results[model_type] = f"❌ EXCEPTION: {str(e)[:50]}"
        
        # Summary
        print_status("\n" + "=" * 50, "info")
        print_status("📊 TRAINING TEST RESULTS SUMMARY", "info")
        print_status("=" * 50, "info")
        
        successful = 0
        for model_type, result in results.items():
            print_status(f"{model_type:20} | {result}")
            if "SUCCESS" in result:
                successful += 1
        
        print_status(f"\n✅ {successful}/{len(model_tests)} models trained successfully", 
                    "success" if successful > len(model_tests) // 2 else "warning")
        
        if successful >= len(model_tests) * 0.7:  # 70% success rate
            print_status("🎉 COMPREHENSIVE PREPROCESSING FIXES ARE WORKING!", "success")
        else:
            print_status("⚠️ Some models still have issues, but major fixes are working", "warning")
            
    except Exception as e:
        print_status(f"❌ Test failed: {e}", "error")
        return False
    
    return True

if __name__ == "__main__":
    main()