import sys
import pandas as pd
import re
from sqlalchemy import create_engine

def load_data(messages_filepath, categories_filepath):
    ''' 
    load data from csv files and merge into a single dataframe
    Input: 
    message_filepath: path to message data file
    categories_filepath : path to categories data file
    
    Returns:
    df : dataframe merging categories and messages
    '''
    
    # load messages dataset
    messages = pd.read_csv(messages_filepath)
    # load categories dataset
    categories = pd.read_csv(categories_filepath)
    # merge datasets
    df = messages.merge(categories, on = 'id')
    return df

def clean_data(df):
    ''' clean and convert data into appropriate datatype
    Input :
    df: Input dataframe
    Return: 
    df: dataframe that has been cleaned
    ''' 
    
    # create a dataframe of the 36 individual category columns
    categories = df['categories'].str.split(";", expand = True)
    # extract column name from 1st row of category df
    row = categories.iloc[0]
    category_colnames = row.apply(lambda x: re.sub(r'-[0-9]+',"", x))
    #rename categories df
    categories.columns = category_colnames
    # Convert category values to just numbers 0 or 1
    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].str.split("-").str[1]
        # convert column from string to numeric
        categories[column] = categories[column].apply(lambda x: 0 if x == '0' else 1).astype('int')
        # drop the original categories column from `df`
    df = df.drop(['categories'], axis = 1)
    # concatenate the original dataframe with the new `categories` dataframe
    df = pd.concat([df, categories], axis =1 ) 
    # remove duplicate
    df = df.drop_duplicates()
    return df



def save_data(df, database_filename):
    engine = create_engine('sqlite:///{}.db'.format(database_filename))  
    df.to_sql('message_table', engine, index=False)

def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()
