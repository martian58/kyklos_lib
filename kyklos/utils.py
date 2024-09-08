
class Utils:

    def get_allowed_symbols(file_path='allowed_symbols.txt'):
        try:
            # Open and read the file
            with open(file_path, 'r') as file:
                # Read all lines and strip any surrounding whitespace or newlines
                symbols = [line.strip() for line in file if line.strip()]
            
            return symbols
        
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []