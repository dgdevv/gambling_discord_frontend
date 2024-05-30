import json, os

def read_json():
    # 현재 스크립트 파일의 절대 경로를 가져옵니다.
    dir_path = os.path.dirname(os.path.realpath(__file__))
    # 상위 디렉토리의 config.json 파일 경로를 구성합니다.
    config_path = os.path.join(dir_path, '..', 'config.json')
    # 파일을 열고 JSON 데이터를 로드합니다.
    with open(config_path, 'r') as file:
        data = json.load(file)
        result = [data['config']['guild_id'], data['config']['token']]
    return result
