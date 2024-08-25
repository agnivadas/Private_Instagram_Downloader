
# Private_Instagram_Downloader
Graphical User Interface based script to batch download posts,reel,highlights,stories of PRIVATE or PUBLIC instagram accounts. *NO CREDENTIALS REQUIRED IN SCRIPT*.Fast download with multi thread download.

## Badges

[![GPL License](https://img.shields.io/badge/license-GPL-violet.svg)](http://www.gnu.org/licenses/gpl-3.0) [![Insta Private_Instagram_Downloader](https://img.shields.io/badge/source-GitHub-303030.svg?style=flat-square)](https://github.com/agnivadas/Private_Instagram_Downloader) ![Maintenance](https://img.shields.io/maintenance/yes/2024) ![Static Badge](https://img.shields.io/badge/contributions-welcome-blue)

## Requirements

Install Python Latest version then in command terminal paste the following for required libraries :

```bash
  pip install requests aiohttp asyncio urllib3 httpx
```
    
## Features

- Can use proxies
- .pyw extension used in the files to prevent appearing of console
- Multiple threads used in program for fast downloading . Then single thread download to cross check and download any remaining files.
- Previously downloaded files skipped automatically.


## Usage
**To download private account posts/stories/highlights , you need to follow the account .**

step 1: Copy the url of profile/post/highlight/stories

step 2 : Open `Instagram GraphQL generator.pyw` and paste the link . Then generate the GraphQL url. 
<img src="/assets/screenshot1.jpg" width="400px">

step3: Paste the GraphQL url in the browser where you are logged in , then Select all(Ctrl+A) and  Copy(Ctrl+C) the page source data .

<img src="/assets/screenshot2.jpg" width="300px">

step4: open `Instagram Downloader.pyw` and paste(Ctrl+v) the data then Start Scrapping .
<img src="/assets/screenshot3.jpg" width="400px">

step5: After completed download copy `generated url` and press `reset`, then paste in the broswer again to get rest source code and keep repeating process. When all pages are completed no generated url will be blank.
                               
<img src="/assets/screenshot4.jpg" width="400px">




## FAQ

If HTTP Error 403 during GraphQL link generation then use proxy or vpn.
Must `Reset` the program for next session.
Instagram GraphQL request fetch 12 posts of feed maximum at a time so process repeat is required to download all posts .For highlights downloading no repeat process is required.


## Disclaimer

Disclaimer: This is not affiliated, associated, authorized, endorsed by, or in any way officially connected with Instagram. The entire responsibility for the use of programs entirely on you.
