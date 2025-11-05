I have a new plan, how about we refactor the extension to just map out all the folders and subfolders, this will give us a reading of the Udio user library structure. From there we can proceed to map out every song in the folder directory including its liked/disliked status, genre and any other useful information. With each song logged correctly we can do future runs to update the list and skip over songs that are already listed. Once we have the metadata for every song in the Udio user library we can begin downloading them. Additionally we will download the lyrics the song uses as an extra .txt file.



This method will be more comphrehensive and will account for bugs and delays in their website by allowing us to effectively scrape all user songs.

Ideally once all songs are scraped I'd also like to recreate a superior minimalistic version of the Udio UI but locally run so I can still navigate all my songs like before but initially we should just focus on the collection of song metadata and their download.