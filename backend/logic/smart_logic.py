from backend.utils.helper import Smart_Helper

class Smart_Logic:
    #Master function
    def smart_fetch(data_path,sample_input):
        #Get Subset of the data
        subset = Smart_Helper.subset_data(sample_input,data_path)
        #Generate the weight
        table_weight = Smart_Helper.merge_input(sample_input,subset)
        #Get the smart data
        smart_df = Smart_Helper.process_data(table_weight)
        return smart_df
    
    def get_ingredient_str(data_path: str, col_name: str):
        #Get the list of all ingredients in the data
        ingredients = Smart_Helper.get_ingredients(data_path,col_name)
        return ingredients
    
    def json_vaildator_space(input_json):
        items_json = Smart_Helper.json_validator(input_json)
        return items_json
    
    def filter_json_by_list(input_json,comparison_list):
        #Get the filtered json
        filter_json = Smart_Helper.filter_json_by_list(input_json, comparison_list=comparison_list)
        return filter_json
    
