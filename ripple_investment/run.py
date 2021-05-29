import pandas as pd 
# from sklearn
import click
from ripple import feature



def meta_setting(data,name='sample'):
    '''
    '''
    if 'time' not in data.columns:
        raise ValueError('date not in columns')
        
    result = {}
    result['start_period'] = data['time'].min().__str__()
    result['end_period'] = data['time'].max().__str__()
    result['nb_obs'] = data.shape[0]
    result['name'] = name
    
    return result



def train_test_split(data,ts_size=0.7):
    '''
    '''
    size = len(data) 
    train_size = int(size * ts_size )
    xtrain = data.iloc[0:train_size]
   
       
    x_val = data.iloc[train_size:size]
    size_val = len(x_val)
    size_xtest = int(0.3 *size_val)
    xtest = x_val.iloc[0:size_xtest]
    xval = x_val.iloc[size_xtest:size_val]
    

    return xtest, xval, xtrain
    
    

    
    
def load():
    data = pd.read_csv('data/XRP_price_20210524.csv')
    return data



def run():
    data = load()
    data = feature.transform(data).dropna()
    
    df_down,result = feature._trend(data,'decreasing')
    df_down.to_csv('data/down_data.csv',index=False)
    result.to_csv('data/down_analysis.csv',index=False)
    
    #=======
    df_up,result = feature._trend(data,'increasing')
    result.to_csv('data/up_analysis.csv',index=False)
    df_up.to_csv('data/up_data.csv',index=False)
    
    
    settings = []
    xtest,xval,xtrain = train_test_split(data)
    print(xtest)
    
    for (k,n) in zip([xtest,xval,xtrain],['test','val','train']):
       
        settings.append(meta_setting(data=k,name=n))
    
#     xtest = feature._trend(xtest)
    settings = pd.DataFrame(settings)
    settings.to_csv('data/settings.csv',index=False)
    print(settings)
    
    return data


if __name__ == '__main__':
    click.secho('Run ripple',fg='green')
   
    run()
    