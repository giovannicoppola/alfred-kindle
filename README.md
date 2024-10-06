# alfred-eBooks📚


### List and open your Kindle and Apple Books ebooks with [Alfred 5](https://www.alfredapp.com/) 



<a href="https://github.com/giovannicoppola/alfred-kindle/releases/latest/">
<img alt="Downloads"
src="https://img.shields.io/github/downloads/giovannicoppola/alfred-kindle/total?color=purple&label=Downloads"><br/>
</a>

![](images/kindle.png)


<!-- MarkdownTOC autolink="true" bracket="round" depth="3" autoanchor="true" -->

- [Motivation](#motivation)
- [Setting up](#setting-up)
- [Basic Usage](#usage)
- [Known Issues](#known-issues)
- [Acknowledgments](#acknowledgments)
- [Changelog](#changelog)
- [Feedback](#feedback)

<!-- /MarkdownTOC -->



<h1 id="motivation">Motivation ✅</h1>

- Quickly list, search, and open your Kindle and Apple Books ebooks


<h1 id="setting-up">Setting up ⚙️</h1>

- Alfred 5 with Powerpack license
- Python3 (howto [here](https://www.freecodecamp.org/news/python-version-on-mac-update/))
- Kindle or Apple Books apps installed
- Download `alfred-eBooks` [latest release](https://github.com/giovannicoppola/alfred-kindle/releases/latest)



## Default settings 
- In Alfred, open the 'Configure Workflow' menu in `alfred-eBooks` preferences
	- set the keyword for the workflow (default: `!k`)
	- set the keyword to force an update (default: `::books-refresh`)
	- set the book content icon, i.e. if a book has been downloaded locally (default: 📘)
	- set the 'ghost' book icon, i.e. if a book has not been downloaded or previously loaned (default: 👻)
	- show 'ghost' books (i.e. books not downloaded, or previously loaned)? (default: yes)
	- set target library (Kindle, Apple Books, or both. Default: 'Both')

	_Note: `alfred-eBooks` will search for Kindle Classic and the (new) Kindle app. If both are installed, the latter with be used._
	- set search scope (default: 'Title')
		- `Title`: search titles only
		- `Author`: search authors only
		- `Both`: search across titles and authors


<h1 id="usage">Basic Usage 📖</h1>

- launch with keyword (default: `!k`), or custom hotkey
- enter a string to search, according to the scope set in `Workflow Configuration`. A few search operators are available:
	- `--p` will filter for purchased books
	- `--l` will filter for loaned books
	- `--d` will filter for downloaded books
	- `--k` will filter for Kindle books
	- `--ib` will filter for Apple Books books
	- `--read` will filter for read books
- `enter` ↩️ will open the book in Apple Books (if downloaded) or the corresponding webpage on Amazon (if not downloaded)
- data is automatically cached for best performance. You can force a database refresh using the keyword `::books-refresh`



<h1 id="known-issues">Limitations & known issues ⚠️</h1>

- I could not figure out how to open a specific book in the Kindle app via command line. If you know how to do that, let me know!
- I could not figure out how the Kindle app can tell if a book was first loaned, then purchased. Currently, if that is the case (i.e. a book was first loaned, then purchased), the book will appear as loaned.
- not tested thoroughly for user-uploaded documents.



<h1 id="acknowledgments">Acknowledgments 😀</h1>

- Thanks to the [Alfred forum](https://www.alfredforum.com) community!
- Icon from [SF symbols](https://developer.apple.com/sf-symbols/)

<h1 id="changelog">Changelog 🧰</h1>

- 10-07-2024: version 0.2: from kindle to eBooks
- 02-28-2023: version 0.1


<h1 id="feedback">Feedback 🧐</h1>

Feedback welcome! If you notice a bug, or have ideas for new features, please feel free to get in touch either here, or on the [Alfred](https://www.alfredforum.com) forum. 
