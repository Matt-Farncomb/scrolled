TODO
START OFF WITH A SIMPLE TEXT ZERO FOMRATTING
SITE THAT HAS MINIMUM FUONCTIONALITY.
FOCUS ALL EFFORT ON MAKING THE FUNCTIONALIT WORK AND ZERO PERCENNT
ON DESIGN.
LATER, maybe don't even add images. Just have
    a book shape (eg rectangle) all from CSS
    Keeping a super fast simple looking sight 
    could be cool. Imagine it is just two colors,
    writing and border is one color, when you hover over img,
    it will fade quckly to switch around.


1. Build a home page.
    a)A simple page showing a login section or a link to register
    b)A part of the page which shows nice info:
        i)top favourite book/s
        ii)top favourite author/s
        ((maybe)) iii)top favourite genre/s
        iv) all just images, no text (if possible)
2. Build a registration page.
    a) Users should be able to register 
    an account and provide the following:
        i)username - required
        ii)password - required
        The info below is not compulsory:
        iii)DOB
        iv)Country of Residence
        v)Favourite Book
        vi)Favourite Author
        ((maybe)) vii)Favourite Genre
3. Build the login functionality that is in the home page
    a)This will be a sperpate page that show their favourite books, authors and genres diplayed alongside matching images.    
4. Build the seach function.
    a)Search will be on the logged-in page. It does the following:
        i)seach by title, author, publication year, ((maybe)) genre
        and/or a combination.
            - I like the idea of this simply being one search bar 
                that ((maybe)) even suggests titles matching what you
                have typed as a suggestion in the bar. Eg, you type  1984 and it starts with the book called 1984, then next would list books released that year.
        ii)It will list the results of even incomplete words/dates.
        iii)Those results will be ordered by what is closest to the search.
        iv) If nothing comes up, eg there title is so far off anything else,
            then it will tell that nothing was found. ((below is a maybe)) 
            - I like the idea of this site almost never not having a result.
            - This could be achieved by doing a theasaurus search and
                then looking those theasarus words up in the database.
            - If the theasurus approach doesn't do anything (maybe its all numbers or a fake/very misplet word) do a google search and list
            the top few results saying "we don't have it, but does this help?"
            - ALso compare to dictionary somehow. So it looks the word up in
            a dictionary, poicks the first result and searches for that.
        v)The results will display the book cover image (somehow) with author, title and publication year beside it.
5. Build a book page.
    a)When the user clicks on a search result book, it takes them to a
    page with info about the book:
        i)title + book cover image (somehow)
        ii)author + image (somehow)
        iii)publication year + history fact about that year (somehow)
        iv)ISBN number
        v)reviews or "be first to review" thingy
        NOTE: The search results should already display i, i and iii.
        vi)AVG rating from this site and also avg rating from goodreads.
        v)Display number of reviews from both websites too
6. Build a review functionality into the book page.
    a)Users can't review the same book twice.
    b)Users can delete their review
    c)Users rate rate a title 1-3 stars.
        - 1 star = bad
        - 2 star = ok
        - 3 = great
    d) A small text-hover section near the stars where it would
        explain why I chose 3 stars.
    7. API shit. See cs50w website.
      