import pyttsx3
from pathlib import Path

# Speaker notes (the same as before)
speaker_notes = """
Slide 1 — Title:
Hello everyone, I’m excited to present our project: AI-Powered Kids’ Book Creator.
We take timeless works of art and transform them into personalized children’s books that teach family values, using GPT-5 as the creative engine.

Slide 2 — The Problem:
The problem we’re addressing is simple: parents want to share values with their children through stories, but personalized, high-quality children’s books are expensive and hard to find.
And when AI is used, the main issue is inconsistency — characters and illustrations change from page to page.

Slide 3 — The Idea:
Our idea is to let parents choose a masterpiece painting, enter their child’s name, age, and a family value — like sharing or kindness.
The agent then generates a full book, with consistent hero, illustrations, and narrative, all delivered as a ready-to-print PDF.

Slide 4 — The Workflow:
Here’s our workflow. We start with user input, extract artistic cues from the painting, then GPT-5 generates the story step by step.
Meanwhile, image models create consistent illustrations. Finally, everything is assembled into a polished book layout, and delivered as a PDF — with the CLI keeping the user informed at every stage.

Slide 5 — Why GPT-5?
GPT-5 is the creative brain here. It’s not just generating text — it’s reasoning across multiple steps.
It creates outlines, adapts vocabulary to the child’s age, keeps characters consistent, and integrates with image models.
This level of structured reasoning is what makes GPT-5 a true step up from GPT-4.

Slide 6 — GPT-4 vs GPT-5 Code:
Here’s the difference. GPT-4 can generate a story in one pass, but often struggles with consistency, age adaptation, and structure.
With GPT-5, we break it into steps: first an outline, then expanding each chapter while remembering the hero’s persona.
The result: structured, consistent, age-appropriate storytelling.

Slide 7 — Example Output Comparison:
Here’s a side-by-side example. GPT-4 might call the hero ‘Liam’ in one chapter and ‘Leo’ in the next.
GPT-5 not only keeps the hero consistent, but also adjusts the vocabulary — simple words for a 5-year-old, richer expressions for a 9-year-old.
This difference is immediately clear when you read the stories.

Slide 8 — Tech Stack:
Our tech stack is pragmatic. GPT-5 handles story logic and style, the image model ensures consistent visuals, and everything is orchestrated through a Python CLI with robust logging.
ReportLab builds the final book PDF, and we use memory structures to keep characters and artistic features consistent across the workflow.

Slide 9 — Impact & Future:
The impact is clear: families can create unique, meaningful books at scale.
Beyond entertainment, this reinforces values and introduces children to art.
We see huge potential — from multilingual editions to an API service and even a mobile app.

Slide 10 — Closing:
To wrap up: we believe AI can help families connect through storytelling. By combining the power of GPT-5 with artistic inspiration, we’re building books that are truly personal and meaningful.
Thank you, and I look forward to your questions.
"""

# Initialize TTS engine
engine = pyttsx3.init()

# Set voice properties (you can change rate/volume/voice)
engine.setProperty("rate", 160)   # Speed
engine.setProperty("volume", 0.9) # Volume

# Save to file
output_path = Path("/mnt/data/speaker_notes.wav")
engine.save_to_file(speaker_notes, str(output_path))

engine.runAndWait()

output_path
