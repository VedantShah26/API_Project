import requests
import json
import redis
import pandas as pd
import matplotlib.pyplot as plt

class NewspaperData:
    """
    A class to manage newspaper data from the Chronicling America API.

    Attributes:
        redis_client (redis.Redis): A Redis client object.
        data (dict): The newspaper data as a dictionary.
    """

    def __init__(self):
        """
        Initialize the NewspaperData class with a Redis client object.
        """
        self.redis_host = 'redis-18591.c326.us-east-1-3.ec2.cloud.redislabs.com'
        self.redis_port = 18591
        self.redis_db = 0
        self.redis_password = 'fUPiPzE8OmVRE0b6pdfnh95RLEDwO48y'
        self.redis_client = redis.Redis(host=self.redis_host, port=self.redis_port, db=self.redis_db, password=self.redis_password)
        self.data = None

    def fetch_data(self):
        """
        Fetch the newspaper data from the Chronicling America API and store it in Redis.

        This method sends a GET request to the Chronicling America API and retrieves the newspaper data as a JSON object.
        It then stores the data in Redis using the `set` method of the `redis_client` object. The data is stored under the key 'newspapers'
        with no expiration time (`ex=None`).

        Returns:
            None

        Raises:
            requests.exceptions.RequestException: if there is an error in sending the request to the API.
        """

        url = 'https://chroniclingamerica.loc.gov/newspapers.json'
        response = requests.get(url)
        response.raise_for_status()
        self.data = response.json()
        self.redis_client.set('newspapers', json.dumps(self.data), ex=None)
        print("Data successfully pushed into the redis server")
    
    def plot_top_20_states_with_most_newspapers(self):
        """
        Plot a bar chart of the top 20 states with the highest number of newspapers.

        The function first checks if the data is already fetched. If not, it fetches the data using the fetch_data method.
        Then, it creates a dictionary to count the number of newspapers in each state. After that, it sorts the state counts in descending order and selects the top 20 states.
        Finally, it plots a bar chart of the top 20 states with the highest number of newspapers.

        Returns:
        None
        """
        if self.data is None:
            self.fetch_data()

        state_counts = {}
        for newspaper in self.data['newspapers']:
            state = newspaper['state']
            if state not in state_counts:
                state_counts[state] = 0
            state_counts[state] += 1

        # Sort the state counts in descending order and get the top 20 states
        sorted_state_counts = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)
        top_20_states = sorted_state_counts[:20]

        plt.figure(figsize=(12, 6))

        # Plot the top 20 states
        states, counts = zip(*top_20_states)
        plt.bar(states, counts)
        plt.xlabel('States')
        plt.ylabel('Number of Newspapers')
        plt.title('Newspaper Distribution Across Top 20 States')
        plt.xticks(rotation=90)
        plt.show()

    def Newspaper_details(self):
        """
        Create a pandas DataFrame from the newspaper data.

        The function first checks if the data is already fetched. If not, it fetches the data using the fetch_data method.
        Then, it uses the pandas json_normalize function to create a DataFrame from the 'newspapers' data.

        Returns:
        pandas.DataFrame: A pandas DataFrame containing the newspaper details.
        """

        if self.data is None:
            self.fetch_data()
        
        df = pd.json_normalize(self.data['newspapers'])
        print(df.head())
        return df

    def count_unique_titles_per_state(newspaper_data):
        """
        Count the number of unique titles per state in the given newspaper data.

        Parameters:
        newspaper_data (NewspaperData): The newspaper data object containing the details of newspapers.

        Returns:
        dict: A dictionary where the keys are the states and the values are the number of unique titles in that state.
        """

        # Get the DataFrame of newspaper details
        newspaper_details_df = newspaper_data.Newspaper_details()

    # Create an empty dictionary to store the number of unique titles per state
        unique_titles_per_state = {}

        for state in newspaper_details_df['state'].unique():
            state_df = newspaper_details_df[newspaper_details_df['state'] == state]
            num_unique_titles = state_df['title'].nunique()
            unique_titles_per_state[state] = num_unique_titles
        print("Unique Titles per state")
        return unique_titles_per_state

    def find_title(self, title):
        """
        Find the state(s) where the given title exists (substring search).
        """
        df = self.Newspaper_details()

        if df is None or df.empty:
            print("DataFrame is empty.")
            return []

        states = df.loc[df['title'].str.contains(title, case=False), 'state'].values

        return states.tolist()

# Create a NewspaperData object
newspaper_data = NewspaperData()

# Fetch the data and plot the number of newspapers per state
newspaper_data.fetch_data()
newspaper_data.plot_top_20_states_with_most_newspapers()

print("converting the data into data frame and printing first 5 rows")

# newspaper_data.Newspaper_details()
print("Total records: ", len(newspaper_data.data['newspapers']))

unique_titles_per_state = newspaper_data.count_unique_titles_per_state()
print(unique_titles_per_state)

# Find the state(s) where a specific title exists
my_title = input("Enter the title you want to search for: ")

# Find the state(s) where the user-defined title exists
states = newspaper_data.find_title(my_title)
if states:
    print(f"Title found in states: {', '.join(states)}")
else:
    print("Title not found in any states.")