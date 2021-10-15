from TwitterAPI import TwitterAPI, TwitterOAuth, TwitterRequestError, TwitterConnectionError, HydrateType, OAuthType
import credenciales
from datetime import datetime
import json 

class Tweet_Record:
    def __init__(self,API_KEY,API_SECRET_KEY):
        self.api = self._devolver_api(API_KEY,API_SECRET_KEY) 

    def _devolver_api(self,API_KEY,API_SECRET_KEY):
        try: api = TwitterAPI(API_KEY,API_SECRET_KEY, auth_type=OAuthType.OAUTH2, api_version='2') 
        except Exception as e: print(e)
        else: return api

    def get_rules(self):
        try:
            rules = self.api.request('tweets/search/stream/rules', method_override='GET') 
            print(f'[{rules.status_code}] RULES: {json.dumps(rules.json(), indent=2)}\n')
        except TwitterRequestError as e: 
            print(f'\n{e.status_code}')
            for msg in iter(e): print(msg)
        except TwitterConnectionError as e:print(e)
        except Exception as e: print(e)

    def add_rules(self,*rules):
        try:
            for rule in rules:
                request = self.api.request('tweets/search/stream/rules', {'add': [{'value':rule}]})
                print(f'[{request.status_code}] RULE ADDED: {json.dumps(request.json(), indent=2)}\n')
                if request.status_code != 201: exit() 
        
        except TwitterRequestError as e:
            print(f'\n{e.status_code}')
            for msg in iter(e):print(msg)
        except TwitterConnectionError as e:print(e)
        except Exception as e:print(e)
    
    def clear_rules(self):
        r = self.api.request('tweets/search/stream/rules', method_override='GET')
        print(f'[{r.status_code}] RULES: {json.dumps(r.json(), indent=2)}\n')
        values_list = [tweet['value'] for tweet in r]
        r = self.api.request('tweets/search/stream/rules', {'delete': {'values':values_list}})
        print(f'[{r.status_code}] RULE DELETED : {json.dumps(r.json(), indent=2)}\n')

    def stream_tweet(self,EXPANSIONS,TWEET_FIELDS,USER_FIELDS):
        try:
            r = self.api.request('tweets/search/stream', {
                    'expansions': EXPANSIONS,
                    'tweet.fields': TWEET_FIELDS,
                    'user.fields': USER_FIELDS,
                },
                hydrate_type=HydrateType.APPEND)
            print(f'[{r.status_code}] START...')
            if r.status_code != 200: exit()
            while(True): self.persistir_tweets(1,r)
        except KeyboardInterrupt:
            print('\nDone!')
        except TwitterRequestError as e:
           print(f'\n{e.status_code}')
           for msg in iter(e):print(msg)
        except TwitterConnectionError as e:
           print(e)
        except Exception as e:
           print(e)
        
    def persistir_tweets(self,cantidad_tweets,api_request):
        dicc_json = dict()
        tweets_recolectados = 0
        try:
            with open("tweets.json", "r",encoding="utf-8") as archivo_json:
                dicc_json = json.load(archivo_json)
        except FileNotFoundError:
            open("tweets.json", "w",encoding="utf-8")
        for tweet in api_request:

            id = str(tweet["data"]["id"])
            dicc_json[id] = {
                "created_at": tweet["data"]["created_at"],
                "name" : tweet["data"]["author_id_hydrate"]["name"],
                "username":tweet["data"]["author_id_hydrate"]["username"],
                "text" :tweet["data"]["text"]
                }

            tweets_recolectados += 1
            if (tweets_recolectados >= cantidad_tweets):break
            
        with open("tweets.json", "w",encoding="utf-8") as archvo_json:
            json.dump(dicc_json, archvo_json,indent=2, ensure_ascii = False)

if __name__ == "__main__":
    QUERY = 'dogecoin -is:retweet'
    EXPANSIONS = 'author_id'
    TWEET_FIELDS = 'created_at,text'
    USER_FIELDS = 'name,username'

    record = Tweet_Record(credenciales.API_KEY,credenciales.API_SECRET_KEY)
    record.clear_rules()
    record.add_rules(QUERY)
    record.stream_tweet(EXPANSIONS,TWEET_FIELDS,USER_FIELDS)
