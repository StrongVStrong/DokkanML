import pandas as pd
import re
import matplotlib.pyplot as plt

# Function to parse ATK and DEF buffs from the passive skill description
def parse_atk_def_buffs(passive_text):
    if not isinstance(passive_text, str):  # Skip non-string values
        return 0, 0  # No buffs if passive skill is missing or invalid
    
    # Split the passive skill text by commas
    segments = passive_text.split(',')
    
    atk_buff_value = 0
    def_buff_value = 0
    
    # Go through each segment and check if it contains ATK or DEF
    for segment in segments:
        segment = segment.strip()  # Clean any leading/trailing whitespace
        
        # Look for the percentage values related to ATK or DEF
        if 'ATK' in segment.upper():  # Check if ATK is mentioned
            atk_buff = re.findall(r'(\+?\d+)%', segment)
            if atk_buff:
                atk_buff_value += int(atk_buff[0]) / 100  # Convert percentage to decimal
        elif 'DEF' in segment.upper():  # Check if DEF is mentioned
            def_buff = re.findall(r'(\+?\d+)%', segment)
            if def_buff:
                def_buff_value += int(def_buff[0]) / 100  # Convert percentage to decimal
    
    return atk_buff_value, def_buff_value

# Function to prepare the data with release date and parsed buffs
def prepare_data_for_ml(df):
    # Apply parsing function to the Passive Skill column
    df['ATK Buff'], df['DEF Buff'] = zip(*df['Passive Skill'].map(parse_atk_def_buffs))
    
    # Convert the Release Date to datetime format (assuming it's in "Month Day, Year" format)
    df['Release Date'] = pd.to_datetime(df['Release Date'], format='%b %d, %Y', errors='coerce')
    
    # Sort the data by Release Date for mapping out the changes over time
    df.sort_values(by='Release Date', inplace=True)
    
    # Filter out rows where Release Date or buffs are NaN or invalid
    df = df.dropna(subset=['Release Date'])
    
    # Keep relevant columns: Name, Release Date, ATK Buff, DEF Buff
    df = df[['Release Date', 'ATK Buff', 'DEF Buff']]
    
    return df

# Function to plot trends over time
def plot_trends(df):
    # Group the data by Release Date to get the average buff values over time
    df_grouped = df.groupby('Release Date').mean()

    # Plotting the trends
    plt.figure(figsize=(10, 6))
    
    # Plot ATK Buff trend
    plt.plot(df_grouped.index, df_grouped['ATK Buff'], label='ATK Buff', color='blue', marker='o')
    
    # Plot DEF Buff trend
    plt.plot(df_grouped.index, df_grouped['DEF Buff'], label='DEF Buff', color='red', marker='x')
    
    # Adding labels and title
    plt.xlabel('Release Date')
    plt.ylabel('Buff Percentage')
    plt.title('Trends of ATK and DEF Buffs Over Time')
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
