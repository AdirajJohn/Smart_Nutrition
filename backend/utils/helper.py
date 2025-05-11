import duckdb
import pandas as pd
import os

class Smart_Helper:

    #Function to create a subset of required dataset
    @staticmethod
    def subset_data(input_json,data_path):
        #Convert the Key into upper case
        input_json = dict((k.upper(),v) for k,v in input_json.items())
        #generate name of the foods to fetch from main data
        foods = (",".join(f"'{k.strip()}'" for k in input_json.keys()))
        #Get Subset table
        table=duckdb.sql(f"SELECT * FROM read_csv_auto('{data_path}') WHERE upper(trim(name)) in ({foods})")
        return table
    
    @staticmethod
    def merge_input(input_json,data):
        #Convert the Key into upper case
        input_json = dict((k.upper(),v) for k,v in input_json.items())
        #create a dataframe of the input json
        df_input = pd.DataFrame(list(input_json.items()),columns = ['name','quantity'])
        #Merge the input_json to the data
        merged_table = duckdb.sql("SELECT d.*,c.quantity FROM data AS d LEFT JOIN df_input c ON upper(trim(d.name))=upper(trim(c.name))")
        #Add Weight column
        table_weight = duckdb.sql("""SELECT *,(quantity/100) as weight FROM merged_table""")
        return table_weight
    

    @staticmethod
    def process_data(table_weight):
        # Identify numeric columns to multiply with weight
        cols_to_multiply = [col for col in table_weight.columns if col not in ['name', 'weight','quantity']]
        # Generate SQL expression: val1 * weight AS val1, ...
        multiplied_expr = ", ".join([f"({col} * weight) AS {col}" for col in cols_to_multiply])
        #Multiply the data with it's corresponding weights
        process_TB1 = duckdb.sql(f"""SELECT name, quantity,{multiplied_expr} FROM table_weight""")
        #Add Total row at the bottom
        cols_to_total = [col for col in process_TB1.columns if col not in ['name']]
        total_expr = ", ".join([f"SUM({col})" for col in cols_to_total])
        process_TB2=duckdb.sql(f"""
                SELECT * , 0 AS order_col
                FROM process_TB1 
                UNION
                SELECT
                'Total' AS Name,
                {total_expr},
                1 AS order_col FROM process_TB1 
                ORDER BY order_col""").df()
        #Drop the order_col column from the final data
        df_final = process_TB2.drop(axis=1,columns="order_col")
        return df_final
    
    @staticmethod
    def get_file_name(path):
        return os.path.basename(path)
    
    @staticmethod
    def get_ingredients(data_path: str,col_name: str) -> str:
        df = pd.read_csv(data_path)
        cols = list(df[col_name])
        #formatted_cols_str = "\n- " + "\n- ".join(cols).upper()
        ingredients_upper = [item.upper() for item in cols]
        return ingredients_upper
    
    @staticmethod
    def json_validator(input_json):
        nospace_json = {key.replace(" ", ""): value for key, value in input_json.items()}
        return nospace_json
    
    @staticmethod
    def filter_json_by_list(input_json, comparison_list):
        result = {}
        for key, value in input_json.items():
            if key in comparison_list:
                result[key] = value
        return result
