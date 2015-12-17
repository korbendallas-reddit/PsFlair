import praw, OAuth2Util, time, re, locale



def Main():

    #--------------subname = 'photoshopbattles'
    subname = 'battleshop'#For testing
    username = '_korbendallas_'
    user_agent = '_korbendallas_ by /u/_korbendallas_ ver 0.1'
    wikiPage = 'flair/karmaqueue'
    interval = 30


    r = praw.Reddit(user_agent)
    o = OAuth2Util.praw.AuthenticatedReddit.login(r, disable_warning=True)

    searchHotComments(subname, wikiPage, r)#For testing
    
    #--------------while True:
        
        #--------------searchHotComments(subname, wikiPage, r)

        #--------------time.sleep(interval*60)


    return


def searchHotComments(subname, wikiPage, r):
    print 'auditing'#For testing
    try:
        
        sub = r.get_subreddit(subname)
        #--------------submissions = sub.get_hot(limit=5)
        submissions = sub.get_new(limit=20)#For testing

        for submission in submissions:
            
            try:
                
                submission.replace_more_comments(limit=None, threshold=0)
                comments = praw.helpers.flatten_tree(submission.comments)
                if comments:
                    for comment in comments:

                        try:
                        
                            if comment.author:
                                karma = int(comment.score)
                                #--------------if karma > 990 and comment.is_root and comment.banned_by == None:
                                if karma > 0 and comment.is_root and comment.banned_by == None:#For testing
                                    auditFlair(comment, subname, wikiPage, r)

                        except (Exception) as e:
        
                            print e.message
                            
            except (Exception) as e:
        
                print e.message

    except (Exception) as e:
        
        print e.message
        
        
    return


def auditFlair(comment, subname, wikiPage, r):
    print 'auditing flair'#For testing
    try:

        karma = int(comment.score)
        user = comment.author.name
        flair = getFlair(user, subname, r)
        
        if flair:
            if flair == 'Error':
                return
        else:
            flair = 'None'
        
        #Disregard Special People
        stylesheet = r.get_stylesheet(subname)
        
        if '.author[href$="/' + user + '"]' in stylesheet:
            return

        #Matrix for updated flair list
        newFlairs = []

        #Legend for shorthand
        b = 'battles'
        p = 'bestofpicks'
        w = 'bestofwins'
        f = 'featured'
        t = 'thanks'

        #First Flair
        if flair == 'None' or flair == None or 'standard' in flair:
            newFlairs.append('standard')
        
        #Battle Wins
        if b in flair:
            newFlairs.append(flair[flair.index(b)-1:flair.index(b)+len(b)])
        #Best of Picks
        if p in flair:
            newFlairs.append(flair[flair.index(p)-1:flair.index(p)+len(p)])
        #Best of Wins
        if w in flair:
            newFlairs.append(flair[flair.index(w)-1:flair.index(w)+len(w)])
        #Featured
        if f in flair:
            newFlairs.append(f)

        
        #Achievements
        #1K
        #--------------if karma < 1990:
        if karma == 1:#For testing
            if '1000' in flair or '2000' in flair or '3000' in flair or '4000' in flair or '5000' in flair or '6000' in flair:
                return
            else:
                newFlairs.append('1000votes')
        #2K Wiki Edit
        #--------------elif karma > 1989 and karma < 2990:
        elif karma == 2:#For testing
            if '2000' in flair or '3000' in flair or '4000' in flair or '5000' in flair or '6000' in flair:
                return
            else:
                newFlairs.append('2000votes')
                updateWiki2(subname, wikiPage, comment, '2000votes', r)
        #3K Wiki Edit
        #--------------elif karma > 2989 and karma < 3990:
        elif karma == 3:#For testing
            if '3000' in flair or '4000' in flair or '5000' in flair or '6000' in flair:
                return
            else:
                newFlairs.append('3000votes')
                updateWiki2(subname, wikiPage, comment, '3000votes', r)
        #4K+  = Message Mods
        #--------------elif karma > 3989:
        elif karma > 3:#For testing
            if '4000' in flair or '5000' in flair or '6000' in flair:
                return
            else:
                messageBody = 'Comment with 4000+ votes: \n\n'
                messageBody += comment.permalink
                #--------------r.send_message('/r/' + subname, 'Manual Flair Required', messageBody)
                r.send_message('/r/korbendallas', 'Manual Flair Required', messageBody)
                updateWiki2(subname, wikiPage, comment, '3000votes', r)
                print 'send'
                return
        

        #Thanks
        if t in flair:
            newFlairs.append(t)
        
        #Format Flair Class
        newFlair = ''
        
        for element in newFlairs:
            newFlair += element + '-'
            
        newFlair = newFlair[:len(newFlair)-1]
        print newFlair#For testing
        
        #Wrap up
        setFlair(user, subname, newFlair, r)
            
        
    except (Exception) as e:
        
        print e.message

        
    return


def getFlair(user, subname, r):
    print 'get flair'#For testing
    try:
        
        userFlair = r.get_flair(subname, user)
        return userFlair['flair_css_class']

    except (Exception) as e:
        
        print e.message

        
    return 'Error'


def setFlair(user, subname, flair, r):
    print 'set flair'#For testing
    try:

        sub = r.get_subreddit(subname)
        sub.set_flair(user, '', flair)

    except (Exception) as e:
        
        print e.message

    print 'flair updated'#For testing
        
        
    return


def updateWiki2(subname, wikiPage, comment, achievement, r):
    print 'update wiki'#For testing
    try:
        
        wiki = r.get_wiki_page(subname, wikiPage)
        wikiContents = wiki.content_md

        newWikiContents = ''

        #Submission Title
        submissionTitle = 'Untitled'

        try:
            
            titleCollector = re.compile('\[(.*?)\]')
            titles = titleCollector.findall(comment.body)
            if titles:
                submissionTitle = str(titles[0])
                
        except (Exception) as e:
        
            print e.message


        #Format into MD table row
        submissionMd = '[' + submissionTitle + '](' + comment.permalink + ')'
        submissionRow = '| ![Flair](%%' + achievement + '%%) | /u/' + comment.author.name + ' | ' + submissionMd


        wikiRows = []
        
        if '\n' in wikiContents:
            wikiRows = wikiContents.split('\n')
        else:
            wikiRows.append('#Flair Queue')

        
        wikiRows.append(submissionRow)

        for wikiRow in wikiRows:

            newWikiContents += wikiRow + '\n\n'

        

        wiki.edit(newWikiContents, 'New karma achievement.')   

        
            
    except (Exception) as e:
        
        print e.message

        
    return


Main()

