# fire weather index (FWI) calculation module
# formulas based on canadian FWI standards
# added vectorization for better performance
import pandas as pd
import p2_fwi as fwi
import numpy as np

def create_fwi_features(df):
    """Optimized FWI system calculations for dataset"""
    
    # Sort by timestamp first
    df = df.sort_values('timestamp')
    
    # Create copies of the arrays we'll need
    temperature = df['temperature'].values
    humidity = df['humidity'].values
    wind_speed = df['wind_speed'].values
    precipitation = df['precipitation'].values
    months = df['timestamp'].dt.month.values
    
    # Initialize FWI arrays with starting values
    n = len(df)
    ffmc = np.ones(n) * 85.0
    dmc = np.ones(n) * 6.0
    dc = np.ones(n) * 15.0
    
    # Calculate sequential indices using numpy operations
    for i in range(1, n):
        ffmc[i] = fwi.calculate_ffmc_vectorized(
            temperature[i], humidity[i], wind_speed[i], 
            precipitation[i], ffmc[i-1]
        )
        
        dmc[i] = fwi.calculate_dmc_vectorized(
            temperature[i], humidity[i], precipitation[i], 
            dmc[i-1], months[i]
        )
        
        dc[i] = fwi.calculate_dc_vectorized(
            temperature[i], precipitation[i], dc[i-1], months[i]
        )
    
    # Assign calculated values back to the DataFrame
    df['FFMC'] = ffmc
    df['DMC'] = dmc
    df['DC'] = dc
    
    # Calculate the remaining indices all at once (already vectorized)
    df['ISI'] = fwi.calculate_isi(df['FFMC'], df['wind_speed'])
    df['BUI'] = fwi.calculate_bui(df['DMC'], df['DC'])
    df['FWI'] = fwi.calculate_fwi(df['ISI'], df['BUI'])
    df['DSR'] = fwi.calculate_dsr(df['FWI'])
    
    return df

def prepare_data(env_data_path, fire_data_path):
   """preps environmental and fire data for modeling"""
   # load the env data first
   env_df = pd.read_csv(env_data_path)
   env_df['timestamp'] = pd.to_datetime(env_df['timestamp'])
   
   if fire_data_path:
       # merge in historical fire data if we have it
       fire_df = pd.read_csv(fire_data_path)
       fire_df['timestamp'] = pd.to_datetime(fire_df['timestamp'])
       
       # need unique id for each location-time combo
       env_df['location_time'] = env_df['timestamp'].dt.strftime('%Y-%m-%d %H:00:00') + '_' + \
                                env_df['latitude'].round(4).astype(str) + '_' + \
                                env_df['longitude'].round(4).astype(str)
       
       fire_df['location_time'] = fire_df['timestamp'].dt.strftime('%Y-%m-%d %H:00:00') + '_' + \
                                 fire_df['latitude'].round(4).astype(str) + '_' + \
                                 fire_df['longitude'].round(4).astype(str)
       
       # mark where fires happened
       fire_locations = fire_df[['location_time']].drop_duplicates()
       fire_locations['fire_occurred'] = 1
       
       # join it all together
       env_df = env_df.merge(fire_locations[['location_time', 'fire_occurred']], 
                            on='location_time', 
                            how='left')
       env_df['fire_occurred'] = env_df['fire_occurred'].fillna(0)
   
   # add the FWI system features
   env_df = create_fwi_features(env_df)
   
   return env_df