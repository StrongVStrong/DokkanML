import pandas as pd
import re
import matplotlib.pyplot as plt

# Function to parse ATK and DEF buffs from the passive skill description
def parse_buffs(passive_text):
    if not isinstance(passive_text, str):  # Skip non-string values
        return 0, 0, 0, 0  # No buffs if passive skill is missing or invalid
    
    # Split the passive skill text by commas
    segments = passive_text.split(',')
    
    initial_atk_buff_value = 0
    action_phase_atk_buff_value = 0
    initial_def_buff_value = 0
    action_phase_def_buff_value = 0
    
    # Define action phase patterns (e.g., after receiving, when performing super attack)
    action_phase_patterns = [
        r'after receiving', r'within the same turn', r'when performing a super attack',
        r'when attacking', r'when receiving', r'after performing a super attack', 
        r'after receiving damage'
    ]
    
    # Go through each segment and check if it contains ATK or DEF
    for segment in segments:
        segment = segment.strip()  # Clean any leading/trailing whitespace
        
        # If the segment mentions "ATK" and has no action phase keyword, it's an initial ATK buff
        if 'ATK' in segment.upper():  # Check if ATK is mentioned
            atk_buff = re.findall(r'(\+?\d+)%', segment)
            if atk_buff and not any(re.search(pattern, segment, re.IGNORECASE) for pattern in action_phase_patterns):
                initial_atk_buff_value += int(atk_buff[0]) / 100  # Convert percentage to decimal
        
        # If the segment mentions "DEF" and has no action phase keyword, it's an initial DEF buff
        if 'DEF' in segment.upper():  # Check if DEF is mentioned
            def_buff = re.findall(r'(\+?\d+)%', segment)
            if def_buff and not any(re.search(pattern, segment, re.IGNORECASE) for pattern in action_phase_patterns):
                initial_def_buff_value += int(def_buff[0]) / 100  # Convert percentage to decimal
        
        # If the segment contains action phase keywords, treat it as action phase buff
        if any(re.search(pattern, segment, re.IGNORECASE) for pattern in action_phase_patterns):
            if 'ATK' in segment.upper():
                atk_buff = re.findall(r'(\+?\d+)%', segment)
                if atk_buff:
                    action_phase_atk_buff_value += int(atk_buff[0]) / 100  # Convert percentage to decimal
            if 'DEF' in segment.upper():
                def_buff = re.findall(r'(\+?\d+)%', segment)
                if def_buff:
                    action_phase_def_buff_value += int(def_buff[0]) / 100  # Convert percentage to decimal
    
    return initial_atk_buff_value, action_phase_atk_buff_value, initial_def_buff_value, action_phase_def_buff_value

# Function to prepare the data with release date and parsed buffs
def prepare_data_for_ml(df):
    # Apply parsing function to the Passive Skill column
    df['Initial ATK Buff'], df['Action Phase ATK Buff'], df['Initial DEF Buff'], df['Action Phase DEF Buff'] = zip(*df['Passive Skill'].map(parse_buffs))
    
    # Convert the Release Date to datetime format (assuming it's in "Month Day, Year" format)
    df['Release Date'] = pd.to_datetime(df['Release Date'], format='%b %d, %Y', errors='coerce')
    
    # Sort the data by Release Date for mapping out the changes over time
    df.sort_values(by='Release Date', inplace=True)
    
    # Filter out rows where Release Date or buffs are NaN or invalid
    df = df.dropna(subset=['Release Date'])
    
    # Keep relevant columns: Release Date, Initial and Action Phase Buffs for ATK and DEF
    df = df[['Release Date', 'Initial ATK Buff', 'Action Phase ATK Buff', 'Initial DEF Buff', 'Action Phase DEF Buff']]
    
    return df

# Function to plot trends over time
def plot_trends(df):
    # Group the data by Release Date to get the average buff values over time
    df_grouped = df.groupby('Release Date').mean()

    # Plotting the trends
    plt.figure(figsize=(10, 6))
    
    # Plot Initial ATK Buff trend
    plt.plot(df_grouped.index, df_grouped['Initial ATK Buff'], label='Initial ATK Buff', color='blue', marker='o')
    
    # Plot Action Phase ATK Buff trend
    plt.plot(df_grouped.index, df_grouped['Action Phase ATK Buff'], label='Action Phase ATK Buff', color='cyan', marker='x')
    
    # Plot Initial DEF Buff trend
    plt.plot(df_grouped.index, df_grouped['Initial DEF Buff'], label='Initial DEF Buff', color='green', marker='o')
    
    # Plot Action Phase DEF Buff trend
    plt.plot(df_grouped.index, df_grouped['Action Phase DEF Buff'], label='Action Phase DEF Buff', color='red', marker='x')
    
    # Adding labels and title
    plt.xlabel('Release Date')
    plt.ylabel('Buff Percentage')
    plt.title('Trends of ATK and DEF Buffs (Initial vs Action Phase) Over Time')
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
