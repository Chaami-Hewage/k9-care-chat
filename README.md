# Pup Pal Chat

"Build a playful yet professional Dog Healthcare Chatbot interface called 'Know Your Dog'. Features: - A dropdown/input for selecting Dog Breed, Age, and Weight. - A modern chat interface with message history and loading spinners. - Quick symptom buttons (e.g., 'Vomiting', 'Lethargy', 'Skin Rash').

When a message is sent, make a POST request to http://localhost:8000/api/ask-vet with:

JSON

{
  "message": "User's query",
  "breed": "Selected breed"
}


Render the response cleanly with markdown support (bullet points, bold text)." add nice pictures of different dogs huggung including srilankan hound and other breeds

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/591dd857-7e0a-4aff-9ed4-166d47ff942f).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
