import praw, OAuth2Util, time, re, locale



def Main():

    subname = 'photoshopbattles'
    username = '_korbendallas_'
    user_agent = '_korbendallas_ by /u/_korbendallas_ ver 0.1'
    wikiPage = ''
    interval = 30


    r = praw.Reddit(user_agent)
    o = OAuth2Util.praw.AuthenticatedReddit.login(r, disable_warning=True)

    searchHotComments(subname, r)
    
    #while True:
        
        #searchHotComments(subname, r)

        #time.sleep(interval*60)


    return


def searchHotComments(subname, r):

    try:
        
        sub = r.get_subreddit(subname)
        submissions = sub.get_hot(limit=5)

        for submission in submissions:
            submission.replace_more_comments(limit=None, threshold=0)
            comments = praw.helpers.flatten_tree(submission.comments)
            for comment in comments:
                if comment.author:
                    karma = int(comment.score)
                    if karma > 990 and comment.is_root and comment.banned_by == None:
                        auditFlair(comment, subname, r)

    except (Exception) as e:
        
        print e.message
        
        
    return


def auditFlair(comment, subname, r):

    try:

        karma = int(comment.score)
        user = comment.author.name
        flair = getFlair(user, subname, r)

        if flair == 'Error':
            return
        
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
        if flair == 'None' or 'standard' in flair:
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
        if karma < 1990:
            if '1000' in flair or '2000' in flair or '3000' in flair:
                return
            else:
                newFlairs.append('1000votes')
        #2K Wiki Edit
        elif karma > 1989 and karma < 2990:
            if '2000' in flair or '3000' in flair:
                return
            else:
                newFlairs.append('2000votes')
                updateWiki(subname, wikiPage, comment, '2000votes', r)
        #3K Wiki Edit
        elif karma > 2989 and karma < 3990:
            if '3000' in flair:
                return
            else:
                newFlairs.append('3000votes')
                updateWiki(subname, wikiPage, comment, '3000votes', r)
        #4K+ Message Mods
        elif karma > 3989:
            messageBody = 'Comment with 4000+ votes: \n\n'
            messageBody += comment.permalink
            r.send_message('/r/' + subname, 'Manual Flair Required', messageBody)
            return


        #Thanks
        if t in flair:
            newFlairs.append(t)

        #Format Flair Class
        newFlair = ''
        
        for element in newFlairs:
            newFlair += element + '-'
            
        newFlair = newFlair[:len(newFlair)-1]

        #Wrap up
        if '.flair-' + newFlair + '{' in stylesheet:
            setFlair(user, subname, newFlair, r)
        else:
            messageBody = 'New Flair Class: \n\n'
            messageBody += newFlair
            messageBody += '\n\n Entry: \n\n'
            messageBody += comment.permalink
            r.send_message('/r/' + subname, 'Manual Flair Required', messageBody)
            
        
    except (Exception) as e:
        
        print e.message

        
    return


def getFlair(user, subname, r):

    try:
        
        userFlair = r.get_flair(subname, username)
        return userFlair['flair_css_class']

    except (Exception) as e:
        
        print e.message

        
    return 'Error'


def setFlair(user, subname, flair, r):

    try:

        sub = r.get_subreddit(subname)
        sub.set_flair(username, '', flair)

    except (Exception) as e:
        
        print e.message
        
        
    return


def updateWiki(subname, wikiPage, comment, achievement, r):

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


        #Split wiki into three sections [everything above, relevant section, everything below]
        #section identifier
        sectionHeader = '######' + achievement[0] + 'k\r\n\r\n&#0160;\r\n\r\n| &#0160;&#0160;&#0160;&#0160; |   User  | Entry    |\r\n|:-----------:|:------------:|:------------:|\r\n'

        #above
        newWikiContents = wikiContents[:wikiContents.index(sectionHeader) + len(sectionHeader)]
        #section
        workingSectionTemp = wikiContents[wikiContents.index(sectionHeader) + len(sectionHeader):]
        workingSection = workingSectionTemp[:workingSectionTemp.index('\r\n\r\n&#0160;')]
        #below
        footer = workingSectionTemp[workingSectionTemp.index('\r\n\r\n&#0160;'):]

        #Split relevant section into rows and add the new row
        wikiRows = workingSection.split('\r\n')
        wikiRows.append(submissionRow)

        #Sort and append rows
        firstRow = True
        for wikiRow in sorted(wikiRows, cmp=locale.strcoll):
                if firstRow:
                        newWikiContents += wikiRow
                        firstRow = False
                newWikiContents += '\r\n' + wikiRow

        #Append footer
        newWikiContents += footer
        
        #Update Wiki
        wiki.edit(newWikiContents, 'Updated karma achievement.')
            
    except (Exception) as e:
        
        print e.message

    
    return


Main()

