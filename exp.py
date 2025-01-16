import json

def process_json(file_path, key_to_find, update_key, update_value):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)

        if key_to_find not in data[0]: 
            print(f"Key '{key_to_find}' is missing in the JSON file.")
            return
        
        updated = False
        for donut in data:
            if donut["name"] == update_key:
                    donut['batters']['batter'].append(update_value)
                    updated = True
                    print(f"Added new batter to '{update_key}': {update_value}")
                    break
        
        if updated:
            with open('ex5_updated.json', 'w') as file:
                json.dump(data, file, indent=4)
            print("Updated JSON file created successfully.")
        else:
            print(f"No donut found with the name '{update_key}'.")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
    
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' is not a valid JSON.")
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

file_path = "ex5.json"  
key_to_find = "name"   
update_key = "Old Fashioned"  
update_value = {"id": "1005", "type": "Tea"}  
process_json(file_path, key_to_find, update_key, update_value)
