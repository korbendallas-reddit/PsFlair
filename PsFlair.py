import praw, OAuth2Util, time, re


special_flairs = ['admin-thanks','adobe','bot','curt','damindrexil','danirama','deimorz','fbc',
    'fdh','gimp','hero','lains','LSUrockhound','mahatmagumby','mcfiesty','none',
    'pixelfuckers','psbvip','rps','taco','thanks','theskabus','totalitarian','workingat7']

special_people = ['2Thebreezes','8906','admancb','AlphaBoner','blue_awning','Captain_McFiesty',
    'Chispy','clintmccool','Cmatthewman','CptSasquatch','cupcake1713',
    'd_cb','Dacvak','DaminDrexil','Danirama','Deimorz',
    'dreamshoes','DrWankalot','facklestix','fatdonuthole','feith',
    'FOOKIN_LEGEND_M8','FueledByCoffee','FullNoodleFrontity','GallowBoob','give_the_lemons_back',
    'gnostic_cat','graphleek','hero0fwar','Hugojunior','JoshuaHaunted',
    'kpengin','lains-experiment','lumm0x','MahatmaGumby','milvus',
    'mocmocmoc81','MonotoneCreeper','MrFlopkins','olafpkyou','OnlyPhotoshopsPenis',
    'OrangeCladAssassin','PicturElements','pixelfuckers','PorkchopExprs','rawveggies',
    'ReeseLaserSpoon','RoyalPrinceSoldier','Shappie','Shosho99','sousvide',
    'Spankler','SplendidDevil','ssebonac','staffell','Suckassloser',
    'tacothecat','TheBlazingPhoenix','TheHongKongBong','theskabus','ThrobinWigwams',
    'totalitarian_jesus','ULTDbreadsticks','undercome','VilliThor','What_No_Cookie',
    'workingat7','zedextol']

old_file_path = 'user_flair_list_old.csv'
new_file_path = 'user_flair_list_new.csv'


subname = 'photoshopbattles'
wiki_page = 'flair/karmaqueue'
username = 'CHANGE THIS'
password = 'CHANGE THIS'
user_agent = 'CHANGE THIS'


def Main():

    global subname
    global username
    global password
    global user_agent


    r = praw.Reddit(user_agent)
    r.login(username, password, disable_warning=True)

    sub = r.get_subreddit(subname)
    flairs = getFlairList(r, sub)
    submissions = sub.get_top_from_month(limit=None)
    searchSubmissions(r, submissions, flairs)

    updateFlairs(r)


    return


def searchSubmissions(r, submissions, flairs):
    
    print('Searching Submissions')

    global subname
    global wiki_page
    global new_file_path
    
    try:

        f = open(new_file_path, 'w')
        f.write('')
        f.close()

        for submission in submissions:

            print(submission.title)
            print(submission.short_link)
            
            try:
                
                submission.replace_more_comments(limit=None, threshold=0)
                comments = praw.helpers.flatten_tree(submission.comments)
                
                if comments:
                    
                    for comment in comments:

                        try:
                        
                            if comment.author:
                                
                                karma = int(comment.score)
                                
                                if karma > 990 and comment.banned_by == None:

                                    linksCollector = re.compile('href="(.*?)"')
                                    links = linksCollector.findall(comment.body_html)

                                    if links:
                                        
                                        auditFlair(r, comment, flairs)

                        except (Exception) as e:
        
                            print(e)
                            
            except (Exception) as e:
        
                print(e)

    except (Exception) as e:
        
        print(e)
        
        
    return


def auditFlair(r, comment, flairs):

    global special_flairs
    global special_people
    global new_file_path
    
    print('Auditing User Flair: ' + comment.author.name + '  ' + str(comment.score))
    
    try:

        karma = int(comment.score)
        user = comment.author.name

        #Disregard Special People
        global special_people
        if user in special_people:
            print('Special person')
            return


        flair = ''

        for f in flairs:

            if user == f[0]:

                flair = f[1]

        #Disregard Special People
        if flair in special_flairs:
            print('Special person')
            return


        #Matrix for updated flair list
        new_flairs = []

        #First Flair
        if len(flair) < 1:
            new_flairs.append('standard')
        else:
            for flair_item in flair.split('-'):
                f = flair_item.strip('-').strip()
                if 'votes' not in f and 'thanks' not in f:
                    new_flairs.append(f)

        
        #Karma Achievements
            
        #1K
        if karma < 1990:
            
            if '1000votes' in flair or '2000votes' in flair or '3000votes' in flair or '4000votes' in flair or '5000votes' in flair or '6000votes' in flair:
                return
            else:
                new_flairs.append('1000votes')
                
        #2K Wiki Edit
        elif karma > 1989 and karma < 2990:
            
            if '2000votes' in flair or '3000votes' in flair or '4000votes' in flair or '5000votes' in flair or '6000votes' in flair:
                return
            else:
                new_flairs.append('2000votes')
                updateWiki(r, comment, '2000votes')
                
        #3K Wiki Edit
        elif karma > 2989 and karma < 3990:
            
            if '3000votes' in flair or '4000votes' in flair or '5000votes' in flair or '6000votes' in flair:
                return
            else:
                new_flairs.append('3000votes')
                updateWiki(r, comment, '3000votes')
                
        #4K+  = Message Mods
        elif karma > 3989:
            
            if '4000votes' in flair or '5000votes' in flair or '6000votes' in flair:
                return
            else:
                message_body = 'Comment with 4000+ votes: \n\n'
                message_body += comment.permalink
                r.send_message('/r/korbendallas', 'Manual Flair Required', message_body)
                updateWiki(r, comment, '4000votes')
                return
        

        #Thanks
        if 'thanks' in flair:
            new_flairs.append('thanks')
            
        
        #Wrap up
        f = open(new_file_path, 'a')
        f.write(user + ',' + flair + ',' + '-'.join(new_flairs) + '\n')
        f.close()            
        
    except (Exception) as e:
        
        print(e)

        
    return


def updateWiki(r, comment, achievement):
    
    print('Updating Wiki')

    global subname
    global wiki_page
    
    try:
        
        wiki = r.get_wiki_page(subname, wiki_page)
        wiki_contents = wiki.content_md

        new_wiki_contents = ''

        #Submission Title
        submission_title = 'Untitled'

        try:
            
            title_collector = re.compile('\[(.*?)\]')
            titles = title_collector.findall(comment.body)
            if titles:
                submission_title = str(titles[0])
                
        except (Exception) as e:
        
            print(e)


        #Format into MD table row
        submission_md = '[' + submission_title + '](' + comment.permalink[comment.permalink.find('/r/'):] + ')'
        submission_row = '![Flair](%%' + achievement + '%%) | /u/' + comment.author.name + ' | ' + submission_md


        wiki_rows = ['#Flair Queue']            
        
        if '\n' in wiki_contents:
            queue = wiki_contents.split('\n')
            for q in queue:
                q = q.strip('\r').strip('\n').strip()
                if len(q) > 15:
                    wiki_rows.append(q)

        wiki_rows.append(submission_row)
        

        new_wiki_contents += '\r\n\r\n'.join(wiki_rows) + '\r\n\r\n'

        wiki.edit(new_wiki_contents, 'New karma achievement.')

        print('Added: ' + submission_row)

        
            
    except (Exception) as e:
        
        print(e)

        
    return


def getFlairList(r, sub):

    global old_file_path

    flairs = []
        
    try:
            
        flairlist = r.get_flair_list(sub, limit=None)

        f = open(old_file_path, 'w')
        
        for flair in flairlist:
                
            flairs.append([flair['user'].strip(), flair['flair_css_class'].strip()])
            f.write(flair['user'].strip() + ',' + flair['flair_css_class'].strip() + '\n')

        f.close()

    except (Exception) as e:
        
        print(e)


    return flairs


def updateFlairs(r):
    
    print('Updating Flairs')

    global new_file_path
    global subname
    
    try:

        sub = r.get_subreddit(subname)

        f = open(new_file_path)

        flair_list = f.readlines()

        f.close()

        for flair_row in flair_list:
            
            flair_row = flair_row.strip('\r')
            flair_row = flair_row.strip('\n')

            if len(flair_row) > 2:

                if not flair_row.split(',')[1] == flair_row.split(',')[2]:
                
                    print(flair_row.split(',')[0] + ' --> ' + flair_row.split(',')[2])
                    sub.set_flair(flair_row.split(',')[0], '', flair_row.split(',')[2])

    except (Exception) as e:
        
        print(e)
        
        
    return




Main()
