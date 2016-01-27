# -*- coding: cp1252 -*-
import praw, OAuth2Util, time, re, locale



def Main():

    subname = 'photoshopbattles'
    username = '_korbendallas_'
    user_agent = '_korbendallas_ by /u/_korbendallas_ ver 0.1'
    wiki_page = 'flair/karmaqueue'


    r = praw.Reddit(user_agent)
    o = OAuth2Util.praw.AuthenticatedReddit.login(r, disable_warning=True)

    sub = r.get_subreddit(subname)

    #Search Hot Of Today
    submissions = sub.get_hot(limit=20)
    searchSubmissions(submissions, subname, wiki_page, r)


    #Search Top Of The Week
    #submissions = sub.get_top_from_month(limit=50)
    #searchSubmissions(submissions, subname, wiki_page, r)


    return


def searchSubmissions(submissions, subname, wiki_page, r):
    
    print 'Searching Submissions'
    
    try:

        for submission in submissions:

            print submission.title
            print submission.short_link
            
            try:
                
                submission.replace_more_comments(limit=None, threshold=0)
                comments = praw.helpers.flatten_tree(submission.comments)
                
                if comments:
                    
                    for comment in comments:

                        try:
                        
                            if comment.author:
                                
                                karma = int(comment.score)
                                
                                if karma > 990 and comment.is_root and comment.banned_by == None:
                                    auditFlair(comment, subname, wiki_page, r)

                        except (Exception) as e:
        
                            print e
                            
            except (Exception) as e:
        
                print e

    except (Exception) as e:
        
        print e
        
        
    return


def auditFlair(comment, subname, wiki_page, r):
    
    print 'Auditing User Flair: ' + comment.author.name + '  ' + str(comment.score)
    
    try:

        karma = int(comment.score)
        user = comment.author.name

        #Disregard Special People
        global special_people
        if user in special_people:
            return


        flair = getFlair(user, subname, r)
        
        if flair:
            flair = flair.strip()
            if flair == 'Error' or flair == 'none' or flair == None:
                print 'Error getting current flair'
                return
            elif flair == 'None':
                flair = ''
            else:
                flair = ''
        else:
            flair = ''


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
                updateWiki(subname, wiki_page, comment, '2000votes', r)
                
        #3K Wiki Edit
        elif karma > 2989 and karma < 3990:
            
            if '3000votes' in flair or '4000votes' in flair or '5000votes' in flair or '6000votes' in flair:
                return
            else:
                new_flairs.append('3000votes')
                updateWiki(subname, wiki_page, comment, '3000votes', r)
                
        #4K+  = Message Mods
        elif karma > 3989:
            
            if '4000votes' in flair or '5000votes' in flair or '6000votes' in flair:
                return
            else:
                message_body = 'Comment with 4000+ votes: \n\n'
                message_body += comment.permalink
                r.send_message('/r/korbendallas', 'Manual Flair Required', message_body)
                updateWiki(subname, wiki_page, comment, '4000votes', r)
                return
        

        #Thanks
        if 'thanks' in flair:
            new_flairs.append('thanks')
            
        
        #Wrap up
        setFlair(user, subname, '-'.join(new_flairs), r)
        print 'set flair for ' + user + ':  ' + flair + ' --> ' + '-'.join(new_flairs)
            
        
    except (Exception) as e:
        
        print e

        
    return


def getFlair(user, subname, r):
    
    print 'Getting Flair'
    
    try:
        
        user_flair = r.get_flair(subname, user)
        
        return user_flair['flair_css_class']

    except (Exception) as e:
        
        print e

        
    return 'Error'


def setFlair(user, subname, flair, r):
    
    print 'Setting Flair'
    
    try:

        sub = r.get_subreddit(subname)
        sub.set_flair(user, '', flair)

    except (Exception) as e:
        
        print e
        
        
    return


def updateWiki(subname, wiki_page, comment, achievement, r):
    
    print 'Updating Wiki'
    
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
        
            print e


        #Format into MD table row
        submission_md = '[' + submission_title + '](' + comment.permalink + ')'
        submission_row = '| ![Flair](%%' + achievement + '%%) | /u/' + comment.author.name + ' | ' + submission_md


        wiki_rows = []
        
        if '\n' in wiki_contents:
            wiki_rows = wiki_contents.split('\r\n')
        else:
            wiki_rows.append('#Flair Queue')

        wiki_rows.append(submission_row)
        

        new_wiki_contents += '\r\n\r\n'.join(wiki_rows) + '\r\n\r\n'

        

        wiki.edit(new_wiki_contents, 'New karma achievement.')

        print 'Added: ' + submission_row

        
            
    except (Exception) as e:
        
        print e

        
    return


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


Main()

