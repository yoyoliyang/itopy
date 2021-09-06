from dotenv import dotenv_values
import os

class Config:
    """保存app配置类"""
    # 使用dotenv载入配置字典
    # 获取绝对路径方便pytest测试时引发的路径错误(pytest运行时的路径不同)导致无法载入.env文件
    envpath = '/'.join(os.path.abspath(__file__).split('/')[:-2] + ['config','.env'])
    print(envpath)
    db_config = dotenv_values(envpath)
    SQLALCHEMY_DB_URL =  f"mysql+pymysql://{db_config['DB_USER']}:{db_config['DB_PSWD']}@{db_config['DB_HOST']}:{db_config['DB_PORT']}/{db_config['DB_NAME']}?charset=utf8mb4" 
