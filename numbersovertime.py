import pandas as pd
import re
import matplotlib.pyplot as plt

# Function to parse ATK and DEF buffs from the passive skill description
def parse_buffs(passive_text):
    if not isinstance(passive_text, str):  # Skip non-string values
        return 0, 0, 0, 0  # No buffs if passive skill is missing or invalid
    
    # Split the passive skill text by commas
    segments = passive_text.split(',')
    
    SoT_atk_buff_value = 0
    on_Super_atk_buff_value = 0
    SoT_def_buff_value = 0
    on_Super_def_buff_value = 0
    
    # Define on_Super patterns (e.g., after receiving, when performing super attack)
    on_Super_patterns = [
        r'after receiving', r'within the same turn', r'when performing a super attack',
        r'when attacking', r'when receiving', r'after performing a super attack', 
        r'after receiving damage'
    ]
    
    # Go through each segment and check if it contains ATK or DEF
    for segment in segments:
        segment = segment.strip()  # Clean any leading/trailing whitespace
        
        # If the segment mentions "ATK" and has no on_Super keyword, it's an SoT ATK buff
        if 'ATK' in segment.upper():  # Check if ATK is mentioned
            atk_buff = re.findall(r'(\+?\d+)%', segment)
            if atk_buff and not any(re.search(pattern, segment, re.IGNORECASE) for pattern in on_Super_patterns):
                SoT_atk_buff_value += int(atk_buff[0])
        
        # If the segment mentions "DEF" and has no on_Super keyword, it's an SoT DEF buff
        if 'DEF' in segment.upper():  # Check if DEF is mentioned
            def_buff = re.findall(r'(\+?\d+)%', segment)
            if def_buff and not any(re.search(pattern, segment, re.IGNORECASE) for pattern in on_Super_patterns):
                SoT_def_buff_value += int(def_buff[0])
        
        # If the segment contains on_Super keywords, treat it as on_Super buff
        if any(re.search(pattern, segment, re.IGNORECASE) for pattern in on_Super_patterns):
            if 'ATK' in segment.upper():
                atk_buff = re.findall(r'(\+?\d+)%', segment)
                if atk_buff:
                    on_Super_atk_buff_value += int(atk_buff[0])
            if 'DEF' in segment.upper():
                def_buff = re.findall(r'(\+?\d+)%', segment)
                if def_buff:
                    on_Super_def_buff_value += int(def_buff[0])
    
    return SoT_atk_buff_value, on_Super_atk_buff_value, SoT_def_buff_value, on_Super_def_buff_value

# Function to prepare the data with release date and parsed buffs
def prepare_data_for_ml(df):
    # Apply parsing function to the Passive Skill column
    df['SoT ATK Buff'], df['on_Super ATK Buff'], df['SoT DEF Buff'], df['on_Super DEF Buff'] = zip(*df['Passive Skill'].map(parse_buffs))
    
    # Convert the Release Date to datetime format (assuming it's in "Month Day, Year" format)
    df['Release Date'] = pd.to_datetime(df['Release Date'], format='%b %d, %Y', errors='coerce')
    
    # Sort the data by Release Date for mapping out the changes over time
    df.sort_values(by='Release Date', inplace=True)
    
    # Filter out rows where Release Date or buffs are NaN or invalid
    df = df.dropna(subset=['Release Date'])
    
    # Keep relevant columns: Release Date, SoT and on_Super Buffs for ATK and DEF
    df = df[['Release Date', 'SoT ATK Buff', 'on_Super ATK Buff', 'SoT DEF Buff', 'on_Super DEF Buff']]
    
    return df

# Function to plot trends over time
def plot_trends(df):
    # Group the data by Release Date to get the average buff values over time
    df_grouped = df.groupby('Release Date').mean()
    
    # Find the largest values for ATK and DEF buffs
    max_SoT_atk_buff = df_grouped['SoT ATK Buff'].max()
    max_on_Super_atk_buff = df_grouped['on_Super ATK Buff'].max()
    max_SoT_def_buff = df_grouped['SoT DEF Buff'].max()
    max_on_Super_def_buff = df_grouped['on_Super DEF Buff'].max()
    
    # Find the corresponding release dates for the largest values
    max_SoT_atk_date = df_grouped['SoT ATK Buff'].idxmax()
    max_on_Super_atk_date = df_grouped['on_Super ATK Buff'].idxmax()
    max_SoT_def_date = df_grouped['SoT DEF Buff'].idxmax()
    max_on_Super_def_date = df_grouped['on_Super DEF Buff'].idxmax()

    # Print the largest values for ATK and DEF buffs
    print(f"Largest SoT ATK Buff: {max_SoT_atk_buff}% (Released on {max_SoT_atk_date.date()})")
    print(f"Largest on_Super ATK Buff: {max_on_Super_atk_buff}% (Released on {max_on_Super_atk_date.date()})")
    print(f"Largest SoT DEF Buff: {max_SoT_def_buff}% (Released on {max_SoT_def_date.date()})")
    print(f"Largest on_Super DEF Buff: {max_on_Super_def_buff}% (Released on {max_on_Super_def_date.date()})")

    # Plotting the trends
    plt.figure(figsize=(10, 6))
    
    # Plot SoT ATK Buff trend
    plt.plot(df_grouped.index, df_grouped['SoT ATK Buff'], label='SoT ATK Buff', color='blue', marker='o')
    
    # Plot on_Super ATK Buff trend
    plt.plot(df_grouped.index, df_grouped['on_Super ATK Buff'], label='On Super ATK Buff', color='cyan', marker='x')
    
    # Plot SoT DEF Buff trend
    plt.plot(df_grouped.index, df_grouped['SoT DEF Buff'], label='SoT DEF Buff', color='green', marker='o')
    
    # Plot on_Super DEF Buff trend
    plt.plot(df_grouped.index, df_grouped['on_Super DEF Buff'], label='On Super DEF Buff', color='red', marker='x')
    
    # Adding labels and title
    plt.xlabel('Release Date')
    plt.ylabel('Buff Percentage')
    plt.title('Trends of ATK and DEF Buffs (SoT vs On Super) Over Time')
    plt.legend()
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    
    # Display the plot
    plt.tight_layout()
    plt.show()

# Example usage
# Load your dataset (update with the correct file path)
file_path = 'data_test1.csv'  # Update with actual file path
data = pd.read_csv(file_path)

# Prepare data for ML
processed_data = prepare_data_for_ml(data)

# Plot the trends
plot_trends(processed_data)
