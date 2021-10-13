from TwitterAPI import TwitterAPI, TwitterOAuth, TwitterRequestError, TwitterConnectionError, HydrateType, OAuthType
import json

#QUERY = '"pizza" OR "hamburguesa"'
#EXPANSIONS = 'author_id,referenced_tweets.id,referenced_tweets.id.author_id,in_reply_to_user_id,attachments.media_keys,attachments.poll_ids,geo.place_id,entities.mentions.username'
#TWEET_FIELDS = 'created_at,text'
#USER_FIELDS = 'created_at,name,profile_image_url,username'

def delete_rules(stream_rules, api):
    rules = [tweet['value'] for tweet in stream_rules]
    r = api.request('tweets/search/stream/rules', {'delete': {'values': rules}})
    print(f'[{r.status_code}] RULE DELETED: {json.dumps(r.json(), indent=2)}\n')


def stream_tweets(query, expansions, tweet_fields, user_fields):
    try:
        o = TwitterOAuth.read_file()
        api = TwitterAPI(o.consumer_key, o.consumer_secret, auth_type=OAuthType.OAUTH2, api_version='2')

        # GET STREAM RULES
        r = api.request('tweets/search/stream/rules', method_override='GET')
        print(f'[{r.status_code}] RULES: {json.dumps(r.json(), indent=2)}\n')
        if r.status_code != 200: exit()

        # DELETE STREAM RULES
        delete_rules(r, api)

        # ADD STREAM RULES
        r = api.request('tweets/search/stream/rules', {'add': [{'value': QUERY}]})
        print({'add': [{'value': QUERY}]})
        print(f'[{r.status_code}] RULE ADDED: {json.dumps(r.json(), indent=2)}\n')
        if r.status_code != 201: exit()

        # START STREAM
        r = api.request('tweets/search/stream', {
            'expansions': EXPANSIONS,
            'tweet.fields': TWEET_FIELDS,
            'user.fields': USER_FIELDS,
        },
                        hydrate_type=HydrateType.APPEND)

        print(f'[{r.status_code}] START...')
        if r.status_code != 200: exit()
        #CARGA EN DISCO

        #with open("dict_pais_puntajes.json", "w",encoding ="utf-8") as archivo:
            #json.dump(diccionario,  archivo, ensure_ascii=False)

        with open("database_tomas.json", "a", encoding ="utf-8") as db:
            x = 0
            for item in r:
                if x < 10:
                    created_at = item["data"]["created_at"]
                    text = item["data"]["text"]
                    username = item["data"]["author_id_hydrate"]["username"]
                    name = item["data"]["author_id_hydrate"]["name"]
                    id = str(item["data"]["id"])

                    dic = {id:{}}
                    dic[id].setdefault("created_at", created_at)
                    dic[id].setdefault("text", text)
                    dic[id].setdefault("username", username)
                    dic[id].setdefault("name", name)
                    x+=1
                else:
                    break

            json.dump(dic, db, ensure_ascii=False, indent=2)

                #print(json.dumps(item, indent=2))

    except KeyboardInterrupt:
        print('\nDone!')

    except TwitterRequestError as e:
        print(f'\n{e.status_code}')
        for msg in iter(e):
            print(msg)

    except TwitterConnectionError as e:
        print(e)

    except Exception as e:
        print(e)


QUERY = 'dogecoin'
EXPANSIONS = 'author_id'
TWEET_FIELDS = 'created_at,text'
USER_FIELDS = 'name,username'
r = stream_tweets(QUERY, EXPANSIONS, TWEET_FIELDS, USER_FIELDS)
