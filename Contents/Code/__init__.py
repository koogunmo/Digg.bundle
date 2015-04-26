VIDEO_PREFIX = "/video/digg"

TITLE = L('Title')

ART  = 'art-default.jpg'
ICON = 'icon-default.png'

DIGG_TV_URL = 'http://digg.com/api/filter.json?source=youtube.com%2Cvimeo.com&tag=&position='

DIGG_POPULAR_URL = 'https://digg.com/api/video/popular.json?exclude_sponsored=true&count='
POPULAR_COUNT = 54;
TAGS = {
    'advertising': 'Advertising',
    'animals': 'Animals',
    'animation': 'Animation',
    'architecture': 'Architecture',
    'archive': 'Archive',
    'art': 'Art',
    'audio': 'Audio',
    'aviation': 'Aviation',
    'beliefs': 'Beliefs',
    'books': 'Books',
    'booze': 'Booze',
    'business': 'Business',
    'cars': 'Cars',
    'cities': 'Cities',
    'comics': 'Comics',
    'crime': 'Crime',
    'culture': 'Culture',
    'curious': 'Curious',
    'cute': 'Cute',
    'data-viz': 'Data Viz',
    'design': 'Design',
    'documentary': 'Documentary',
    'drugs': 'Drugs',
    'economics': 'Economics',
    'education': 'Education',
    'explainer': 'Explainer',
    'fame': 'Fame',
    'food': 'Food',
    'funny': 'Funny',
    'gaming': 'Gaming',
    'gender': 'Gender',
    'gross': 'Gross',
    'histories': 'Histories',
    'health': 'Health',
    'how-to': 'How-To',
    'human-nature': 'Human Nature',
    'internet': 'Internet',
    'language': 'Language',
    'late-night': 'Late Night',
    'law': 'Law',
    'lgbt': 'LGBT',
    'lust': 'Lust',
    'maps': 'Maps',
    'media': 'Media',
    'warfare': 'Warfare',
    'movies': 'Movies',
    'music': 'Music',
    'nature': 'Nature',
    'news': 'News',
    'originals': 'Originals',
    'photos': 'Photos',
    'politics': 'Politics',
    'race': 'Race',
    'science': 'Science',
    'short-film': 'Short Film',
    'space': 'Space',
    'sports': 'Sports',
    'studies': 'Studies',
    'style': 'Style',
    'technology': 'Technology',
    'trailers': 'Trailers',
    'tv': 'TV',
    'world': 'World',
    };
###################################################################################################
def Start():

    ObjectContainer.title1 = TITLE
    HTTP.CacheTime = 300

###################################################################################################
@handler('/video/digg', TITLE)
def MainMenu():

    oc = ObjectContainer()

    oc.add(DirectoryObject(key=Callback(LatestList, page=1), title="Latest Videos"))
    oc.add(DirectoryObject(key=Callback(Popular), title="Popular"));

    for key in sorted(TAGS):
        oc.add(DirectoryObject(key=Callback(CategoryList, page=1, tag=key), title=TAGS[key]));

    #oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.digg.", title="Search for Videos", prompt="Search Digg for...", term="Videos"))
    return oc

###################################################################################################
@route('/video/digg/latest/{page}', page=int, allow_sync=True)
def LatestList(page):

    oc = ObjectContainer(title2="Latest Videos")
    result = ScrapeVideos(page,None)
    keys = result.keys()
    keys.sort()

    for key in keys:
        oc.add(result[key])

    oc.add(NextPageObject(key=Callback(LatestList, page=page+1), title="More Videos..."))

    return oc

@route('/video/digg/{tag}/{page}', page=int, tag=str, allow_sync=True)
def CategoryList(page,tag):

    oc = ObjectContainer(title2=TAGS[tag])
    result = ScrapeVideos(page,tag)
    keys = result.keys()
    keys.sort()

    for key in keys:
        oc.add(result[key])

    oc.add(NextPageObject(key=Callback(CategoryList, page=page+1, tag=tag), title="More Videos..."))

    return oc

def ScrapeVideos(page, tag):

    result = {}

    @parallelize
    def GetVideos():
        pos = (page-1) * 10
        url = "http://digg.com/api/filter.json?source=youtube.com%2Cvimeo.com&pizza=2&position="
        url = '%s%d' % (url, pos)
        if tag is not None:
            url = '%s&tag=%s' % (url, tag)

        json = JSON.ObjectFromURL(url)
        videos = json['data']['feed'];

        for num in range(len(videos)):
            video = videos[num]

            @task
            def GetVideo(num=num, result=result, video=video):
                try:
                    embed_code = video['embed_code']
                    url = 'https:%s' % (HTML.ElementFromString(embed_code).get('src'))
                    video_object = URLService.MetadataObjectForURL(url)

                    if video_object is not None:
                        result[num] = video_object
                except:
                    pass
    return result

@route('/video/digg/popular', allow_sync=True)
def Popular():

    oc = ObjectContainer(title2="Popular")
    result = {}

    @parallelize
    def GetVideos():
        url = '%s%d' % (DIGG_POPULAR_URL, POPULAR_COUNT)

        json = JSON.ObjectFromURL(url)
        #Log.Error(json);
        videos = json['data']['feed'];
        #Log.Error(videos);
        for num in range(len(videos)):
            video = videos[num]
            @task
            def GetVideo(num=num, result=result, video=video):
                try:
                    embed_code = video['content']['embed_code']
                    Log.Error(embed_code);
                    url = 'https:%s' % (HTML.ElementFromString(embed_code).get('src'))
                    video_object = URLService.MetadataObjectForURL(url)

                    if video_object is not None:
                        result[num] = video_object
                except:
                    pass

    keys = result.keys()
    keys.sort()

    for key in keys:
        oc.add(result[key])

    return oc