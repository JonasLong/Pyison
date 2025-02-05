# Pyison

Pyison is a tarpit for AI webcrawlers

## Introduction
- Like all web crawlers, AI bots request pages from webservers, and then follow links on the page to other pages. By doing this, they can build an index of an entire website.
    - Unlike other web crawlers, though, AI bots present some unique issues
        - Server admins can configure a [robots.txt file](https://en.wikipedia.org/wiki/Robots.txt), which tells web crawlers what pages they should and shouldn't crawl.
            - Some AI crawlers have been found to ignore this file. There are privacy and copyright concerns with allowing these bots to use a website's data to train LLMs, especially when the user has explicitly opted out of crawling.
            - Some crawlers also ingore ratelimiting. When they request pages as fast as possible, they can put significant load on a webserver.
    - Enter Pyison. Like other AI crawler tarpits (Nepenthes, Iocane), Pyison feeds web crawlers an endless list of links to other pages on its site. This traps the crawlers on a single site, where they'll endlessly navigate an ever-growing sea of links.
        - Keeping AI crawlers stuck in one place prevents them from indexing other parts of the site that the owner might not want to feed to LLMs.
        - At the same time, these pages can contain tons of useless text. When LLMs incorporate this text into their models, they can gradually be "poisoned" as the random input will make their responses less coherent.
            
## Motivations
- Creating useful software to address the rise in LLM content thievery
- Solving problems in existing AI tarpits:
    - Generating random text without use of a Markov Chain, LLMs, or any existing writing samples
    - Not discriminating AI bots by User-Agent header, since crawlers will often disguise themselves as normal users
    - Designing a realistic blog-esque site in order to prevent detection
        - Creating an extremely customizable framework to allow further configuration
    - Providing a solution that can easily integrate into an existing website
        - Supports but doesn't require reverse proxies/specific webservers, provides sub-path configuration with a document root setting
    - Running with a small footprint rather than an entire CMS or feature-rich webserver
    
## Technical Specifications
- This project runs a dynamic web server using Python's HTTPServer library
- Sentences are produced from a 50/50 mix between random english words and "stop words"
- Pyison uses a global salt as well as a page url to seed its RNG. This ensures that if crawlers ever perform a "sanity check" by reloading a page, it will be the same as the last time they checked it. At the same time, different servers should use different global seeds so that not all sites using Pyison look the same.
- It's possible to generate an unlimited number of pages, since Pyison isn't actually creating any permanent files. It's a dynamic web server, so it just generates html and sends it to the client.
- Use of HTML content tags, CSS formatting, and images should make the site seem a bit more realistic to a crawler.
- It's possible to configure Pyison's output without rewriting the program, by changing the config, static, and template files
- Pyison responds to errant POST and PUT requests with a 404 in case crawlers test that those HTTP verbs are configured

## Getting Started
- Clone this project to a local folder
- Change settings in the `config/config.json` file
    - Set the `random-seed` to a random number!
    - Set the `port` number for the server to use
    - See the [Configuration](#configuration) section for more info
- (Optional but recommended) Update the HTML template, CSS, images, and robots.txt to your liking
    - This project is more effective if pages look different, which can be done by varying the HTML and CSS structure. Rearrange and rename some stuff, or rewrite it completely.
- (Optional) Edit the robots.txt if you want to change which bots are affected
- Set up the server environment with any of the methods below
- Put the server behind a [Reverse Proxy](#reverse-proxy)

  ### Running locally
    - Install nltk
        - `pip install nltk`
    - Run Pyison
        - `python3 src/server.py`
    - Check it's running
        - Open `http://localhost:<your port number>` in a browser

  ### Docker
  
    #### With docker compose
    - Make a bare-minimum [docker-compose.yml](docker-compose.yml) file containing
      ```yaml
      services:
        pyison:
          image: "ghcr.io/j0hnl0cke/pyison:main"
          container_name: pyison
          tty: true
          ports:
            - 80:80
       ```
    - `docker compose up`
      - (Optional) Use the `-d` flag to detach from the container
    - For changes to local files to have an effect, clone this repository and use a bind mount. See the [full compose file](docker-compose.yml).
    
    #### With docker run
    - `docker run --tty --name pyison -p "127.0.0.1:80:80" --rm ghcr.io/j0hnl0cke/pyison:main`
      - (Optional) Remove the `--rm` flag to persist the container
    
    #### Building from source
    - Clone the repository locally
    - `docker build -t pyison:latest .`
    - Run the container with `docker run --tty --name pyison -p "127.0.0.1:80:80" --rm pyison:latest`


## Reverse Proxy
  It is **highly recommended** that you use a reverse proxy to serve this content. It can reduce server load by caching pages and introducing ratelimits, as well as serve the content over https and protect from some basic webserver exploits.
    
  ### Considerations
  - These examples use Nginx Proxy Manager, but any reverse proxy software should work
  - Pyison supports NPM's strictest SSL settings
  - NPM *should* pass the `User-Agent` http header from NPM to the Pyison server without any special configuration. Use `proxy_pass_header User-Agent;` if needed.

  ### Independent Subdomain Configuration
  - Select the following settings in the UI, or enter the equivalent settings in the configuration file:
  
    <img src="docs/Proxy Host config.png" alt='The NGINX Reverse Proxy interface. The "Edit Proxy Host dialogue is open.' height="300"/>

      - Domain Names: A domain or subdomain you control, like `tarpit.example.com`
      - Scheme: `http`
      - Forward Hostname / IP: `localhost`, or the name of the docker container if using a docker network
      - Forward Port: Whatever port is defined in the docker-compose/run command/config.json (default is `80`)
      - Enable `Cache Assets` and `Block Common Exploits`, but not `Websockets Support`
  
  ### Sub-path Configuration
  - To use Pyison in a sub-path, use the following location configuration
  
      ```Nginx
      # Handles the root page ("example.com/tarpit")
      location /tarpit {
          proxy_pass http://localhost:80;
      }

      # Handles all sub-pages ("example.com/tarpit/a" and "example.com/tarpit/a/b")
      location /tarpit/ {
          proxy_pass http://pyison:80;
      }

      # Handles all urls with a 3-letter file extension ("example.com/tarpit/style.css" and "example.com/tarpit/images/picture.jpg")
      # Note that the ~ denotes regex matching. The string immediately following it must be a valid regex statement.
      location ~ .*\/tarpit\/.*\....$ {  
          proxy_pass http://localhost:80;
      }
      ```
  - Here is a working setup using the UI:
      
    <img src="docs/Proxy Host sub-path config.png" alt='The NGINX Reverse Proxy interface. The "Edit Proxy Host dialogue is open to the "Custom locations" tab.' height="400"/>
    
      - The first location block, `/tarpit`, has no custom configuration. It will behave like the first location block defined above.
      - The second location block, `/tarpit/`, contains the second and third location blocks defined above
    - Replace `tarpit` with the desired root path.
      - If using a deeper root path like `/tar/pit`, note that the third location block uses regex, so any slashes must be escaped with a backslash
        - eg: `/tar/pit` would require `location ~ .*\/tar\/pit\/.*\....$` in the 3rd location block
    - Update Pyison's `document-root` setting with the sub-path used by the proxy (see the [Configuration](#configuration) section)
    - See [above](#reverse-proxy) sections for further configuration of host, ports, SSL, etc

## Configuration
- The config.json file defines various settings for easy customization:
- `port` (default 80)
    - What port to serve content on
- `random-seed` (Please change this!)
    - Global seed (salt) used to make sure not every webserver has the exact same text
    - Set this to some random number, doesn't need to be secure
- `document-root` (default "/")
    - Prepends a path onto links
    - You'll only need to change this if you're using a reverse proxy and serving to a sub-directory
        - If so, use either a fully-qualified path or one relative to the root
            - ie `https://example.com/pyison/` or `/pyison/`
- `fake-image-dir` (default ["images"])
    - All images will appear to be served from this path
    - Accepts either a single string, null, or a list of options to randomly choose from
- `fake-css-dir` (default ["css"])
    - All css files will appear to be served from this path
    - Accepts either a single string, null, or a list of options to randomly choose from
- `spacing-characters` (default ["_","-","%20"])
    - Spaces to use between the words in a page URL
    - This will also affect how page URLs are split to decode back into titles
- `unsafe-characters` (default ["'","`"])
    - Characters that can occur naturally in the word list but should be removed from URLs
    - By default, this removes apostrophes (`) and single quotes (')
- `robots-txt` (default "assets/robots.txt")
    - This configures the file that gets served at `/robots.txt`
    - If the string is empty, a 404 response will be returned instead
- `html-templates` (default ["assets/template.html"])
    - HTML file to serve, containing format text to provide random values for (see HTML Templating)
    - Accepts either a single string, or a list of options to randomly choose from
- `css-files` (default ["assets/style.css"])
    - CSS file(s) to serve
    - No substitution is done on CSS files
    - Accepts either a single string, or a list of options to randomly choose from
- `images`
    - `ico` (default ["assets/logo.ico"])
    - `jpg` (default ["assets/logo.jpg"])
    - `png` (default["assets/logo.png"])
    - For each of the above image extensions: A single image file, null, or a list of images to pick randomly from
- `remove-from-stop-words`
    - The nltk library has a "stop words" list that's useful to generate lots of common words. However, some entries shouldn't be used for text generation because they're an obvious giveaway that this is generated content
    
## HTML Templating
- Before serving your HTML file(s), Pyison will substitue some preset tags with its own values
  ### Static values
    When one of these tags is specified multiple times in the template, each value will be the same
    - `{HOME}`
        - Link to the document root, as defined in the config
    - `{TITLE}`
        - Title text of the page, based on the current URL
            - ex '/blog/about/once-upon-a-time' -> 'Once Upon A Time'
    - `{UPTITLE}`
        - Title text of the parent page, generated from the current URL
    - `{MAIN}`
        - This should be used as the site's main content. It will generate several paragraphs containing random text, along with section headings and subheadings. Random links may also be present throughout each paragraph.
    - `{UP}`
        - Path to the parent page
        - eg: `/blog/about/once-upon-a-time` -> `/blog/about`
    - `{CSSLINK}`
        - Random URL to a CSS document
        - The beginning path of this URL (eg `/styles`) can be set in the config
        - Make sure to specify '.css' immediately after the tag. This is how the webserver knows to send css rather than more html.
            - The actual document returned by the server will be chosen based on the css page(s) specified in the config
  ### Dynamic values
  Each occurrence of these tags will be replaced by a unique value
    - `{WORD}`
        - Generates a single random word. Proper nouns may be capitalized.
    - `{NAME}`
        - Generates two capitalized words with a space in between.
    - `{SENTENCE}`
        - Generates a random sentence starting with a capital letter and ending with a period.
    - `{PIC}`
        - Generates a random URL to an image file
        - The beginning path of this URL (eg `/images`) can be set in the config
        - Make sure to put an appropriate file extension after the link (.png, .jpg, .ico)
            - The actual image returned by the server will be chosen based on the provided extension and the image(s) specified in the config
    - `{LINK}`
        - Generates a random link, which may contain sub-paths
        - The page name may be separated by dashes or underscores
        - eg: `/dressage/electrochronometer/himself-she-eciliate`
    - `{OVER}`
        - Generates a random link to a sibling page
        - eg: When visiting `/neighborliness/wont_unhonest`, an `{OVER}` tag  might be replaced with `/neighborliness/hooliganism`
    - `{NEWTITLE}`
        - Generates a random title
        - Uses a series of random words in Title Capitalization
        - eg: 'Nectarial Electrofusion Which Dephosphorization'
        - If this tag follows a `{LINK}` or `{OVER}` tag, the title and url will be synced
          - eg: `<a href="{OVER}">{NEWTITLE}</a>` might be replaced with `<a href="/swordmanship/yeller/over-will-oghuz">Over Will Oghuz</a>`
          - Tags are evaluated forwards through the template. A `{NEWTITLE}` tag will search backwards for the closest `{LINK}` or `{OVER}` tag to sync with.
            - Tags will always pair correctly when any `{LINK}` or `{OVER}` tag is immediately followed by its `{NEWTITLE}` tag, if a `{NEWTITLE}` is desired

## Images

<img src="docs/logo.png" alt="Pyison logo. A rectangular landscape-oriented image with a grainy gray background. Bright green text in a paintbrushed font with a dark red text shadow is centered in the top third of the image. It reads 'Pyison'. Near the bottom, stylized angular white text reads 'This is a tar pit for AI webcrawlers'. There is visible jpeg artifcating throughout the image upon closer inspection." height="200"/>
  
Here is a sample of how the site looks before any editing of the template:
   
<img src="docs/sample.png" alt="Zoomed out image of an entire Pyison page. It uses black text on a light yellow background. At the top of the page is a green navigation bar at the top with links containing random words. Below the nav bar is the title 'Home' and a logo image reading 'Pyison: This is a tar pit for AI webcrawlers'. Under the images is several paragraphs of random words with headings at various levels of indentation. These paragraphs takes up the majority of the page. Some of the text within the paragraphs are links to other pages. Near the bottom of the page, it has a fake author blurb with another Pyison logo. The blurb reads 'Written by It'S An'. Below that is an 'Other Posts' section, with several more links." height="500"/>
