import instaloader
from instaloader import Instaloader, Profile
import pandas as pd
import requests
import sys

def _comp(a,b):
  if a == None:
    if b == None:
      return None
    else:
      return b['name'] # b['slug']
  else:
    return a.name # a.slug
  

def single_prof_scrapper(USER, PASSWORD, PROFILE, NUM_POSTS):

  # Create instance for scrapiing
  L = Instaloader()

  # Optionally, login or load session
  L.login(USER, PASSWORD) # (login)

  # Define the instagram profile to be scraped
  profile = Profile.from_username(L.context, PROFILE)

  # Basic profile information
  username = profile.username
  followers = profile.followers
  followees = profile.followees
  is_verified = profile.is_verified
  is_business = profile.is_business_account
  if (is_business):
    bus_cat = profile.business_category_name
  else:
    bus_cat = "N/A"

  # Start creating our dataset (this is called header as it is common for every folloowing picture)
  dataset_header = [username, followers, followees, is_verified, is_business, bus_cat]

  # Sort posts based on the number of likes + comments (could be changed)
  posts_sorted_by_likes = sorted(profile.get_posts(),
                                key=lambda p: p.likes + p.comments,
                                reverse=True)

  # Keep only image posts
  posts_no_videos = [post for post in posts_sorted_by_likes if post.is_video==False]

  # Keep the number of posts
  dataset_header = dataset_header + [len(posts_sorted_by_likes)]

  # Profile's Dataset
  dataset_prof = [dataset_header]*NUM_POSTS

  # Parse all images and extract information
  for i, post in enumerate(posts_no_videos[:NUM_POSTS]):

    # Extract post information
    url = post.url
    caption = post.caption
    hashtags = post.caption_hashtags
    likes = post.likes
    comments = post.comments
    location = _comp(post.location, post._node['location'])
    date_utc = post.date_utc
    img_type = post._node["__typename"]

    # Append post's informations to dataset
    dataset_prof[i] = dataset_prof[i] + [url, caption, hashtags, likes, comments, location, date_utc, img_type]

  return dataset_prof

def main():
  if len(sys.argv) != 5:
      print(f'Usage: {sys.argv[0]} <USER> <PASSWORD> <INSTA_PROFILE> <NUMBER_OF_POSTS>')
      return -1

  print("Hello..")

  USER = sys.argv[1]
  PASSWORD = sys.argv[2]
  PROFILE = sys.argv[3]   # profile to download from
  NUM_POSTS = int(sys.argv[4]) # number of posts to append to dataset

  data_prof = single_prof_scrapper(USER, PASSWORD, PROFILE, NUM_POSTS)

  headers = ['username', 'followers', 'followees', 'is_verified', 'is_business',
             'business_category', 'number_of_posts', 'post_url', 'caption', 'hashtags',
             'likes', 'comments', 'location', 'date_utc', 'img_type']

  df = pd.DataFrame(data=data_prof, columns=headers)
  df.to_csv(f'dataset_{PROFILE}.csv') 

  for i in range(len(df['post_url'])):

    image_url = df['post_url'][i] # Define the url for the image to be donwloaded
    image_name = df['username'][i]+ '_'+ str(df['date_utc'][i]).replace(" ", "_").replace(":","__") # Create an ID for the image's name <USERNAME_DATE-OF-POST>

    # Call this to download and save the image
    img_data = requests.get(image_url).content
    with open(f'{image_name}.jpg', 'wb') as handler:
        handler.write(img_data)

  return 0 


if __name__ == "__main__":
  main()





