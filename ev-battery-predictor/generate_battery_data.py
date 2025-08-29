#!/usr/bin/env python3
"""
Battery Data Generator - Creates realistic EV battery data with low noise
Generates 10,000+ samples with physically consistent patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_battery_data(num_samples=10000):
    """
    Generate realistic battery data with low noise patterns
    
    Physical relationships modeled:
    - SOH degrades with cycle count and time
    - Temperature affects internal resistance and voltage
    - SOC varies realistically based on usage patterns
    - Capacity fade increases with degradation
    - Internal resistance increases with age and temperature
    """
    
    print(f"Generating {num_samples} battery data samples...")
    
    data = []
    base_date = datetime(2022, 1, 1)
    
    # Battery aging simulation parameters
    initial_soh = 100.0
    initial_capacity = 75.0  # kWh
    initial_resistance = 0.02  # Ohms
    
    for i in range(num_samples):
        # Time progression (simulate 3+ years of data)
        days_elapsed = (i / num_samples) * 1200  # 3.3 years
        timestamp = base_date + timedelta(days=days_elapsed)
        
        # Cycle count increases over time with some variance
        cycle_count = int(days_elapsed * 0.8 + np.random.normal(0, 50))
        cycle_count = max(0, cycle_count)
        
        # SOH degradation model (realistic battery aging)
        # Combines linear aging and cyclic degradation
        age_factor = days_elapsed / 1000.0  # Age-based degradation
        cycle_factor = cycle_count / 2000.0  # Cycle-based degradation
        
        # More realistic SOH degradation curve (accelerates with age)
        soh_degradation = (
            5.0 * age_factor +                    # Linear aging (5% per ~3 years)
            8.0 * cycle_factor +                  # Cycle degradation
            2.0 * (age_factor ** 2) +             # Accelerated aging
            1.0 * (cycle_factor ** 2)             # Accelerated cycle wear
        )
        
        state_of_health = max(20.0, initial_soh - soh_degradation)
        
        # Capacity fade based on SOH
        capacity_fade = ((initial_soh - state_of_health) / initial_soh) * 100
        
        # Temperature variation (seasonal and daily patterns)
        season_temp = 20 + 15 * np.sin(2 * np.pi * (days_elapsed % 365) / 365)
        daily_variance = np.random.normal(0, 5)  # Daily temperature variation
        ambient_temp = season_temp + daily_variance
        
        # Operating temperature (higher during usage)
        usage_heating = np.random.uniform(0, 15)  # 0-15°C heating from use
        temperature = ambient_temp + usage_heating
        temperature = max(-20, min(60, temperature))  # Physical limits
        
        # State of charge (realistic usage patterns)
        # Simulate different charging behaviors
        if i % 20 == 0:  # Occasional full charge
            base_soc = np.random.uniform(85, 100)
        elif i % 5 == 0:  # Regular charging to ~80%
            base_soc = np.random.uniform(70, 90)
        else:  # Normal daily usage
            base_soc = np.random.uniform(20, 80)
        
        # Add small random variation
        state_of_charge = base_soc + np.random.normal(0, 2)
        state_of_charge = max(5, min(100, state_of_charge))
        
        # Voltage relationship (realistic battery chemistry)
        # Lithium-ion typical voltage curve
        soc_factor = state_of_charge / 100.0
        voltage_base = 3.2 + 0.6 * soc_factor  # 3.2V to 3.8V typical range
        
        # Temperature effect on voltage (cold reduces voltage)
        temp_effect = -0.002 * (20 - temperature)  # -2mV per degree below 20°C
        
        # SOH effect on voltage (degraded batteries have lower voltage)
        soh_effect = -0.1 * (100 - state_of_health) / 100
        
        voltage = voltage_base + temp_effect + soh_effect
        voltage += np.random.normal(0, 0.02)  # Small measurement noise
        voltage = max(2.5, min(4.2, voltage))  # Physical limits
        
        # Current (varies with usage and charging state)
        if state_of_charge > 95:  # Near full charge
            current = np.random.uniform(-0.5, 1.0)  # Light charging or standby
        elif state_of_charge < 20:  # Low charge, likely charging
            current = np.random.uniform(5, 25)      # Active charging
        else:  # Normal operation
            current = np.random.uniform(-10, 15)    # Discharge to charge
        
        current += np.random.normal(0, 0.5)  # Measurement noise
        
        # Internal resistance (increases with age and temperature)
        temp_resistance_factor = 1 + 0.01 * (temperature - 25)  # Higher at extremes
        age_resistance_factor = 1 + (100 - state_of_health) / 100  # Doubles at 50% SOH
        
        internal_resistance = (
            initial_resistance * 
            temp_resistance_factor * 
            age_resistance_factor
        )
        internal_resistance += np.random.normal(0, 0.002)  # Small noise
        internal_resistance = max(0.01, min(0.2, internal_resistance))
        
        # Data source simulation (realistic mix)
        data_sources = ['OBD', 'CAN', 'BMS', 'Sensor']
        data_source = np.random.choice(data_sources, p=[0.4, 0.3, 0.2, 0.1])
        
        # Create sample
        sample = {
            'measurement_timestamp': timestamp.isoformat(),
            'state_of_health': round(state_of_health, 2),
            'state_of_charge': round(state_of_charge, 2),
            'voltage': round(voltage, 3),
            'current': round(current, 2),
            'temperature': round(temperature, 1),
            'cycle_count': cycle_count,
            'capacity_fade': round(capacity_fade, 2),
            'internal_resistance': round(internal_resistance, 4),
            'data_source': data_source
        }
        
        data.append(sample)
        
        # Progress indicator
        if (i + 1) % 1000 == 0:
            print(f"Generated {i + 1} samples...")
    
    return pd.DataFrame(data)

def validate_data_quality(df):
    """Validate the generated data for consistency and realism"""
    print("\n=== Data Quality Validation ===")
    
    # Check basic statistics
    print(f"Total samples: {len(df)}")
    print(f"Date range: {df['measurement_timestamp'].min()} to {df['measurement_timestamp'].max()}")
    
    # Check SOH degradation pattern
    soh_trend = df['state_of_health'].rolling(100).mean()
    is_decreasing = (soh_trend.diff() <= 0.1).sum() / len(soh_trend.dropna())
    print(f"SOH degradation consistency: {is_decreasing:.2%}")
    
    # Check physical relationships
    high_temp_high_resistance = df[df['temperature'] > 40]['internal_resistance'].mean()
    low_temp_low_resistance = df[df['temperature'] < 10]['internal_resistance'].mean()
    print(f"Temperature-resistance relationship: {high_temp_high_resistance:.4f} vs {low_temp_low_resistance:.4f}")
    
    # Check for missing values
    missing_data = df.isnull().sum().sum()
    print(f"Missing values: {missing_data}")
    
    # Noise level analysis
    soh_noise = df['state_of_health'].diff().std()
    voltage_noise = df['voltage'].diff().std()
    print(f"SOH noise level (std of differences): {soh_noise:.3f}")
    print(f"Voltage noise level (std of differences): {voltage_noise:.3f}")
    
    return df

def main():
    """Main function to generate and save battery data"""
    print("🔋 Battery Data Generator v1.0")
    print("Creating realistic EV battery dataset with low noise...")
    
    # Generate data
    df = generate_battery_data(10000)
    
    # Validate data quality
    df = validate_data_quality(df)
    
    # Sort by timestamp
    df = df.sort_values('measurement_timestamp').reset_index(drop=True)
    
    # Save to CSV
    filename = f"battery_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    
    print(f"\n✅ Successfully generated {len(df)} samples")
    print(f"📁 Saved to: {filename}")
    print(f"📊 File size: {round(len(df) * df.memory_usage().sum() / 1024 / 1024, 2)} MB")
    
    # Show sample data
    print("\n📋 Sample data (first 5 rows):")
    print(df.head())
    
    print("\n📈 Summary statistics:")
    print(df[['state_of_health', 'state_of_charge', 'voltage', 'current', 'temperature']].describe())
    
    return filename

if __name__ == "__main__":
    filename = main()
    print(f"\n🎉 Battery data generation complete!")
    print(f"Use this file to train your ML models: {filename}")