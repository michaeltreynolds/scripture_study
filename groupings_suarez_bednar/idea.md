I have been invited to do the following:

I’ve made lists of what the Book of Mormon is, what it affirms, what it refutes, what it fulfills, what it clarifies, and what it reveals. Looking at the Book of Mormon through these lenses has been an insightful and inspiring exercise! I recommend it to each of you.”

OK we have a virtual env ..\.venv we have python and we have access to openai embeddings via APIs (moved to .env)

Here is the idea we have these categories:
what it affirms generally. Significant items like "God knows us by name" or "we are children of god" or "We lived in heaven before we came to earth".

what it refutes of false beliefs of people today.
what it fulfills of prophecies made in the old testament.
what it clarifies about the teachings of Jesus that are less clear in the old and new testament
and what it reveals that we otherwise would not have known that is valuable to know about mankind generally or God or the kingdom of heaven.

Honestly I think I'd want to send a chat prompt to each for each of these. I'd prefer to use my google ultra subscription that I have, but could use opeanai if that subscription doesn't really provide any way to do this.

The prompt is important it needs to allow for a chapter to come up with nothing as a result. A response of it doesn't really reveal anything general or applicable to you would mean we just don't have anything from that chapter. The idea is not to generate a response for every chapter, but instead to get 5 list of interesting and enlightening insights.

The json format is by verse. The script would need to combine texts into chapters before prompting (could just have the text in the prompt for the whole chapter  plus a good prompt that allows for the result to be empty so we don't just make up a result for each chapter and only surface real matches)

My idea is to go chapter by chapter and prompt ask each of those 5 questions (one prompt each). And then make lists with references to the BoM where that item was found.

We do not want

For example in the clarifies.csv we might have:

2 Nephi 11, Clarifies the manner of baptism.

Book as PDF: Might be other more accessible txt versions.

https://assets.churchofjesuschrist.org/2d5e0fa7545611ec81e4eeeeac1e6f4d7d08ab17.pdf
