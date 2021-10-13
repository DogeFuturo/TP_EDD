from TwitterAPI import TwitterAPI, TwitterOAuth, TwitterRequestError, TwitterConnectionError, HydrateType, OAuthType
import json

QUERY = '"pizza" OR "hamburguesa"'
EXPANSIONS = 'author_id,referenced_tweets.id,referenced_tweets.id.author_id,in_reply_to_user_id,attachments.media_keys,attachments.poll_ids,geo.place_id,entities.mentions.username'
TWEET_FIELDS = 'author_id,conversation_id,created_at,entities,geo,id,lang,public_metrics,source,text'
USER_FIELDS = 'created_at,description,entities,location,name,profile_image_url,public_metrics,url,username'


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

        # START STREA
        r = api.request('tweets/search/stream', {
            'expansions': EXPANSIONS,
            'tweet.fields': TWEET_FIELDS,
            'user.fields': USER_FIELDS,
        },
                        hydrate_type=HydrateType.APPEND)

        print(f'[{r.status_code}] START...')
        if r.status_code != 200: exit()
        for item in r:
            print(json.dumps(item, indent=2))

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
EXPANSIONS = 'author_id,referenced_tweets.id,referenced_tweets.id.author_id,in_reply_to_user_id,attachments.media_keys,attachments.poll_ids,geo.place_id,entities.mentions.username'
TWEET_FIELDS = 'author_id,conversation_id,created_at,entities,geo,id,lang,public_metrics,source,text'
USER_FIELDS = 'created_at,description,entities,location,name,profile_image_url,public_metrics,url,username'
r = stream_tweets(QUERY, EXPANSIONS, TWEET_FIELDS, USER_FIELDS)
