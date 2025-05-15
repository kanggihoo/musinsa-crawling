import _path_utils
import pandas as pd
df = pd.read_csv("musinsa_product_summary_final_.csv")

def convert_num_likes_to_number(num_str):
    num_str = num_str.strip() # 앞뒤 공백 제거
    if '만' in num_str and num_str[-1] == "만":
        value_str = num_str[:-1]
        try:
            value = int(float(value_str) * 10000)
        except ValueError:
            print(f"경고: '{num_str}'는 유효한 숫자 형식이 아닙니다.")
            return num_str
        return value
    elif '천' in num_str and num_str[-1]=="천":
        value_str = num_str[:-1]
        try:
            value = int(float(value_str) * 1000)
        except ValueError:
             print(f"경고: '{num_str}'는 유효한 숫자 형식이 아닙니다.")
             return num_str
        return value
    else:
        try:
            value = int(num_str)
        except ValueError:
             print(f"경고: '{num_str}'는 유효한 숫자 형식이 아닙니다.")
             return num_str
        return value
    
df["num_likes"].apply(convert_num_likes_to_number)
df["review_count"].apply(lambda x : x[1:-1] if isinstance(x , str) else x)