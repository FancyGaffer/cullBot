#    Developer:  FancyGaffer
#    Date: June 23, 2020
#    Use:  To cull users from a subreddit who have been inactive for more than a week. 
#    Notes:  This will need revamping at some point, becuause there is a limit to how
#        many comments can be pulled from reddit (999).  Based on the size of the subs
#        this is meant to be used on, they are not active enough for this to present a 
#        problem.   Presupposes that each person has a unique individual flair.  

import praw
import time 
from datetime import datetime
homeSubreddit = 'Epine'


def main(): 
    #    Start by opening up reddit. 
    #reddit = (<Redacted Reddit password info>) 
    subreddit = reddit.subreddit(homeSubreddit)
    #    Get a list of all the users
    users = getUsers(subreddit)
    #    Get a list of everyone's flairs (and print it, just in case)
    flairDict = getFlairs(subreddit)
    #    Grab a list of active users. 
    active = activeUsers(reddit, subreddit, users)
    #    Yeet the ones who are inactive.   
    yeetInactive(reddit, subreddit, users, active,)
    #    Get a list of all the flairs of the remaining users. 
    oldFlair = setFlairs(subreddit, flairDict, active)
    return

#    Function:  getUsers
#    Arguments: subreddit 
#    Use:  Takes in a subreddit, and returns a list of all approved users of that subreddit. 
#        Usernames are standardized to all lowercase, for ease of later lookup. 
def getUsers(subreddit): 
    users = []
    for contributor in subreddit.contributor(limit=None): 
        users.append(contributor.name.lower())
    return users


#    Funciton: getFlairs
#    Arguments:  Subreddit
#    Use:  Takes in a subreddit, and returns a dictionary where the keys are the usernames
#        (all in lowercase, for ease of matching) and the values are the flairs.  This assumes
#        that the flairs are integers.  

def getFlairs(subreddit): 
    flairdict = {} 
    for flair in subreddit.flair(limit = None):
        user = str(flair['user'])
        lowerUser = user.lower() 
        flairtext = int(flair['flair_text'])
        flairdict[lowerUser] = flairtext
    return flairdict


#    Function:  Flairlist
#    Arguments:  Subreddit
#    Use:  Takes in a subreddit, and returns a list of the flairs in use in that 
#        subreddit (unattached to the users)
def flairList(subreddit): 
    flairlist = []
    for flair in subreddit.flair(limit = None):
        flairtext = int(flair['flair_text'])
        flairlist.append(flairtext)
    return flairlist


#    Funciton: getActive
#    Arguments: Subreddit
#    Use:  Takes in a subreddit, and returns a unique list of all active users of that subreddit
#        who have commented within the last week.  Note that the mechanism of this function
#        is likely to change in the future. 

#        In its current iteration, it takes the last 999 comments and combs through
#        that to find all active users.  In the future, it should go through all users,
#        and see when their last comment in the sub was made.  
# 
#        Also note that the hardcoding of the time (in seconds) should potentially be  
#        expanded to be more leniant, to allow for differences in times between culling.  
def getActiveComments(subreddit): 
    active = ['fancygaffer', 'vermilion-red', 'newaccttrial']
    # Grab our current time to compare it to the time the comment was made.
    seconds = time.time() 
    #    Get as many comments as we can (999), and if a comment is made in the last
    #    week, add the author to our list of active users.  Otherwise ignore it. 
    for comment in subreddit.comments(limit = None): 
        if(seconds - comment.created < 604800): 
            try: 
                active.append(comment.author.name.lower())
            except: 
                print("Error: " + comment.permalink)
        else: 
            pass
    #Deduplicate our list, to make it as short as possible. 
    activeList = list(set(active))
    return activeList

#    Function:  activeUsers
#    Arguments:  
#         reddit: self-explanatory.  Reddit handle. 
#         users: A list of all the users on the subreddit
#    Use:  Returns a list of all the users who posted on the subreddit in the last
#         week.  Note that this only trawls their last 999 comments, so if they made
#         500+ comments in the last week, this will run into problems.  That's a ridiculous
#         amount of comments, so tough cookies.  
def activeUsers(reddit, homeSubreddit, users):
    active = []
    seconds = time.time()
    for user in users: 
        for comment in reddit.redditor(user).comments.new(limit=500):
            if user not in active: 
                if(seconds - comment.created < 604800) and (comment.subreddit.display_name == homeSubreddit):
                    active.append(user)
                    print(user)
                else: 
                    pass
            else: 
                break
    return active

        

#    Function:  printStats
#    Arguments:  List of active users, inactive users, and all users
#    Use: Prints the number of active and inactive, and then a list of both categories. 
def printStats(active, inactive, users):
    print("Total Users: " + str(len(users)))
    print("Active Users: " + str(len(active)))
    print("Inactive users: " + str(len(inactive))) 
    print("Active: ")
    print(active) 
    print("Inactive: ")
    print(inactive)
    return

#    Function:  yeetInactive
#    Arguments: 
#        reddit:  Allows us to send messages
#        subreddit: Desired subreddit
#        users:  A list of users to potentially be culled. 
#        active:  A list of users who are active (And should not be culled)
#    User:  Goes through and removes all users who are not in active from the target subreddit, 
#        and sends a message to all members (culled and active) informing them of their new
#        status.  Prints the number of total, active, and inactive users. 
def yeetInactive(reddit, subreddit, users, active):
    inactive = []
    #    Go through our list of users, and see if they're in our active list.  If not, cull them. 
    for user in users: 
        if user not in active: 
            try: 
                inactive.append(user.lower())
                #subreddit.contributor.remove(user)
                #reddit.redditor(user).message("You have perished in the culling.", "Thank you for participating on r/Epine.  You have perished in the culling.", from_subreddit='Epine')
            except: 
                print("Error yeeting user: " + user)
        else: 
            #reddit.redditor(user).message("You have survived in the culling.", "Thank you for participating on r/Epine.  You have survived the culling.", from_subreddit='Epine')
            pass
    printStats(active, inactive, users)
    return

#    Function: setFliars
#    Arguments: 
#        subreddit: self-explanatory
#        flairDict: list of old flairs.  Assumed to contain ints. 
#        active:  List of active users. 
#    Use:  Takes in a subreddit, a dictionary of flairs, and a list of active users.  The active users are
#        ordered according to their old flair, and then assigned a new flair in the order of their old
#        flairs, starting at 1 and continuint. 
def setFlairs(subreddit, flairDict, active): 
    flairlist = []
    #    Start by making a list that holds all of our active users in a tuple, where the first value is their
    #    username (lowercase), and the second value is their flair. 
    for user in active: 
        if user in flairDict: 
            flairtext = int(flairDict[user])
            flairlist.append((user, flairtext))
        else: 
            print("Error:  Unflaired user " + user)
            flairtext = 10000
            flairlist.append((user, flairtext))
    #   Sort that list by the second value.  
    flairlist.sort(key=lambda x:x[1])
    print(flairlist)
    #   Assign flair to each user in the list, in order.

    maxFlair = 0
    #subreddit.flair.delete_all()
    for i in range(len(flairlist)): 
        newflair = str(i)
        user = flairlist[i][0]
        print(user + "," + newflair)
        maxFlair += 1
        #subreddit.flair.set(user, text = newflair)
    return maxFlair

main()